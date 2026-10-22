"""
Graph API Router for AgenticBuy.

Endpoints to query the structural product knowledge graph generated
by Graphify and synced to Neo4j.
"""

from typing import Any, Dict, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import get_current_user, get_optional_current_user
from app.database import get_db, get_neo4j_driver
from app.models.merchant import Merchant
from app.models.product import Product
from app.models.user import User
from app.services.graph_service import (
    get_merchant_graph,
    get_similar_products,
    query_products,
)

router = APIRouter(prefix="/api/v1/graph", tags=["knowledge-graph"])


class GraphQueryRequest(BaseModel):
    """Schema for querying the knowledge graph."""

    query: str
    merchant_id: Optional[uuid.UUID] = None


@router.get(
    "/mine",
    summary="Get knowledge graph for currently logged-in merchant",
)
async def get_my_knowledge_graph(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve full knowledge graph for the authenticated merchant."""
    target_merchant_id = None
    store_name = "Merchant Store"

    if current_user:
        stmt = select(Merchant).where(Merchant.user_id == current_user.id)
        res = await db.execute(stmt)
        merch = res.scalars().first()
        if merch:
            target_merchant_id = merch.id
            store_name = merch.business_name

    if not target_merchant_id:
        # Default to first merchant
        stmt = select(Merchant).limit(1)
        res = await db.execute(stmt)
        merch = res.scalars().first()
        if merch:
            target_merchant_id = merch.id
            store_name = merch.business_name

    if not target_merchant_id:
        return {"nodes": [], "edges": [], "store_name": store_name}

    return await get_merchant_knowledge_graph(merchant_id=target_merchant_id, db=db)


@router.get(
    "/merchant/{merchant_id}",
    summary="Get full graph structure for a merchant",
)
async def get_merchant_knowledge_graph(
    merchant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve all nodes and edges (products, categories, relationships) for visualization."""
    # 1. Try Neo4j
    try:
        driver = get_neo4j_driver()
        if driver:
            graph_res = await get_merchant_graph(
                neo4j_driver=driver,
                merchant_id=str(merchant_id),
            )
            if graph_res and len(graph_res.get("nodes", [])) > 0:
                return graph_res
    except Exception:
        pass

    # 2. Relational fallback from live PostgreSQL products
    stmt = select(Product).where(Product.merchant_id == merchant_id, Product.is_active == True)  # noqa: E712
    res = await db.execute(stmt)
    products = list(res.scalars().all())

    # Get merchant info
    m_stmt = select(Merchant).where(Merchant.id == merchant_id)
    m_res = await db.execute(m_stmt)
    merch = m_res.scalars().first()
    store_title = merch.business_name if merch else "Store"

    nodes = [
        {
            "id": f"store_{merchant_id}",
            "label": "Merchant",
            "properties": {"name": store_title, "id": str(merchant_id)},
        }
    ]
    edges = []
    categories = set()

    for p in products:
        nodes.append({
            "id": str(p.id),
            "label": "Product",
            "properties": {
                "name": p.name,
                "price": float(p.price),
                "category": p.category,
                "auto_accept_threshold": float(p.auto_accept_threshold or p.price),
                "min_acceptable_price": float(p.min_acceptable_price or p.price),
                "stock_quantity": p.stock_quantity,
                "bargaining_enabled": p.bargaining_enabled,
            },
        })
        cat_name = p.category or "General"
        categories.add(cat_name)
        cat_id = f"cat_{cat_name.lower().replace(' ', '_')}"
        edges.append({
            "source": str(p.id),
            "target": cat_id,
            "type": "BELONGS_TO",
        })

    for cat in categories:
        cat_id = f"cat_{cat_name.lower().replace(' ', '_')}"
        nodes.append({
            "id": cat_id,
            "label": "Category",
            "properties": {"name": cat},
        })
        edges.append({
            "source": f"store_{merchant_id}",
            "target": cat_id,
            "type": "OFFERS_CATEGORY",
        })

    return {"nodes": nodes, "edges": edges, "store_name": store_title, "source": "postgres_live"}


@router.post(
    "/query",
    summary="Query the Neo4j knowledge graph",
)
async def query_knowledge_graph(
    payload: GraphQueryRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Search products and related categories across the Neo4j knowledge graph."""
    try:
        driver = get_neo4j_driver()
        results = await query_products(
            neo4j_driver=driver,
            query=payload.query,
            merchant_id=str(payload.merchant_id) if payload.merchant_id else None,
        )
        return {"query": payload.query, "matches": results, "count": len(results)}
    except Exception as e:
        # Fallback to relational DB if Neo4j is not connected
        search_pattern = f"%{payload.query}%"
        stmt = select(Product).where(
            Product.name.ilike(search_pattern) | Product.description.ilike(search_pattern)
        )
        if payload.merchant_id:
            stmt = stmt.where(Product.merchant_id == payload.merchant_id)
        res = await db.execute(stmt)
        products = res.scalars().all()
        return {
            "query": payload.query,
            "matches": [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "price": float(p.price),
                    "category": p.category,
                    "description": p.description,
                }
                for p in products
            ],
            "count": len(products),
            "fallback": True,
            "note": f"Graph database query fallback used: {e}",
        }





@router.get(
    "/similar/{product_id}",
    summary="Find similar products via graph traversal",
)
async def get_similar_graph_products(
    product_id: uuid.UUID,
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Traverse graph relationships to find similar or competing products."""
    try:
        driver = get_neo4j_driver()
        return await get_similar_products(
            neo4j_driver=driver,
            product_id=str(product_id),
            limit=limit,
        )
    except Exception:
        # Fallback: products in same category
        p_stmt = select(Product).where(Product.id == product_id)
        p_res = await db.execute(p_stmt)
        orig = p_res.scalars().first()
        if not orig or not orig.category:
            return []

        sim_stmt = (
            select(Product)
            .where(Product.category == orig.category, Product.id != product_id)
            .limit(limit)
        )
        sim_res = await db.execute(sim_stmt)
        return [
            {
                "id": str(p.id),
                "name": p.name,
                "price": float(p.price),
                "category": p.category,
                "image_url": p.image_url,
            }
            for p in sim_res.scalars().all()
        ]
