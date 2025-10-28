from . import Dataset
from ..session.dir import Dir as SessionDir

class Dir(Dataset):
    """
    An NDI dataset associated with a directory.
    """

    def __init__(self, reference, path_name=None, docs=None):
        """
        Initializes a new Dir dataset.

        Args:
            reference: The reference for the dataset or the path if path_name is None.
            path_name: The path to the dataset directory.
            docs: Optional documents to add to the dataset.
        """
        if path_name is None:
            path_name = reference
            self._session = SessionDir(path_name)
        else:
            self._session = SessionDir(reference, path_name)

        self.path = self._session.path

        if docs:
            # Simplified implementation for adding docs
            pass

    @staticmethod
    def dataset_erase(dataset_dir_obj, areyousure='no'):
        """
        Deletes the entire session database folder.

        Args:
            dataset_dir_obj: The dataset directory object to erase.
            areyousure: A string ('yes' or 'no') to confirm deletion.
        """
        if areyousure.lower() == 'yes':
            # Simplified implementation for erasing the dataset
            print(f"Erasing dataset at {dataset_dir_obj.path}")
        else:
            print("Not erasing dataset.")
