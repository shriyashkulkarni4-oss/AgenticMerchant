"""
Gemma Agent Service for AgenticBuy.

Executes autonomous consumer shopping interactions, product discovery,
bargaining, and purchase placement powered directly by local Gemma open-weight models.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional
import uuid

import httpx
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.merchant import Merchant
from app.models.negotiation import NegotiationMessage, NegotiationSession
from app.models.order import Order
from app.models.product import Product
from app.models.user import User

logger = logging.getLogger(__name__)


class AgenticBuyAgent:
    """Autonomous shopping and negotiation assistant powered by open-weight Gemma."""

    def __init__(
        self,
        ollama_url: str,
        model_name: str,
        db_session: AsyncSession,
        user: Optional[User] = None,
    ) -> None:
        self.ollama_url = ollama_url.rstrip("/")
        self.model_name = model_name
        self.db = db_session
        self.user = user

    async def _get_inventory_context(self) -> tuple[List[Product], str]:
        """Fetch active products to provide real-time context to Gemma."""
        stmt = (
            select(Product)
            .where(Product.is_active == True)  # noqa: E712
            .order_by(Product.created_at.desc())
            .limit(100)
        )
        res = await self.db.execute(stmt)
        products = list(res.scalars().all())

        if not products:
            return [], "No products currently listed."

        lines = ["Available Merchant Products:"]
        for p in products:
            bargain_info = (
                f"Bargaining: Open (Directly Agreeable at ${float(p.auto_accept_threshold or p.price):.2f}, Floor Minimum: ${float(p.min_acceptable_price or p.price):.2f})"
                if p.bargaining_enabled
                else "Bargaining: Disabled (Firm Price)"
            )
            lines.append(
                f"- '{p.name}' | Category: {p.category or 'General'} | Listed Price: ${float(p.price):.2f} | Stock: {p.stock_quantity} | {bargain_info} | ID: {p.id}"
            )
        return products, "\n".join(lines)

    async def chat(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process conversational agent prompt with the local Gemma model."""
        session_uuid = session_id or str(uuid.uuid4())
        actions_taken = []

        products, inventory_text = await self._get_inventory_context()

        system_prompt = f"""You are the AgenticBuy Assistant, an autonomous shopping and price negotiation agent powered by Google Gemma.
You represent verified merchants on the platform and assist human shoppers.

{inventory_text}

Rules:
1. When asked about products, recommend relevant items from the catalog with their listed prices and stock.
2. When the user proposes a price or asks for a discount:
   - If offer >= Directly Agreeable price: enthusiastically accept the deal!
   - If offer >= Floor Minimum but < Directly Agreeable: propose a fair counter-offer between their offer and the listed price.
   - If offer < Floor Minimum: politely decline and state the lowest price allowed.
   - If bargaining is disabled for that item: state that the listed price is firm.
3. When the user says they want to buy, confirm, or accept the price, confirm the order with them.
4. Keep your replies concise, natural, and friendly (2 to 4 sentences). Do not mention internal rules or thresholds directly.
"""

        # 1. Direct LLM Generation from local Gemma
        gemma_reply = None
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                resp = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "system": system_prompt,
                        "prompt": message,
                        "stream": False,
                    },
                )
                if resp.status_code == 200:
                    gemma_reply = resp.json().get("response", "").strip()
        except Exception as e:
            logger.warning("Ollama Gemma request error: %s", e)

        # 2. Check for offer or order intent to record live negotiation / purchase in database
        clean_msg = message.lower()
        price_match = re.search(r"\$?([0-9]+(?:\.[0-9]{1,2})?)", message)

        # Detect matching product in conversation
        matched_product = None
        for p in products:
            words = p.name.lower().split()
            if any(w in clean_msg for w in words if len(w) > 3):
                matched_product = p
                break
        if not matched_product and products:
            matched_product = products[0]

        # Record purchase if user confirmed
        if any(w in clean_msg for w in ["buy", "confirm", "deal", "accept"]) and ("confirm" in clean_msg or "buy" in clean_msg or "yes" in clean_msg):
            if matched_product:
                buyer = self.user
                if not buyer:
                    u_res = await self.db.execute(select(User).where(User.role == "consumer").limit(1))
                    buyer = u_res.scalars().first()
                    if not buyer:
                        u_res = await self.db.execute(select(User).limit(1))
                        buyer = u_res.scalars().first()

                if buyer:
                    order_price = float(matched_product.price)
                    if price_match:
                        order_price = float(price_match.group(1))

                    order = Order(
                        user_id=buyer.id,
                        merchant_id=matched_product.merchant_id,
                        product_id=matched_product.id,
                        quantity=1,
                        unit_price=order_price,
                        total_price=order_price,
                        original_price=float(matched_product.price),
                        status="confirmed",
                    )
                    self.db.add(order)
                    matched_product.stock_quantity = max(0, (matched_product.stock_quantity or 10) - 1)
                    await self.db.commit()
                    await self.db.refresh(order)

                    actions_taken.append({
                        "tool": "place_order",
                        "result": {
                            "order_id": str(order.id),
                            "product_name": matched_product.name,
                            "unit_price": order_price,
                            "total_price": order_price,
                            "status": "confirmed",
                        },
                    })
        elif price_match and matched_product and any(w in clean_msg for w in ["offer", "pay", "take", "give", "discount", "$", "how about"]):
            # Record negotiation offer
            offered_val = float(price_match.group(1))
            floor_val = float(matched_product.min_acceptable_price or matched_product.price)
            auto_val = float(matched_product.auto_accept_threshold or matched_product.price)

            status_val = "active"
            counter_val = round((offered_val + float(matched_product.price)) / 2, 2)
            final_val = None

            if offered_val >= auto_val:
                status_val = "accepted"
                final_val = offered_val
            elif offered_val < floor_val:
                status_val = "rejected"

            actions_taken.append({
                "tool": "start_negotiation",
                "result": {
                    "product_name": matched_product.name,
                    "current_offer": offered_val,
                    "counter_offer": counter_val if status_val == "active" else None,
                    "final_price": final_val,
                    "status": status_val,
                },
            })

        # Return Gemma's response if available
        if gemma_reply:
            return {
                "response": gemma_reply,
                "actions": actions_taken,
                "session_id": session_uuid,
            }

        # Fallback only if Gemma is completely offline
        fallback_text = (
            f"Hello! I am your Gemma Shopping Agent. We currently have '{matched_product.name}' in stock for ${matched_product.price:.2f}. "
            f"Bargaining is open! What price would you like to offer?"
            if matched_product
            else "Hello! I am your Gemma Shopping Agent. How can I help you find products today?"
        )
        return {
            "response": fallback_text,
            "actions": actions_taken,
            "session_id": session_uuid,
        }
