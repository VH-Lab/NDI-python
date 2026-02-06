# NDI-python

A Python port of VH-Lab/NDI-matlab.

## Installation

To install the package, run the following command in the root directory. **Note the dot `.` at the end**, which tells pip to install from the current directory. This will automatically install all required dependencies (including `did`, `ndi-compress`, etc.):

```bash
pip install .
```

If you are installing for development (editable mode), use the `-e` flag (again, **note the dot `.` at the end**):

```bash
pip install -e .
```

## Usage

```python
import ndi
```

## Development

### Environment Setup

To set up the development environment, first create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Dependency Installation

Install the package in editable mode, which will also install all dependencies:

```bash
pip install -e .
```

### Running Tests

To run the tests, use the following command:

```bash
python -m unittest discover tests
```

### Building Documentation

To build the documentation, use the following command:

```bash
mkdocs build
```
