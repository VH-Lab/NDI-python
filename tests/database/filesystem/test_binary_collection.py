from ndi.database.file_system import BinaryCollection
from pathlib import Path
import numpy as np

randarray = np.random.random(200000)

class TestBinaryCollection:
    def setup(self):
        self.collection = BinaryCollection('./test_db', 'document')
        self.collection_dir = self.collection.collection_dir

    def test_directory_creation(self):
        self.setup()
        assert self.collection_dir.exists()
        assert self.collection_dir.is_dir()

        self.tear_down()
        assert not self.collection_dir.exists()

    def test_write(self):
        self.setup()
        self.collection.write('fake_id', randarray)

        assert (self.collection_dir / 'fake_id.bin').exists()
        assert (self.collection_dir / 'fake_id.bin').is_file()

    def test_read_slice(self):
        result = self.collection.read_slice('fake_id')
        assert type(result) == np.ndarray
        for i, item in enumerate(result):
            assert item == randarray[i]
        
        result = self.collection.read_slice('fake_id', 300, 40000)
        assert type(result) == np.ndarray
        for i, item in enumerate(result):
            assert item == randarray[300:40000][i]
    
    def test_read_stream(self):
        with self.collection.read_stream('fake_id') as stream:
            assert stream.tell() == 0
            stream.seek(2)
            assert stream.tell() == 2
            assert stream.read(1)[0] == randarray[2]
            assert stream.tell() == 3
            result = stream.read()
            for i, item in enumerate(result):
                assert item == randarray[3:][i]
                
        self.tear_down()
        assert not self.collection_dir.exists()

    

    def tear_down(self):
        rmrf(self.collection_dir)


def rmrf(directory):
    for item in directory.iterdir():
        if item.is_dir():
            rmrf(item)
        elif item.is_file():
            item.unlink()
    directory.rmdir()
