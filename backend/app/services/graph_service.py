"""
Neo4j graph query service for AgenticBuy.

Provides functions to query the product knowledge graph stored in Neo4j,
including product search, similarity lookups, and full merchant graph retrieval.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def query_products(
    neo4j_driver: Any,
    query: str,
    merchant_id: str | None = None,
) -> list[dict]:
    """Search for products in Neo4j matching a text query.

    Runs a Cypher query to find Product nodes whose name or description
    contains the search text.

    Args:
        neo4j_driver: The Neo4j driver instance.
        query: The search text to match against product names/descriptions.
        merchant_id: Optional merchant ID to filter results by.

    Returns:
        A list of dicts, each representing a matching product node
        with its properties.
    """
    try:
        cypher = """
            MATCH (p:Product)
            WHERE toLower(p.name) CONTAINS toLower($query)
               OR toLower(p.description) CONTAINS toLower($query)
        """
        params: dict[str, Any] = {"query": query}

        if merchant_id:
            cypher += " AND p.merchant_id = $merchant_id"
            params["merchant_id"] = merchant_id

        cypher += """
            OPTIONAL MATCH (p)-[:BELONGS_TO]->(c:Category)
            RETURN p {.*, category: c.name} AS product
            LIMIT 50
        """

        async with neo4j_driver.session() as session:
            result = await session.run(cypher, params)
            records = await result.data()

        products = []
        for record in records:
            product_data = record.get("product", {})
            if product_data:
                products.append(product_data)

        logger.info(
            "Graph query '%s' returned %d products (merchant_id=%s)",
            query,
            len(products),
            merchant_id,
        )
        return products

    except Exception:
        logger.exception("Failed to query products in Neo4j")
        raise


async def get_similar_products(
    neo4j_driver: Any,
    product_id: str,
    limit: int = 5,
) -> list[dict]:
    """Find similar products via graph traversal.

    Uses SIMILAR_TO relationships and shared Category memberships
    to discover related products.

    Args:
        neo4j_driver: The Neo4j driver instance.
        product_id: The UUID of the product to find similarities for.
        limit: Maximum number of similar products to return.

    Returns:
        A list of dicts representing similar product nodes.
    """
    try:
        cypher = """
            MATCH (p:Product {id: $product_id})
                  -[:SIMILAR_TO|BELONGS_TO]->(related)
                  <-[:SIMILAR_TO|BELONGS_TO]-(similar:Product)
            WHERE similar.id <> $product_id
            OPTIONAL MATCH (similar)-[:BELONGS_TO]->(c:Category)
            RETURN DISTINCT similar {.*, category: c.name} AS product
            LIMIT $limit
        """

        async with neo4j_driver.session() as session:
            result = await session.run(
                cypher,
                {"product_id": product_id, "limit": limit},
            )
            records = await result.data()

        products = []
        for record in records:
            product_data = record.get("product", {})
            if product_data:
                products.append(product_data)

        logger.info(
            "Found %d similar products for product_id=%s",
            len(products),
            product_id,
        )
        return products

    except Exception:
        logger.exception(
            "Failed to find similar products for %s", product_id
        )
        raise


async def get_merchant_graph(
    neo4j_driver: Any,
    merchant_id: str,
) -> dict:
    """Get the full knowledge graph for a merchant.

    Retrieves all products, categories, and their relationships
    associated with a given merchant.

    Args:
        neo4j_driver: The Neo4j driver instance.
        merchant_id: The UUID of the merchant.

    Returns:
        A dict containing:
            - nodes: List of node dicts with id, label, and properties.
            - edges: List of edge dicts with source, target, and type.
    """
    try:
        # Fetch all product nodes for this merchant
        products_cypher = """
            MATCH (p:Product {merchant_id: $merchant_id})
            RETURN p
        """

        # Fetch all categories linked to the merchant's products
        categories_cypher = """
            MATCH (p:Product {merchant_id: $merchant_id})-[:BELONGS_TO]->(c:Category)
            RETURN DISTINCT c
        """

        # Fetch all relationships between the merchant's products and categories
        edges_cypher = """
            MATCH (p:Product {merchant_id: $merchant_id})-[r]->(target)
            RETURN p.id AS source_id, type(r) AS rel_type, 
                   COALESCE(target.id, target.name) AS target_id,
                   labels(target)[0] AS target_label
        """

        # Fetch SIMILAR_TO relationships between the merchant's products
        similar_cypher = """
            MATCH (p1:Product {merchant_id: $merchant_id})
                  -[r:SIMILAR_TO]->(p2:Product {merchant_id: $merchant_id})
            RETURN p1.id AS source_id, type(r) AS rel_type, p2.id AS target_id
        """

        params = {"merchant_id": merchant_id}
        nodes: list[dict] = []
        edges: list[dict] = []
        seen_node_ids: set[str] = set()

        async with neo4j_driver.session() as session:
            # Get product nodes
            result = await session.run(products_cypher, params)
            records = await result.data()
            for record in records:
                node = record.get("p", {})
                node_id = node.get("id", "")
                if node_id and node_id not in seen_node_ids:
                    nodes.append({
                        "id": node_id,
                        "label": "Product",
                        "properties": dict(node),
                    })
                    seen_node_ids.add(node_id)

            # Get category nodes
            result = await session.run(categories_cypher, params)
            records = await result.data()
            for record in records:
                node = record.get("c", {})
                node_id = node.get("name", node.get("id", ""))
                if node_id and node_id not in seen_node_ids:
                    nodes.append({
                        "id": node_id,
                        "label": "Category",
                        "properties": dict(node),
                    })
                    seen_node_ids.add(node_id)

            # Get product -> category/other edges
            result = await session.run(edges_cypher, params)
            records = await result.data()
            for record in records:
                edges.append({
                    "source": record["source_id"],
                    "target": record["target_id"],
                    "type": record["rel_type"],
                })

            # Get SIMILAR_TO edges between products
            result = await session.run(similar_cypher, params)
            records = await result.data()
            for record in records:
                edges.append({
                    "source": record["source_id"],
                    "target": record["target_id"],
                    "type": record["rel_type"],
                })

        logger.info(
            "Merchant graph for %s: %d nodes, %d edges",
            merchant_id,
            len(nodes),
            len(edges),
        )
        return {"nodes": nodes, "edges": edges}

    except Exception:
        logger.exception(
            "Failed to get merchant graph for %s", merchant_id
        )
        raise
