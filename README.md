# Neuroscience Data Interface (NDI) - Python
A sister project to [NDI Matlab](https://github.com/VH-Lab/NDI-matlab).
---
The NDI library is an Object Relational Mapping API for managing session data. It brings together data acquisition (daq) systems, a file navigator, the Data Interface Database (DID), and data analysis libraries for use by user-built apps.

## Usage

Basic usage is recommended via [Jupyter Notebook](https://jupyter.org/). Any Jupyter install should work but [Anaconda](https://www.anaconda.com/distribution/) (Python 3) is an easy way to get started with Jupyter.

## Package manager
Ndi-python uses pipenv is used for package management, it can be installed with pip.

## Jupyter Notebook Quickstart

```shell
# Install dependencies (use the --dev flag if you plan to run the linter, test suite, or docs)
$ pipenv install
# Activate virtualenv
$ pipenv shell
# Verify virtual environment (OPTIONAL)
(ndi-python) $ which jupyter
# Start Jupyter Notebook
(ndi-python) $ jupyter notebook
```

## Developer Notes

The Python package makes use of [native namespace packages available in Python 3.3 and later](https://packaging.python.org/guides/packaging-namespace-packages/#native-namespace-packages).

NDI_Object subclasses are PascalCase, their collection/table names are snake_case + 's', and their reference keys are snake_case + '_id'.

## Documentation

This library is documented in the set of Jupyter Notebooks at ./examples.
Further documentation on the associated DID library can be found in that repo at did-python/examples.

## Testing

From pipenv shell, run `python -m pytest`.