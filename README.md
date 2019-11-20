This is a Python wrapper around ndi-schema objects and reference implementations which can be used to help implement support for new probes, databases, and apps.

# Usage

Basic usage is recommended via [Jupyter Notebook](https://jupyter.org/). Any Jupyter install should work but [Anaconda](https://www.anaconda.com/distribution/) (Python 3) is an easy way to get started with Jupyter.

## Package manager
Ndi-python uses pipenv is used for package management, it can be installed with pip.

## Jupyter Notebook Quickstart

```shell
# Install dependencies
$ pipenv install
# Activate virtualenv
$ pipenv shell
# Verify virtual environment (OPTIONAL)
(ndi-python) $ which jupyter
# Start Jupyter Notebook
(ndi-python) $ jupyter notebook
```

# Developer Notes

The Python package makes use of [native namespace packages available in Python 3.3 and later](https://packaging.python.org/guides/packaging-namespace-packages/#native-namespace-packages).
