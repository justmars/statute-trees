from typing import Iterator


def fetch_values_from_key(data: dict, key: str) -> Iterator:
    """Stack based function applicable to nested dictionaries to yield values
    that match the key; e.g. `fetch_values_from_key(data, "history")` will go
    through the nested dictionary searching for the "history" key.

    Args:
        data (dict): The nested dictionary
        key (str): The key of the nested dictionary

    Yields:
        Iterator: [description]
    """
    stack = [data]

    while stack:
        # remove from stack
        evaluate_data = stack.pop()

        # yield if the key value pair is found
        if (
            not isinstance(evaluate_data, str)
            and key in evaluate_data
            and evaluate_data[key] is not None
        ):
            yield evaluate_data[key]

        # continue if the data being evaluated is a string;
        # if not, determine whether a list or a dict
        # if a dict, add the dictionary to the stacked list to evaluate later
        # if a list, extend the stacked list
        if not isinstance(evaluate_data, str):
            for v in evaluate_data.values():
                if isinstance(v, dict):
                    stack.append(v)
                if isinstance(v, list):
                    stack += v
