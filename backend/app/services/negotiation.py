"""
Negotiation engine for AgenticBuy.

Provides counter-offer calculation, message generation, and offer evaluation
logic for the automated price negotiation system.
"""

import random


def calculate_counter_offer(
    current_offer: float,
    list_price: float,
    min_price: float,
    round_num: int,
    max_rounds: int,
) -> float:
    """Calculate a counter-offer based on the negotiation strategy.

    Strategy: Start closer to list price, gradually move toward min_price
    as rounds progress.

    Args:
        current_offer: The buyer's current offer amount.
        list_price: The original listed price of the product.
        min_price: The minimum acceptable price for the merchant.
        round_num: The current round number (0-indexed).
        max_rounds: The maximum number of negotiation rounds allowed.

    Returns:
        The calculated counter-offer amount, never below min_price.
    """
    if max_rounds <= 0:
        return min_price

    progress = round_num / max_rounds
    counter = min_price + (list_price - min_price) * (1 - progress) * 0.7

    # Never go below min_price
    counter = max(counter, min_price)

    # Never go above list_price
    counter = min(counter, list_price)

    # Round to 2 decimal places
    return round(counter, 2)


def generate_negotiation_message(
    action: str,
    counter_offer: float | None = None,
    product_name: str = "",
    round_num: int = 0,
) -> str:
    """Generate a human-like negotiation message for the agent.

    Args:
        action: One of "counter", "accept", "reject", "final_offer".
        counter_offer: The counter-offer amount (used for counter/final_offer).
        product_name: The name of the product being negotiated.
        round_num: The current round number for context.

    Returns:
        A human-readable negotiation message string.
    """
    product_ref = f" for {product_name}" if product_name else ""

    if action == "accept":
        accept_messages = [
            f"Great news! We've accepted your offer{product_ref}. "
            f"The deal is done at ${counter_offer:.2f}!" if counter_offer else
            f"We're happy to accept your offer{product_ref}! You've got a deal!",
            f"Your offer{product_ref} has been accepted! "
            f"Let's finalize this at ${counter_offer:.2f}." if counter_offer else
            f"Congratulations! Your offer{product_ref} has been accepted.",
            f"Deal! We're pleased to accept your price{product_ref}. "
            f"Final price: ${counter_offer:.2f}." if counter_offer else
            f"Deal! We're pleased to accept your price{product_ref}.",
        ]
        return random.choice(accept_messages)

    if action == "reject":
        reject_messages = [
            f"Unfortunately, we can't go that low{product_ref}. "
            "Your offer is below our minimum acceptable price. "
            "We hope to do business with you in the future!",
            f"We appreciate your interest{product_ref}, but that price "
            "is too far below what we can accept. "
            "Feel free to check out our other products!",
            f"Sorry, we're unable to accept that offer{product_ref}. "
            "The price is below our floor. Thank you for your time!",
        ]
        return random.choice(reject_messages)

    if action == "final_offer":
        if counter_offer is not None:
            final_messages = [
                f"This is our final offer{product_ref}: ${counter_offer:.2f}. "
                "We've reached the last round of negotiation. "
                "Take it or leave it!",
                f"Last chance! Our best and final price{product_ref} "
                f"is ${counter_offer:.2f}. This is as low as we can go.",
                f"We've reached the end of our negotiation{product_ref}. "
                f"Our final price is ${counter_offer:.2f}. "
                "We can't go any lower than this.",
            ]
            return random.choice(final_messages)
        return f"This is our final offer{product_ref}. Take it or leave it!"

    if action == "counter":
        if counter_offer is not None:
            counter_messages = [
                f"Thanks for your offer{product_ref}! "
                f"How about ${counter_offer:.2f}? "
                "We think that's a fair price for both of us.",
                f"We appreciate the offer{product_ref}, "
                f"but we'd like to suggest ${counter_offer:.2f} instead. "
                "What do you think?",
                f"Good negotiation{product_ref}! "
                f"We can meet you at ${counter_offer:.2f}. "
                "Let us know if that works for you.",
            ]
            if round_num > 2:
                counter_messages.append(
                    f"We're getting closer{product_ref}! "
                    f"Our counter is ${counter_offer:.2f}. "
                    "We're trying to find a price that works for everyone."
                )
            return random.choice(counter_messages)
        return f"Thanks for your offer{product_ref}! Let us work on a counter."

    return f"Thank you for your interest{product_ref}."


def evaluate_offer(
    offer: float,
    min_price: float,
    auto_accept: float,
    list_price: float,
) -> str:
    """Evaluate a buyer's offer and determine the appropriate action.

    Args:
        offer: The buyer's offered price.
        min_price: The minimum acceptable price.
        auto_accept: The auto-accept threshold price.
        list_price: The original listed price.

    Returns:
        One of "accept", "reject", or "counter".
    """
    if offer >= auto_accept:
        return "accept"
    if offer < min_price:
        return "reject"
    return "counter"
