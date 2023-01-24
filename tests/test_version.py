import toml

import statute_trees


def test_version():
    assert (
        toml.load("pyproject.toml")["tool"]["poetry"]["version"]
        == statute_trees.__version__
    )
