# ndimatlabport: Ported MATLAB Unit Tests

This package contains Python ports of specific unit tests from the VH-Lab/NDI-matlab repository. The purpose is to run identical tests between the MATLAB and Python versions to identify points of divergence and ensure parity.

## Structure

The Python packages within this directory should mimic the MATLAB namespaces. For example, a test located at `+ndi/+unittest/+dataset/testDatasetBuild.m` in MATLAB should be ported to `tests/nditests/unittest/ndimatlabport/dataset/test_dataset_build.py`.

## Comparison Table

The following table tracks the status of MATLAB unit tests being ported to Python.

| MatlabTests | Converted_Yet |
| :--- | :--- |
| `ndi.unittest.dataset.buildDataset` | Yes |
| `ndi.unittest.dataset.OldDatasetTest` | Yes |
| `ndi.unittest.dataset.testDatasetBuild` | Yes |
| `ndi.unittest.dataset.testDatasetConstructor` | Yes |
| `ndi.unittest.dataset.testDeleteIngestedSession` | Yes |
| `ndi.unittest.dataset.testSessionList` | Yes |
| `ndi.unittest.dataset.testUnlinkSession` | Yes |
| `ndi.unittest.session.buildSession` | Yes |
| `ndi.unittest.session.buildSessionNDRAxon` | Yes |
| `ndi.unittest.session.buildSessionNDRIntan` | Yes |
| `ndi.unittest.session.TestDeleteSession` | Yes |
| `ndi.unittest.session.testIsIngestedInDataset` | Yes |
| `ndi.unittest.session.testSessionBuild` | Yes |
