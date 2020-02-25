"""Type Module

Singular location for reusable complex types.
All types are PascalCase.

To use:
::
  from __future__ import annotations
  from typing import TYPE_CHECKING
  if TYPE_CHECKING:
      import ndi.type as T

  Helpful type references: `docs <https://docs.python.org/3/library/typing.html#the-any-type>`_, `examples <https://www.pythonsheets.com/notes/python-typing.html>`_
"""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  # common basic types
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

  from .schema.ChannelType import ChannelType as ChannelType_schema
  from .schema.ClockType import ClockType as ClockType_schema
  from .schema.ProbeType import ProbeType as ProbeType_schema

  import ndi
  from ndi import Channel, DaqSystem, Epoch, Experiment, Probe
  from ndi import ChannelType, ClockType, ProbeType

  from ndi.file_navigator import FileNavigator, EpochFiles

  from ndi.database import SQL, FileSystem, Query
  from ndi.database.sql import Collection as SQL_Collection
  from ndi.database.file_system import Collection as FS_Collection

  """Schema Types
  Associated with the flatbuffer layer in ndi.schema."""

  Schema = Union[ Channel_schema, DaqSystem_schema, Epoch_schema, Experiment_schema, FileNavigator_schema, Probe_schema ]
  SchemaEnumClass = Union[ Type[ChannelType_schema], Type[ClockType_schema], Type[ProbeType_schema] ]
  SchemaEnum = Union[ ChannelType_schema, ClockType_schema, ProbeType_schema ]

  BuildOffset = int


  """NDI Types
  Associated with the NDI classes and types."""

  NdiClass = Union[ Type[ndi.Channel], Type[ndi.DaqSystem], Type[ndi.Epoch], Type[ndi.Experiment], Type[ndi.FileNavigator], Type[ndi.Probe] ]
  NdiObject = Union[ ndi.Channel, ndi.DaqSystem, ndi.Epoch, ndi.Experiment, ndi.FileNavigator, ndi.Probe ]
  NdiId = str



  """DAQ Types
  Associated with ndi.daqreaders."""

  FilePath = str
 


  """Database Types
  Associated with ndi.database drivers."""




  """Miscellaneous Types"""

  Class = type
  RegexStr = str



  """TODO"""
  
  DaqReader = Any
