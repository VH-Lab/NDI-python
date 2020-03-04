"""Type Module

Singular location for reusable complex types.
All types are PascalCase.

To use:
::
  from __future__ import annotations
  from typing import TYPE_CHECKING
  if TYPE_CHECKING:
      import ndi.types as T

  Helpful type references: `docs <https://docs.python.org/3/library/typing.html#the-any-type>`_, `examples <https://www.pythonsheets.com/notes/python-typing.html>`_
"""

# common basic types
from typing import TYPE_CHECKING, NewType

NdiId = NewType('NdiId', str)

FilePath = NewType('FilePath', str)

if TYPE_CHECKING:
    from typing import *
    from typing import List, Set, Dict, Tuple, Iterable, Mapping
    # uncommon basic types
    from typing import IO, Pattern, Match, Text
    from typing import Type, ClassVar, Union, Literal, TypedDict
    from typing import TypeVar, Callable, Generic, Protocol
    from typing import Optional, Final, Any

    from flatbuffers import Builder

    from .schema.Channel import Channel as Channel_schema
    from .schema.DaqSystem import DaqSystem as DaqSystem_schema
    from .schema.Epoch import Epoch as Epoch_schema
    from .schema.Experiment import Experiment as Experiment_schema
    from .schema.FileNavigator import FileNavigator as FileNavigator_schema
    from .schema.Probe import Probe as Probe_schema
    from .schema.Document import Document as Document_schema

    from .schema.ChannelType import ChannelType as ChannelType_schema
    from .schema.ClockType import ClockType as ClockType_schema
    from .schema.ProbeType import ProbeType as ProbeType_schema

    from ndi import NDI_Object
    from ndi import Channel, DaqSystem, Epoch, Experiment, Probe, Document, DocumentExtension
    from ndi import ChannelType, ClockType, ProbeType

    from ndi.file_navigator import FileNavigator, EpochFiles

    from ndi.database import SQL, FileSystem, Query
    from ndi.database.sql import Collection as SQL_Collection
    from ndi.database.file_system import Collection as FS_Collection

    from sqlalchemy.orm import relationship, Session

    """Schema Types
        Associated with the flatbuffer layer in ndi.schema."""

    SchemaClass = Union[
        Type[Channel_schema],
        Type[DaqSystem_schema],
        Type[Epoch_schema],
        Type[Experiment_schema],
        Type[FileNavigator_schema],
        Type[Probe_schema],
        Type[Document_schema]
    ]

    Schema = Union[
        Channel_schema,
        DaqSystem_schema,
        Epoch_schema,
        Experiment_schema,
        FileNavigator_schema,
        Probe_schema,
        Document_schema
    ]

    SchemaVar = TypeVar(
        'SchemaVar',
        Channel_schema,
        DaqSystem_schema,
        Epoch_schema,
        Experiment_schema,
        FileNavigator_schema,
        Probe_schema,
        Document_schema
    )

    SchemaEnumClass = Union[
        Type[ChannelType_schema],
        Type[ClockType_schema],
        Type[ProbeType_schema]
    ]

    SchemaEnum = Union[
        ChannelType_schema,
        ClockType_schema,
        ProbeType_schema
    ]

    """NDI Types
        Associated with the NDI classes and types."""

    NdiClass = Type[NDI_Object]
    NdiObject = NDI_Object

    """Database Types
        Associated with ndi.database drivers."""

    CollectionMap = Dict[
        # in sql database, lookup tables have string keys.
        Union[ NdiClass, str ], 
        Union[ SQL_Collection, FS_Collection, None ]
    ]

    # SQL

    RelationshipMap = Dict[NdiClass, relationship]

    """Miscellaneous Types / Aliases"""

    BuildOffset = int

    Class = type

    RegexStr = str

    """TODO"""

    DaqReader = Any
