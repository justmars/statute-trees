# Statute Trees Docs

## Rules

Rules are tree-based. This library facilitates the creation of codifications, statutes, and documents in the form of trees.

```py
trees=CodeUnit(
    item='Modern Child and Youth Welfare Code',
    caption=None,
    content=None,
    id='1.',
    history=None,
    units=[
        CodeUnit(
            item='Title I',
            caption='General Principles',
            content=None,
            id='1.1.',
            history=None,
            units=[
                CodeUnit(
                    item='Article 1',
                    caption='Declaration of Policy.',
                    content=None,
                    id='1.1.1.',
                    history=None,
                    units=[
                        CodeUnit(
                            item='Paragraph 1',
                            caption=None,
                            content='The Child is one of the most important assets of the nation. Every effort should be exerted to promote his welfare and enhance his opportunities for a useful and happy life.',
                            id='1.1.1.1.',
                            history=None,
                            units=[]
                        ),
                        CodeUnit(
                            item='Paragraph 2',
                            caption=None,
                            content='The child is not a mere creature of the State. Hence, his individual traits and aptitudes should be cultivated to the utmost insofar as they do not conflict with the general welfare.',
                            id='1.1.1.2.',
                            history=None,
                            units=[]
                        ),
                    ]
                )
            ]
        )
    ]
... # sample excludes the rest of the tree
)
```

## Categories

We'll concern ourselves with 3 distinct categorizations of trees as they apply to Philippine law:

1. Codification Trees
2. Statute Trees
3. Document Trees

Each of these trees rely on a similar `Node` structure consisting of the following fields:

```python
class Node:
    item: str
    caption: str
    content: str
```

If we imagine this to be the root of the tree, it can branch out using a `units` key like so:

```py
>>> data = [
        {
            "item": "Preliminary Title",
            "units": [
                {
                    "item": "Chapter 1",
                    "caption": "Effect and Application of Laws",
                    "units": [
                        {
                            "item": "Article 1",
                            "content": 'This Act shall be known as the "Civil Code of the Philippines." (n)\n',
                        },
                        {
                            "item": "Article 2",
                            "content": "Laws shall take effect after fifteen days following the completion of their publication either in the Official Gazette or in a newspaper of general circulation in the Philippines, unless it is otherwise provided. (1a)\n",
                        },
                    ],
                }
            ],
        }
    ]
```

Since each branch needs to be validated, i.e. have the correct type of information per field. We utilize Pydantic for each of the main categories.

## Prerequisite

To add a new statute-pattern that will get recognized, update the `statute-patterns` library.

This enables the `Rule` mechanism, a pre-requisite to utilizing the `StatuteBase` pydantic model.

Trees are a crucial cog in the `corpus-x` library.
