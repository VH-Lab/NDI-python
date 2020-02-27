from __future__ import annotations
import ndi.types as T
from abc import ABC, abstractmethod

from ..experiment import Experiment
from ..daq_system import DaqSystem
from ..probe import Probe
from ..epoch import Epoch
from ..channel import Channel
from ..document import Document

class NDI_Database(ABC):
    """
    Abstract class for NDI database interfaces.
    Child classes of :class:`NDI_Database` are standardized, and share the same base methods and data signatures.
    """
    _collections: T.CollectionMap = {
        Experiment: None,
        DaqSystem: None,
        Probe: None,
        Epoch: None,
        Channel: None,
        Document: None
    }

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def add_experiment(self, experiment):
        """.. currentmodule:: ndi.experiment

        It should be able to take an :class:`Experiment` and add it and it's contents (including its DaqSystems, Probes, Channels, and Epochs) to the database.

        :param experminent:
        :type experiment: :class:`Experiment`
        """
        pass

    @abstractmethod
    def create_collection(self, ndi_class):
        """.. currentmodule:: ndi.ndi_object

        It should be able to take a derivative class of :class:`NDI_Object` and create a collection/table based off of it and its fields. The collection/table name should be created from :func:`ndi.database.utils.class_to_collection_name`.

        :param ndi_class:
        :type ndi_class: :class:`NDI_Object`
        """
        pass

    @abstractmethod
    def drop_collection(self, ndi_class):
        """.. currentmodule:: ndi.ndi_object
        Clears all entries for the collection corresponding to the :term:`NDI class` passed and deletes the collection.

        :param ndi_class:
        :type ndi_class: :class:`NDI_Object`
        """

    @abstractmethod
    def add(self, ndi_object):
        """It should be able to add one or many instances of an :term:`NDI object` to the appropriate :term:`collection`.
        
        :param ndi_object:
        :type ndi_object: :term:`NDI object`
        """
        pass

    @abstractmethod
    def update(self, ndi_object):
        """It should be able to update one or many instances of an :term:`NDI object`. Updated entries are found by their :term:`NDI class` and id.
        
        :param ndi_object:
        :type ndi_object: :term:`NDI object`
        """
        pass

    @abstractmethod
    def upsert(self, ndi_object):
        """It should be able to update one or many instances of an :term:`NDI object`. Updated entries are found by their :term:`NDI class` and id. In the case that an instance does not already exist, it should be added to its :term:`collection`.
        
        :param ndi_object:
        :type ndi_object: :term:`NDI object`
        """
        pass

    @abstractmethod
    def delete(self, ndi_object):
        """It should be able to delete one or many instances of an :term:`NDI object`.
        
        :param ndi_object:
        :type ndi_object: :term:`NDI object`
        """
        pass

    @abstractmethod
    def find_by_id(self, ndi_class, id_):
        """It should be able to retrieve a single :term:`document` given the :term:`NDI class` it belongs to and its id.

        :param ndi_class:
        :type ndi_class: :class:`NDI_Object`
        :param id_:
        :type id_: str
        """
        pass

    @abstractmethod
    def update_by_id(self, ndi_class, id_, payload):
        """It should be able to update a single :term:`document` given the :term:`NDI class` it belongs to, its id, and the data being updated.

        :param ndi_class:
        :type ndi_class: :class:`NDI_Object`
        :param id_:
        :type id_: str
        :param payload: Containing fields with values to update to in the specified ndi_class. Not passing a dict will result in no updates.
        :type payload: :term:`payload`, optional
        """
        pass

    @abstractmethod
    def delete_by_id(self, ndi_class, id_):
        """It should be able to remove a single :term:`document` from a collection given its :term:`NDI class` and id.

        :param ndi_class:
        :type ndi_class: :class:`NDI_Object`
        :param id_:
        :type id_: str
        """
        pass

    @abstractmethod
    def find(self, ndi_class, ndi_query):
        """It should be able to utilize a :term:`NDI query` to retrive data from the :term:`collection` of the given :term:`NDI class`.

        :param ndi_class:
        :type ndi_class: :class:`NDI_Object`
        :param ndi_query: A set of conditions to find on. Not passing a query will return all :term:`document`\ s from the :term:`collection.
        :type ndi_query: :term:`NDI query`, optional
        """
        pass

    @abstractmethod
    def update_many(self, ndi_class, ndi_query, payload):
        """It should be able to update all :term:`document`\ s matching the given :term:`NDI query` in the :term:`collection` of the given :term:`NDI class`.

        :param ndi_class:
        :type ndi_class: :class:`NDI_Object`
        :param ndi_query: A set of conditions to update on. Not passing a query will update all :term:`document`\ s from the :term:`collection`.
        :type ndi_query: :term:`NDI query`, optional
        :param payload: Containing fields with values to update to in the specified ndi_class. Not passing a dict will result in no updates.
        :type payload: :term:`payload`, optional
        """
        pass

    @abstractmethod
    def delete_many(self, ndi_class, query):
        """It should be able to delete all :term:`document`\ s matching the given :term:`NDI query` in the :term:`collection` of the given :term:`NDI class`.

        :param ndi_class:
        :type ndi_class: :class:`NDI_Object`
        :param ndi_query: A set of conditions to delete on. Not passing a query will delete all :term:`document`\ s from the :term:`collection`.
        :type ndi_query: :term:`NDI query`, optional
        """
        pass
