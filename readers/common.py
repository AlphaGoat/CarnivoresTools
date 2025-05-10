import collections
import numpy as np
from abc import ABC, abstractmethod


# Data types present in CarnivoresII files
class DataType(ABC):
    @classmethod
    @property
    @abstractmethod
    def num_bytes(cls):
        raise NotImplementedError

    @classmethod
    @property
    @abstractmethod
    def nptype(cls):
        raise NotImplementedError


class Byte(DataType):
    num_bytes = 1
    nptype = '<u1'

class Word(DataType):
    num_bytes = 2
    nptype = '<u2'

class Short(DataType):
    num_bytes = 2
    nptype = '<i2'

class Long(DataType):
    num_bytes = 4
    nptype = '<i4'

class Single(DataType):
    num_bytes = 4
    nptype = 'f'


def read_data(file_handle, dtype):
    data = file_handle.read(dtype.num_bytes)
    data = np.frombuffer(data, dtype.nptype)[0]
    return data


class OrderedClassMembers(type):
    @classmethod
    def __prepare__(self, name, bases):
        return collections.OrderedDict()
    def __new__(self, name, bases, classdict):
        classdict['__ordered_attrs__'] = [
            key for key in classdict.keys()
            if key not in ('__module__', '__qualname__')
        ]
        return type.__new__(self, name, bases, classdict)


