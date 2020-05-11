from ndi.database.file_system import BinaryCollection
from pathlib import Path
import numpy as np
import pytest

randarray = lambda: np.random.random(200000)

@pytest.fixture
def binary_collection():
    collection = BinaryCollection('./test_db', 'document')
    test_array = randarray()
    (collection.collection_dir / 'test_id.bin').write_bytes(test_array.tobytes())
    yield collection, collection.collection_dir, test_array
    rmrf(collection.collection_dir)

class TestBinaryCollection:
    def test_directory_creation(self, binary_collection):
        _, collection_dir, _ = binary_collection
        assert collection_dir.exists()
        assert collection_dir.is_dir()

    def test_write(self, binary_collection):
        collection, collection_dir, _ = binary_collection
        test_array = randarray()

        assert not (collection_dir / 'fake_id.bin').exists()
        collection.write('fake_id', test_array)

        assert (collection_dir / 'fake_id.bin').exists()
        assert (collection_dir / 'fake_id.bin').is_file()

        file_content = np.frombuffer((collection_dir / 'fake_id.bin').read_bytes(), dtype=float)
        for i, item in enumerate(file_content):
            assert item == test_array[i]

    def test_read_slice(self, binary_collection):
        collection, _, test_arr = binary_collection

        result = collection.read_slice('test_id')
        assert type(result) == np.ndarray
        for i, item in enumerate(result):
            assert item == test_arr[i]
        
        result = collection.read_slice('test_id', 300, 40000)
        assert type(result) == np.ndarray
        for i, item in enumerate(result):
            assert item == test_arr[300:40000][i]
    
    def test_write_stream(self, binary_collection):
        collection, collection_dir, _ = binary_collection
        test_arr = randarray()

        with collection.write_stream('fake_id') as write_stream:
            for item in test_arr:
                write_stream.write(item)
    
        assert (collection_dir / 'fake_id.bin').exists()
        assert (collection_dir / 'fake_id.bin').is_file()

        file_content = np.frombuffer((collection_dir / 'fake_id.bin').read_bytes(), dtype=float)
        for i, item in enumerate(file_content):
            assert item == test_arr[i]

    def test_read_stream(self, binary_collection):
        collection, _, test_arr = binary_collection

        with collection.read_stream('test_id') as read_stream:
            assert read_stream.tell() == 0
            read_stream.seek(2)
            assert read_stream.tell() == 2
            assert read_stream.read(1)[0] == test_arr[2]
            assert read_stream.tell() == 3
            result = read_stream.read()
            for i, item in enumerate(result):
                assert item == test_arr[3:][i]


def rmrf(directory):
    for item in directory.iterdir():
        if item.is_dir():
            rmrf(item)
        elif item.is_file():
            item.unlink()
    directory.rmdir()
