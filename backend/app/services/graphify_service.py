"""
Graphify integration service for AgenticBuy.

Handles running the Graphify CLI on crawled website data, parsing
the output, and syncing the resulting knowledge graph into Neo4j.
"""

import asyncio
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


async def run_graphify_on_crawl_data(
    merchant_id: str,
    crawl_data: dict,
    output_dir: str,
) -> str:
    """Run the Graphify CLI on crawled website data.

    Saves crawled page content as individual files in a temporary directory,
    runs the Graphify CLI to generate a knowledge graph, and returns the
    path to the output directory.

    Args:
        merchant_id: The UUID of the merchant whose data is being processed.
        crawl_data: The crawl output dict containing pages, products, etc.
        output_dir: The directory where Graphify output should be stored.

    Returns:
        The path to the directory containing Graphify output files.

    Raises:
        RuntimeError: If the Graphify CLI fails or is not available.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create a temporary directory for input files
    with tempfile.TemporaryDirectory(prefix=f"graphify_{merchant_id}_") as tmp_dir:
        input_dir = Path(tmp_dir) / "input"
        input_dir.mkdir(parents=True, exist_ok=True)

        # Save crawled pages as individual files
        pages = crawl_data.get("pages", [])
        for i, page in enumerate(pages):
            page_content = {
                "url": page.get("url", ""),
                "title": page.get("title", ""),
                "description": page.get("description", ""),
                "headings": page.get("headings", []),
            }
            page_file = input_dir / f"page_{i:04d}.json"
            page_file.write_text(json.dumps(page_content, indent=2))

        # Save extracted products
        products = crawl_data.get("products_found", [])
        if products:
            products_file = input_dir / "products.json"
            products_file.write_text(json.dumps(products, indent=2))

        # Save categories
        categories = crawl_data.get("categories_found", [])
        if categories:
            categories_file = input_dir / "categories.json"
            categories_file.write_text(json.dumps(categories, indent=2))

        # Run graphify CLI
        try:
            process = await asyncio.create_subprocess_exec(
                "graphify",
                "build",
                "--input", str(input_dir),
                "--output", output_dir,
                "--format", "json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(
                    "Graphify failed for merchant %s: %s",
                    merchant_id,
                    error_msg,
                )
                raise RuntimeError(
                    f"Graphify CLI failed with exit code {process.returncode}: "
                    f"{error_msg}"
                )

            logger.info(
                "Graphify completed for merchant %s. Output: %s",
                merchant_id,
                stdout.decode() if stdout else "",
            )

        except FileNotFoundError:
            logger.warning(
                "Graphify CLI not found. Creating fallback graph for merchant %s",
                merchant_id,
            )
            # Create a fallback graph from the crawl data directly
            fallback_graph = _create_fallback_graph(crawl_data, merchant_id)
            graph_file = Path(output_dir) / "graph.json"
            graph_file.write_text(json.dumps(fallback_graph, indent=2))

    return output_dir


def _create_fallback_graph(crawl_data: dict, merchant_id: str) -> dict:
    """Create a basic graph structure from crawl data when Graphify is unavailable.

    Args:
        crawl_data: The crawl output dict.
        merchant_id: The merchant's UUID.

    Returns:
        A dict representing the graph with nodes and edges.
    """
    nodes: list[dict] = []
    edges: list[dict] = []
    category_ids: dict[str, str] = {}

    # Create product nodes
    products = crawl_data.get("products_found", [])
    for i, product in enumerate(products):
        product_id = f"product_{merchant_id}_{i}"
        nodes.append({
            "id": product_id,
            "type": "Product",
            "properties": {
                "name": product.get("name", ""),
                "price": product.get("price"),
                "description": product.get("description", ""),
                "image_url": product.get("image_url"),
                "source_url": product.get("source_url", ""),
                "merchant_id": merchant_id,
            },
        })

    # Create category nodes
    categories = crawl_data.get("categories_found", [])
    for cat_name in categories:
        cat_id = f"category_{cat_name.lower().replace(' ', '_')}"
        category_ids[cat_name] = cat_id
        nodes.append({
            "id": cat_id,
            "type": "Category",
            "properties": {
                "name": cat_name,
                "merchant_id": merchant_id,
            },
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "merchant_id": merchant_id,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
        },
    }


def load_graphify_graph(graph_path: str) -> dict:
    """Load and parse a Graphify graph.json output file.

    Args:
        graph_path: Path to the graph.json file.

    Returns:
        A dict containing the parsed graph data with nodes and edges.

    Raises:
        FileNotFoundError: If the graph file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    path = Path(graph_path)

    if path.is_dir():
        path = path / "graph.json"

    if not path.exists():
        raise FileNotFoundError(f"Graph file not found at {path}")

    with open(path, "r", encoding="utf-8") as f:
        graph_data = json.load(f)

    logger.info(
        "Loaded graph from %s: %d nodes, %d edges",
        path,
        len(graph_data.get("nodes", [])),
        len(graph_data.get("edges", [])),
    )

    return graph_data


