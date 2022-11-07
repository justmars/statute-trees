# Statute Trees

## Rules

Rules are tree-based. This library facilitates the creation of codifications, statutes, and documents in the form of trees.

```python
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

```python
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

## HTML

Follow prerequisite [tailwind](/docs/tailwind.md) process to generate the css. Create html based on the following function:

```python
>>> from tree_markup import create_tree
>>> from statute_trees import set_node_ids
>>> set_node_ids(code['units']) # assumings the nodes do not yet have an `id` value, this will populate the same.
>>> html_tree = create_tree("codification", "test", code['units'])
>>> type(html_tree)
<str>
```

This will produce the following html string that can be inserted as a variable `html_tree` which if marked safe will render likeso:

```html
    <article class="tree">
      <ul class="pl-0 sm:pl-3 mt-4 mx-0 mb-0">
        <li class="pl-0 sm:pl-3 mt-4 mx-0 mb-0">
          <details>
            <summary>
              <a
                class="text-blue-800 hover:text-rose-600"
                href="/codification/test/unit/1.1."
                title="Focus on Preliminary Title"
                data-tooltip="Focus on Preliminary Title"
                ><em>Preliminary Title.</em></a
              >
            </summary>
            <ul class="pl-0 sm:pl-3 mt-4 mx-0 mb-0">
              <li class="pl-0 sm:pl-3 mt-4 mx-0 mb-0">
                <details>
                  <summary>
                    <a
                      class="text-blue-800 hover:text-rose-600"
                      href="/codification/test/unit/1.1.1."
                      title="Focus on Chapter 1. Effect and Application of Laws"
                      data-tooltip="Focus on Chapter 1. Effect and Application of Laws"
                      >Chapter 1. <em>Effect and Application of Laws</em></a
                    >
                  </summary>
                  <ul class="pl-0 sm:pl-3 mt-4 mx-0 mb-0">
                    <li class="pl-0 sm:pl-3 mt-4 mx-0 mb-0">
                      <p>
                        <a
                          class="text-blue-800 hover:text-rose-600"
                          href="/codification/test/unit/1.1.1.1."
                          title="Focus on Article 1"
                          data-tooltip="Focus on Article 1"
                          >Article 1.</a
                        >
                        This Act shall be known as the "Civil Code of the
                        Philippines." (n)
                      </p>
                    </li>
                    <li class="pl-0 sm:pl-3 mt-4 mx-0 mb-0">
                      <p>
                        <a
                          class="text-blue-800 hover:text-rose-600"
                          href="/codification/test/unit/1.1.1.2."
                          title="Focus on Article 2"
                          data-tooltip="Focus on Article 2"
                          >Article 2.</a
                        >
                        Laws shall take effect after fifteen days following the
                        completion of their publication either in the Official
                        Gazette or in a newspaper of general circulation in the
                        Philippines, unless it is otherwise provided. (1a)
                      </p>
                    </li>
    <!-- more nodes not known -->
```
