# Example Data

Some functions to help with tree like (json-ish) python structures.

## Setter of IDs

```python shell
>>> from statute_trees.utils import set_node_ids
>>> set_node_ids(data)
# all nodes in the tree will now have an `id` key, e.g.:
{
    "item": "Article 1",
    "content": 'This Act shall be known as the "Civil Code of the Philippines." (n)\n',
    "id": "1.1.1.1."
},
```

## Getter of Node by ID

```python shell
>>> from statute_trees.utils import get_node_id
>>> get_node_id("1.1.1.1.")
{
    "item": "Article 1",
    "content": 'This Act shall be known as the "Civil Code of the Philippines." (n)\n',
    "id": "1.1.1.1."
}
```

## Enables Limited Enumeration Per Layer

```python shell
>>> raw = [
    {"content": "Parent Node 1"},
    {
        "content": "Parent Node 2",
        "units": [
            {
                "content": "Hello World!",
                "units": [
                    {"content": "Deeply nested content"},
                    {"content": "Another deeply nested one"},
                ],
            },
            {"content": "Another Hello World!"},
        ],
    },
]
>>> from statute_trees.utils import Layers
>>> Layers.DEFAULT(raw) # note the addition of the `item` key to the raw itemless data
[{'content': 'Parent Node 1', 'item': 'I'},
 {'content': 'Parent Node 2',
  'units': [{'content': 'Hello World!',
    'units': [{'content': 'Deeply nested content', 'item': 1},
     {'content': 'Another deeply nested one', 'item': 2}],
    'item': 'A'},
   {'content': 'Another Hello World!', 'item': 'B'}],
  'item': 'II'}]

```

## Fetcher of Values

```python shell
>>> from statute_trees.utils import test_fetch_values_from_key
>>> list(test_fetch_values_from_key(data[0]), "item")
[
    "Preliminary Title",
    "Chapter 1",
    "Article 2",
    "Article 1",
]
```