async def sync_graph_to_neo4j(
    graph_data: dict,
    merchant_id: str,
    neo4j_driver: Any,
) -> None:
    """Sync Graphify graph output into Neo4j.

    Takes the parsed Graphify output and creates corresponding
    Neo4j nodes and relationships, tagged with the merchant_id.

    Args:
        graph_data: The parsed graph dict with nodes and edges.
        merchant_id: The UUID of the merchant who owns this data.
        neo4j_driver: The Neo4j async driver instance.
    """
    if not neo4j_driver:
        logger.warning("Neo4j driver is not available. Skipping graph sync to Neo4j.")
        return

    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    try:
        async with neo4j_driver.session() as session:
            # Clear existing data for this merchant to avoid duplicates
            await session.run(
                """
                MATCH (n {merchant_id: $merchant_id})
                DETACH DELETE n
                """,
                {"merchant_id": merchant_id},
            )
            logger.info("Cleared existing Neo4j data for merchant %s", merchant_id)

            # Create nodes
            for node in nodes:
                node_type = node.get("type", "Entity")
                properties = node.get("properties", {})
                properties["id"] = node.get("id", "")
                properties["merchant_id"] = merchant_id

                # Dynamically build SET clause from properties
                set_parts = []
                params: dict[str, Any] = {"node_id": properties["id"]}
                for key, value in properties.items():
                    param_name = f"prop_{key}"
                    set_parts.append(f"n.{key} = ${param_name}")
                    params[param_name] = value

                set_clause = ", ".join(set_parts) if set_parts else ""

                cypher = f"""
                    MERGE (n:{node_type} {{id: $node_id}})
                    {f'SET {set_clause}' if set_clause else ''}
                """

                await session.run(cypher, params)

            logger.info(
                "Created %d nodes in Neo4j for merchant %s",
                len(nodes),
                merchant_id,
            )

            # Create edges
            for edge in edges:
                source_id = edge.get("source", "")
                target_id = edge.get("target", "")
                rel_type = edge.get("type", "RELATED_TO")

                # Sanitize relationship type for Cypher
                rel_type = rel_type.upper().replace(" ", "_").replace("-", "_")

                cypher = f"""
                    MATCH (source {{id: $source_id}})
                    MATCH (target {{id: $target_id}})
                    MERGE (source)-[r:{rel_type}]->(target)
                """

                await session.run(
                    cypher,
                    {"source_id": source_id, "target_id": target_id},
                )

            logger.info(
                "Created %d edges in Neo4j for merchant %s",
                len(edges),
                merchant_id,
            )

            logger.info(
                "Graph sync complete for merchant %s: %d nodes, %d edges",
                merchant_id,
                len(nodes),
                len(edges),
            )
    except Exception as e:
        logger.warning("Failed to sync graph into Neo4j: %s", e)
