def get_node_id(
    nodes: list[dict],
    query_id: str,
    child_key: str = "units",
) -> dict | None:
    """Return the first node matching the `query_id`, if it exists.

    Args:
        nodes (list[dict]): The deeply nested json list
        query_id (str): The id previously set by `set_tree_ids()`

    Returns:
        dict | None: The first node matching the query_id or None
    """
    for node in nodes:
        if node["id"] == query_id:
            return node
        if units := node.get(child_key, None):
            if match := get_node_id(units, query_id, child_key):
                return match
    return None
