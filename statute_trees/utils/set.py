def set_node_ids(
    nodes: list[dict],
    parent_id: str = "1.",
    child_key: str = "units",
):
    """Recursive function updates nodes in place since list/dicts are mutable.
    Assumes that the nodes reprsent a deeply nested json, e.g.

    For each node in the `nodes` list, it will add a new `id` key and will
    increment according to its place in the tree structure.

    If node id "1.1." has child nodes, the first child node will be "1.1.1.".

    A trailing period is necessary for materialized paths. Otherwise a string
    with  `value like '%'` where the value is 1.1 will also match 1.11

    The root of the tree will always be "1.", unless the `parent_id` is
    set to a different string.

    The child key of the tree will always be "units", unless the `child_key`
    is set to a different string.

    Args:
        nodes (list[dict]): The list of dicts that
        parent_id (str, optional): The root node id. Defaults to "1.".
        child_key (str, optional): The node which represents a list of children nodes.
            Defaults to "units".
    """
    if isinstance(nodes, list):
        for counter, node in enumerate(nodes, start=1):
            node["id"] = f"{parent_id}{str(counter)}."
            if node.get(child_key, None):
                set_node_ids(node[child_key], node["id"], child_key)
