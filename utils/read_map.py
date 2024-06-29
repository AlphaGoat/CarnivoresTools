"""
Utilities for parsing Carnvivores .map and .rsc files

Author: Peter Thomas
Date: 18 May, 2024
"""
import struct
import logging
import collections
import numpy as np
from abc import ABC
from pathlib import Path
from itertools import tee
from numpy.typing import NDArray
from collections import OrderedDict
from typing import List, Union, get_type_hints

BLOCK_LEN = 1024 * 1024
SUB_BLOCK_LEN = 512 * 512

BYTE = np.uint8
WORD = np.uint16
SHORT = np.int16
LONG = np.int32
SINGLE = np.uint32


class u16():
    pass


class u8():
    pass


class Ptr(ABC):
    def __init__(self, init_val: int=0):
        self.curr_val = init_val
    def __index__(self):
        return self.curr_val


class PtrU8(Ptr):
    def __init__(self, init_val: int=0):
        super().__init__(init_val=init_val)
    def __add__(self, x):
        return PtrU8(self.curr_val + x)
    def __sub__(self, x):
        return PtrU8(self.curr_val - x)
    def __mul__(self, x):
        if isinstance(x, u8):
            return self
        if isinstance(x, u16):
            return PtrU16(self.curr_val // 2)
        if isinstance(x, int):
            return PtrU8(self.curr_val * x)
        raise ValueError(f"Multiplication with type {type(x)} not recognized.")
    def __str__(self):
        return f"PtrU8[{self.curr_val}]"
    def get_value(self):
        return self.curr_val


class PtrU16(Ptr):
    def __init__(self, init_val: int=0):
        super().__init__(init_val=init_val)
    def __add__(self, x):
        return PtrU16(self.curr_val + x)
    def __sub__(self, x):
        return PtrU16(self.curr_val - x)
    def __mul__(self, x):
        if isinstance(x, u8):
            return PtrU8(self.curr_val * 2)
        if isinstance(x, u16):
            return self
        if isinstance(x, int):
            return PtrU16(self.curr_val * x)
        raise ValueError(f"Multiplication with type {type(x)} not recognized.")
    def __str__(self):
        return f"PtrU16[{self.curr_val}]"
    def get_value(self):
        return self.curr_val


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


class RSCHeader():
    def __init__(self):
        self._internal_map = OrderedDict(
            num_textures=None,
            num_objects=None,
            dawn_atm_light_R=None,
            dawn_atm_light_G=None,
            dawn_atm_light_B=None,
            day_atm_light_R=None,
            day_atm_light_G=None,
            day_atm_light_B=None,
            night_atm_light_R=None,
            night_atm_light_G=None,
            night_atm_light_B=None,
            unknown_dawn_R=None,
            unknown_dawn_G=None,
            unknown_dawn_B=None,
            unknown_day_R=None,
            unknown_day_G=None,
            unknown_day_B=None,
            unknown_night_R=None,
            unknown_night_G=None,
            unknown_night_B=None,
        )
        self._header_key_iter = self._internal_map.keys()
        *_, self._last_key = self._internal_map.keys()

    def assign_next_header_val(self, val: np.int32):
        try:
            next_key = next(self._header_key_iter)
        except StopIteration:
            raise RuntimeError("No available keys in header to assign value to.")
        self._internal_map[next_key] = val

        # Check if we are on the last header key
        if next_key == self._last_key:
            self._create_vars_from_dict_keys()

    def _create_vars_from_dict_keys(self):
        for key in self._internal_map.keys():
            setattr(self, key, self._internal_map[key])


class Texture():
    """
    Class that encapsulates a single texture read from an RSC file.
    Textures are 128x128 16-bit maps.
    """
    def __init__(self, texture_array: np.ndarray):

        if not isinstance(texture_array, np.ndarray):
            raise ValueError("Texture array must be a numpy type array")
        # Ensure that the texture array is 16-bit, 
        # and is 128 x 128
        if texture_array.dtype != np.uint16:
            try:
                texture_array.astype(np.uint16)
            except ValueError:
                raise ValueError("Input texture array must be able to be cast "
                + f"as an 16-bit integer array, but got {type(texture_array)}")

        self.texture_array = texture_array
        if self.texture_array.ndim != 2:
            self.texture_array = self.texture_array.reshape(128, 128)


class Object():
    """
    Class that encapsulates a single object from an RSC file.
    Objects in RSC files consist of a variable number of
    points and triangles and a 256xN 16-bit map, where N is
    height of the bit map and is also variable.
    """
    def __init__(self):
        self.header = self.HeaderSubBlock()
        self.triangle_sub_blocks: List[self.TrianglesSubBlock] = []
        self.points_sub_blocks: List[self.PointsSubBlock] = []
        self.bones_sub_blocks: List[self.BonesSubBlock] = []
        self.texture_sub_block = self.TextureSubBlock()

        # Attribute iterators for each sub-block type
        self._header_attr_iter = tee(iter(self.header.__ordered_attrs__), 2)
        self._triangle_attr_iter = None
        self._points_attr_iter = None
        self._bones_attr_iter = None

        # References to iterators, to be used to create N number of sub block
        # iterators when we know the number of sub blocks to instantiate
        self._triangle_attr_iter_ref = iter(self.TrianglesSubBlock().__ordered_attrs__)
        self._points_attr_iter_ref = iter(self.PointsSubBlock().__ordered_attrs__)
        self._bones_attr_iter_ref = iter(self.BonesSubBlock().__ordered_attrs__)

        # Internal counters to let us know how many 
        # blocks of a certain type we have instantiated,
        # and how many we still need to fill
        self._triangle_block_counter = 0
        self._points_block_counter = 0
        self._bones_block_counter = 0
        self._texture_bytes_counter = 0

    def assign_next_val(self, val):
        try:
            next_header_attr = next(self._header_attr_iter[0])
            setattr(self.header, next_header_attr, val)
            return
        except StopIteration:
            logging.info("All fields in object header sub-block have been assigned values")
            logging.info("Moving onto triangles sub-block")

        if self._triangle_block_counter < self.header.num_triang:
            next_triangle_attr = next(self._triangle_attr_iter[2 * self._triangle_block_counter])
            setattr(
                self.triangle_sub_blocks[2 * self._triangle_block_counter],
                next_triangle_attr,
                val
            )

        else:
            logging.info("All triangle sub-block fields have been assigned values.")
            logging.info("Moving onto points sub-blocks")

        if self._points_block_counter < self.header.num_points:
            next_points_attr = next(self._points_attr_iter[2 * self._points_block_counter])
            setattr(
                self.points_sub_blocks[2 * self._points_block_counter],
                next_points_attr,
                val
            )

        else:
            logging.info("All points sub-block fields have been assigned values.")
            logging.info("Moving onto bones sub-blocks")

        if self._bones_block_counter < self.header.num_bones:
            next_bones_attr = next(self._bones_attr_iter[2 * self._bones_block_counter])
            setattr(
                self.bones_sub_blocks[2 * self._bones_block_counter],
                next_bones_attr,
                val
            )

        else:
            logging.info("All bones sub-block fields have been assigned values.")
            logging.info("Moving onto texture sub-block")

        if self.texture_sub_block.texture is None:
            self.texture_sub_block.texture = np.empty((self.header.long_tex, 256), dtype=np.uint8)
            
        if self._texture_bytes_counter < 256 * self.header.long_tex:
            row = self._texture_bytes_counter // 256
            col = self._texture_bytes_counter % 256
            self.texture_sub_block.texture[row][col] = val
        else:
            raise RuntimeError("This object has no more fields left to fill!")

    def get_next_field_type(self):
        """
        Get the type for the next field that needs to be filled.
        """
        try:
            next_header_attr = next(self._header_attr_iter[1])
            header_type_hints = get_type_hints(self.HeaderSubBlock)
            return header_type_hints[next_header_attr]
        except StopIteration:
            pass

        if not self.triangle_sub_blocks:
            self.triangle_sub_blocks = [self.TrianglesSubBlock() for _ in self.num_triangle_blocks]

        if self._triangle_attr_iter is None:
            self._triangle_attr_iter = tee(self._triangle_attr_iter_ref, 2 * self.num_triangle_blocks)

        try:
            next_triangle_attr = next(self._triangle_attr_iter[2 * self._triangle_block_counter + 1])
            triangle_type_hints = get_type_hints(self.TrianglesSubBlock)
            return triangle_type_hints[next_triangle_attr]
        except StopIteration:
            if self._triangle_block_counter < self.header.num_triang: self._triangle_block_counter += 1
            if self._triangle_block_counter < self.header.num_triang:
                next_triangle_attr = next(self._triangle_attr_iter[2 * self._triangle_block_counter + 1])
                triangle_type_hints = get_type_hints(self.TrianglesSubBlock)
                return triangle_type_hints[next_triangle_attr]

        if not self.points_sub_blocks:
            self.points_sub_blocks = [self.PointsSubBlock() for _ in range(self.header.num_points)]

        if self._points_attr_iter is None:
            self._points_attr_iter = tee(self._points_attr_iter_ref, 2 * self.header.num_points)

        try:
            next_point_attr = next(self._points_attr_iter[2 * self._points_block_counter + 1])
            point_type_hints = get_type_hints(self.PointsSubBlock)
            return point_type_hints[next_point_attr]
        except StopIteration:
            if self._points_block_counter < self.header.num_points: self._points_block_counter += 1
            if self._points_block_counter < self.header.num_points:
                next_point_attr = next(self._points_attr_iter[2 * self._points_block_counter + 1])
                point_type_hints = get_type_hints(self.PointsSubBlock)
                return point_type_hints[next_point_attr]

        if not self.bones_sub_blocks:
            self.bones_sub_blocks = [self.BonesSubBlock() for _ in range(self.header.num_bones)]

        if self._bones_attr_iter is None:
            self._bones_attr_iter = tee(self._bones_attr_iter_ref, 2 * self.header.num_bones)

        try:
            next_bone_attr = next(self._bones_attr_iter[2 * self._bones_block_counter + 1])
            bone_type_hints = get_type_hints(self.BonesSubBlock)
            return bone_type_hints[next_bone_attr]
        except StopIteration:
            if self._bones_block_counter < self.header.num_bones: self._bones_block_counter += 1
            if self._bones_block_counter < self.header.num_bones:
                next_bone_attr = next(self._bones_attr_iter[2 * self._bones_block_counter + 1])
                bone_type_hints = get_type_hints(self.BonesSubBlock)
                return bone_type_hints[next_bone_attr]

        # Texture sub block has only one attribute of certain dtype
        if self._texture_bytes_counter < 256 * self.header.long_tex:
            return np.uint8

        # When we are done, return Null to let reader know that
        # all fields in this object have been filled
        return None

    def are_there_fields_without_assigned_values(self):
        # Check to see if all fields in the header 
        # have been assigned
        header_fields = vars(self.header)
        for field in header_fields.keys():
            if header_fields[field] is None:
                return True

        # If the header field for the number of triangles is 
        # greater than zero, but no triangle sub blocks have
        # been instantiated, then 
        if self.header.num_triang > 0 and len(self.triangle_sub_blocks) == 0:
            return True

    class HeaderSubBlock(metaclass=OrderedClassMembers):
        Ob1: np.int32 = None
        Ob2: np.int32 = None
        Ob3: np.int32 = None
        Ob4: np.int32 = None
        Ob5: np.int32 = None
        Ob6: np.int32 = None
        Ob7: np.int32 = None
        Ob8: np.int32 = None
        Ob9: np.int32 = None
        Ob10: np.int32 = None
        Ob11: np.int32 = None
        Ob12: np.int32 = None
        Ob13: np.int32 = None
        Ob14: np.int32 = None
        Ob15: np.int32 = None
        Ob16: np.int32 = None
        num_points: np.int32 = None
        num_triang: np.int32 = None
        num_bones: np.int32 = None
        long_tex: np.int32 = None

    class TrianglesSubBlock(metaclass=OrderedClassMembers):
        Tn_Point1: np.int32 = None
        Tn_Point2: np.int32 = None
        Tn_Point3: np.int32 = None
        Tn_CoordX1: np.int32 = None
        Tn_CoordX2: np.int32 = None
        Tn_CoordX3: np.int32 = None
        Tn_CoordY1: np.int32 = None
        Tn_CoordY2: np.int32 = None
        Tn_CoordY3: np.int32 = None
        Tn_U1: np.int32 = None
        Tn_U2: np.int32 = None
        Tn_Parent: np.int32 = None
        Tn_U3: np.int32 = None
        Tn_U4: np.int32 = None
        Tn_U5: np.int32 = None
        Tn_U6: np.int32 = None

    class PointsSubBlock(metaclass=OrderedClassMembers):
        Pn_CoordX: np.uint32 = None
        Pn_CoordY: np.uint32 = None
        Pn_CoordZ: np.uint32 = None
        Pn_bone: np.int32 = None

    class BonesSubBlock(metaclass=OrderedClassMembers):
        bone1_name: str = None
        bone1_X: np.uint32 = None
        bone1_Y: np.uint32 = None
        bone1_Z: np.uint32 = None
        bone1_parent: np.int16 = None
        bone1_unknown: np.int16 = None
        bone2_X: np.uint32 = None
        bone2_Y: np.uint32 = None
        bone2_Z: np.uint32 = None
        bone2_parent: np.int16 = None
        bone2_unknown: np.int16 = None

    class TextureSubBlock():
        texture: NDArray[np.uint8] = None


class SkyBlock():
    sky_bmp: NDArray[BYTE] = None
    clouds_bmp: NDArray[BYTE] = None


class FogBlock():
    num_fogs: LONG = None

    def __init__(self):
        self.fog_sections: List[self.FogSection] = []

        # Counter to keep track of which fog section
        # we are on
        self._fog_section_counter = 0

        # fog section attribute iterator
        self._fog_section_attr_iter = None

    def get_next_field_type(self):
        if self.num_fogs is None:
            return LONG
        self._fog_section_attr_iter = tee(iter(self.FogSection().__ordered_attrs__), 2)
        pass

    def are_there_fields_without_assigned_values(self):
        if self.num_fogs is None:
            return True

        # If the header field for the number of triangles is 
        # greater than zero, but no triangle sub blocks have
        # been instantiated, then 
        if self.num_fogs > 0 and len(self.fog_sections) == 0:
            return True

        for section in self.fog_sections:
            section_vars = vars(section)
            for field in section_vars.keys():
                if section_vars[field] == None:
                    return True

        return False

    class FogSection(metaclass=OrderedClassMembers):
        fog_RGBA: NDArray[BYTE] = None
        fog_alt: SINGLE = None
        fig_poison: LONG = None
        fog_dist: SINGLE = None
        fog_dens: SINGLE = None



class RSCReader():
    def __init__(self, file_path: Union[str, Path]):
        self.file_path = file_path
        self.header = RSCHeader()
        self.textures = []
        self.objects = []
        self.skyblock = SkyBlock()

    def __enter__(self):
        self.file = open(self.file_path, 'rb')
        self._read_header()
        self._parse_textures()
        self._parse_objects()
        self._parse_sky_block()
        self._parse_fog_block()

    def __exit__(self):
        self.file.close()

    def _read_header(self):
        # Header consists of first 80 bytes in file,
        # which populates 20 long data structures
        for _ in range(20):
            data = self.file.read(4)
            val = np.frombuffer(data, 'int32')
            self.header.assign_next_header_val(val)

    def _parse_textures(self):
        num_textures = self.header.num_textures
        for _ in range(num_textures):
            texture_array = []
            for _ in range(128 * 128):
                data = self.file.read(2)
                val = np.frombuffer(data, 'uint16')
                texture_array.append(val)
            self.textures.append(Texture(np.array(
                texture_array, dtype=np.int16).reshape(128, 128)))

    def _parse_objects(self):
        num_objects = self.header.num_objects
        for _ in range(num_objects):
            obj = Object()
            while obj.are_there_fields_without_assigned_values():
                # Get the data type for the next field
                # in this object
                field_type = obj.get_next_field_type()
                if field_type == np.uint8:
                    data = self.file.read(1)
                    val = np.frombuffer(data, 'uint8')
                elif field_type == np.uint16:
                    data = self.file.read(2)
                    val = np.frombuffer(data, 'uint16')
                elif field_type == np.int16:
                    data = self.file.read(2)
                    val = np.frombuffer(data, 'int16')
                elif field_type == np.int32:
                    data = self.file.read(4)
                    val = np.frombuffer(data, 'int32')
                elif field_type == np.uint32:
                    data = self.file.read(4)
                    val = np.frombuffer(data, 'uint32')
                elif field_type == str:
                    data = self.file.read(32)
                    val = data.decode('ascii')
                elif field_type == NDArray:
                    data = self.file.read(1)
                    val = np.frombuffer(data, 'uint8')

                obj.assign_next_val(val)
            self.objects.append(obj)

    def _parse_sky_block(self):
        sky_map_data = self.file.read(256 * 256 * 2)
        sky_map_array = np.frombuffer(sky_map_data, 'uint16')
        self.skyblock.sky_bmp = sky_map_array

        cloud_map_data = self.file.read(128 * 128 * 1)
        cloud_map_array = np.frombuffer(cloud_map_data, 'uint8')
        self.skyblock.cloud_bmp = cloud_map_array

    def _parse_fog_block(self):
        pass

    def get_header(self):
        return self.header

    def get_textures(self):
        return self.textures

    def get_objects(self):
        return self.objects

    def get_skyblock(self):
        return self.skyblock


class MAP():

    def __init__(self):
        self._HMap: NDArray[np.uint8] = None
        self._TMap1: NDArray[np.uint16] = None
        self._TMap2: NDArray[np.uint16] = None
        self._OMap: NDArray[np.uint8] = None
        self._FMap: NDArray[np.uint16] = None
        self._DawnLMap: NDArray[np.uint8] = None
        self._DayLMap: NDArray[np.uint8] = None
        self._NightLMap: NDArray[np.uint8] = None
        self._WMap: NDArray[np.uint8] = None
        self._HMap0: NDArray[np.uint8] = None
        self._FogsMap: NDArray[np.uint8] = None
        self._AmbMap: NDArray[np.uint8] = None

    def _parse_uint16_block(
            self,
            attribute_name: str,
            value: Union[bytes, NDArray[np.uint16]],
    ):
        if not isinstance(value, bytes) and not isinstance(value, np.ndarray):
            raise ValueError("{} property can only be set by ".format(attribute_name)
                             + "byte array or np.uint16 array")

        if isinstance(value, bytes):
            assert len(value) == 2 * BLOCK_LEN, f"Length of byte array must be {2 * BLOCK_LEN}"
            value = np.frombuffer(value, np.uint16)

        setattr(self, attribute_name, np.reshape(value, (1024, 1024)))

    def _parse_uint8_block(
            self,
            attribute_name: str,
            value: Union[bytes, NDArray[np.uint8]],
    ):
        if not isinstance(value, bytes) and not isinstance(value, np.ndarray):
            raise ValueError("{} property can only be set by ".format(attribute_name)
                             + "byte array or np.uint8 array")

        if isinstance(value, bytes):
            assert len(value) == BLOCK_LEN, f"Length of byte array must be {BLOCK_LEN}"
            value = np.frombuffer(value, np.uint8)

        setattr(self, attribute_name, np.reshape(value, (1024, 1024)))

    def _parse_uint8_sub_block(
            self,
            attribute_name: str,
            value: Union[bytes, NDArray[np.uint8]],
    ):
        if not isinstance(value, bytes) and not isinstance(value, np.ndarray):
            raise ValueError("{} property can only be set by ".format(attribute_name)
                             + "byte array or np.uint8 array")

        if isinstance(value, bytes):
            assert len(value) == SUB_BLOCK_LEN, f"Length of byte array must be {SUB_BLOCK_LEN}"
            value = np.frombuffer(value, np.uint8)

        setattr(self, attribute_name, np.reshape(value, (512, 512)))

    # HMap
    def _get_hmap(self) -> NDArray[np.uint8]:
        return self._HMap

    def _set_hmap(self, value: Union[bytes, NDArray[np.uint8]]):
        self._parse_uint8_block("_HMap", value)

    def _del_hmap(self):
        del self._HMap

    # TMap1
    def _get_tmap1(self) -> NDArray[np.uint16]:
        return self._TMap1

    def _set_tmap1(self, value: Union[bytes, NDArray[np.uint16]]):
        self._parse_uint16_block("_TMap1", value)

    def _del_tmap1(self):
        del self._TMap1

    # TMap2
    def _get_tmap2(self) -> NDArray[np.uint16]:
        return self._TMap2

    def _set_tmap2(self, value: Union[bytes, NDArray[np.uint16]]):
        self._parse_uint16_block("_TMap2", value)

    def _del_tmap2(self):
        del self._TMap2

    # OMap
    def _get_omap(self) -> NDArray[np.uint8]:
        return self._OMap

    def _set_omap(self, value: Union[bytes, NDArray[np.uint8]]):
        self._parse_uint8_block("_OMap", value)

    def _del_omap(self):
        del self._OMap

    # FMap
    def _get_fmap(self) -> NDArray[np.uint16]:
        return self._FMap

    def _set_fmap(self, value: Union[bytes, NDArray[np.uint16]]):
        if not isinstance(value, bytes) and not isinstance(value, np.ndarray):
            raise ValueError("FMap property can only be set by byte array or np.uint16 array")

        if isinstance(value, bytes):
            assert len(value) == 2 * BLOCK_LEN, f"Length of byte array must be {BLOCK_LEN}"
            value = np.frombuffer(value, np.uint16)

        # Convert to bit string representation for each value
        # in array
        bit_string = np.unpackbits(value.view(np.uint8))
        self._FMap = np.reshape(bit_string, (1024, 1024, 16))

    def _del_fmap(self):
        del self._FMap

    # DawnLMap
    def _get_dawn_lmap(self) -> NDArray[np.uint8]:
        return self._DawnLMap

    def _set_dawn_lmap(self, value: Union[bytes, NDArray[np.uint8]]):
        self._parse_uint8_block("_DawmLMap", value)

    def _del_dawn_lmap(self):
        del self._DawnLMap

    # DayLMap
    def _get_day_lmap(self) -> NDArray[np.uint8]:
        return self._DayLMap

    def _set_day_lmap(self, value: Union[bytes, NDArray[np.uint8]]):
        self._parse_uint8_block("_DayLMap", value)

    def _del_day_lmap(self):
        del self._DayLMap

    # NightLMap
    def _get_night_lmap(self) -> NDArray[np.uint8]:
        return self._NightLMap

    def _set_night_lmap(self, value: Union[bytes, NDArray[np.uint8]]):
        self._parse_uint8_block("_NightLMap", value)

    def _del_night_lmap(self):
        del self._NightLMap

    # WMap
    def _get_wmap(self) -> NDArray[np.uint8]:
        return self._WMap

    def _set_wmap(self, value: Union[bytes, NDArray[np.uint8]]):
        self._parse_uint8_block("_WMap", value)

    def _del_wmap(self):
        del self._WMap

    # HMap0
    def _get_hmap0(self) -> NDArray[np.uint8]:
        return self._HMap0

    def _set_hmap0(self, value: Union[bytes, NDArray[np.uint8]]):
        self._parse_uint8_block("_HMap0", value)

    def _del_hmap0(self):
        del self._HMap0

    # FogsMap
    def _get_fogsmap(self) -> NDArray[np.uint8]:
        return self._FogsMap

    def _set_fogsmap(self, value: Union[bytes, NDArray[np.uint8]]):
        self._parse_uint8_sub_block("_FogsMap", value)

    def _del_fogsmap(self):
        del self._FogsMap

    # AmbMap
    def _get_ambmap(self) -> NDArray[np.uint8]:
        return self._AmbMap

    def _set_ambmap(self, value: Union[bytes, NDArray[np.uint8]]):
        self._parse_uint8_sub_block("_AmbMap", value)

    def _del_ambmap(self):
        del self._AmbMap

    HMap: NDArray[np.uint8] = property(
        fget=_get_hmap,
        fset=_set_hmap,
        fdel=_del_hmap,
        doc="Height Map property."
    )
    TMap1: NDArray[np.uint16] = property(
        fget=_get_tmap1,
        fset=_set_tmap1,
        fdel=_del_tmap1,
        doc="TMap1 property. Contains indices to ground texture in RSC."
    )
    TMap2: NDArray[np.uint16] = property(
        fget=_get_tmap2,
        fset=_set_tmap2,
        fdel=_del_tmap2,
        doc="TMap2 property. Contains indices to ground texture in RSC for distant mesh."
    )
    OMap: NDArray[np.uint8] = property(
        fget=_get_omap,
        fset=_set_omap,
        fdel=_del_omap,
        doc="OMap property. Contains indices of 3DF object in RSC."
    )
    FMap: NDArray[np.uint8] = property(
        fget=_get_fmap,
        fset=_set_fmap,
        fdel=_del_fmap,
        doc="FMap property. Set of flags for each cell."
    )
    DawnLMap: NDArray[np.uint8] = property(
        fget=_get_dawn_lmap,
        fset=_set_dawn_lmap,
        fdel=_del_dawn_lmap,
        doc="DawnLMap property. Grayscale lightmap for dawn."
    )
    DayLMap: NDArray[np.uint8] = property(
        fget=_get_day_lmap,
        fset=_set_day_lmap,
        fdel=_del_day_lmap,
        doc="DayLMap property. Grayscale lightmap for day."
    )
    NightLMap: NDArray[np.uint8] = property(
        fget=_get_night_lmap,
        fset=_set_night_lmap,
        fdel=_del_night_lmap,
        doc="DayLMap property. Grayscale lightmap for night."
    )
    WMap: NDArray[np.uint8] = property(
        fget=_get_wmap,
        fset=_set_wmap,
        fdel=_del_wmap,
        doc="WMap property. Indices to water table in RSC."
    )
    HMap0: NDArray[np.uint8] = property(
        fget=_get_hmap0,
        fset=_set_hmap0,
        fdel=_del_hmap0,
        doc="HMap0 property. Height map for objects that have the ofPLACEUSER flag."
    )
    FogsMap: NDArray[np.uint8] = property(
        fget=_get_fogsmap,
        fset=_set_fogsmap,
        fdel=_del_fogsmap,
        doc="FogsMap property. Indices to fog table in RSC."
    )
    AmbMap: NDArray[np.uint8] = property(
        fget=_get_ambmap,
        fset=_set_ambmap,
        fdel=_del_fogsmap,
        doc="FogsMap property. Indices to fog table in RSC."
    )


class MAPReader():
    def __init__(self, file_path: Union[str, Path]):
        self.file_path = file_path
        self.ptr = PtrU8()
        self.MAP = MAP()

    def __enter__(self):
        self.file = open(self.file_path, 'rb')

        # Read out the HMAP
        try:
            data = self.file.read(BLOCK_LEN)
            self.MAP.HMap = data

            # Read out TMAP1
            data = self.file.read(2 * BLOCK_LEN)
            self.MAP.TMap1 = data

            # Read out TMAP2
            data = self.file.read(2 * BLOCK_LEN)
            self.MAP.TMap2 = data

            # Read out OMap
            data = self.file.read(BLOCK_LEN)
            self.MAP.OMap = data

            # Read out FMap
            data = self.file.read(2 * BLOCK_LEN)
            self.MAP.FMap = data

            # Read out Dawn LMap
            data = self.file.read(BLOCK_LEN)
            self.MAP.DawnLMap = data

            # Read out Day LMap
            data = self.file.read(BLOCK_LEN)
            self.MAP.DayLMap = data

            # Read out Night LMap
            data = self.file.read(BLOCK_LEN)
            self.MAP.NightLMap = data

            # Read out height map for objects that
            # have ofPLACEUSER flag
            data = self.file.read(BLOCK_LEN)
            self.MAP.HMap0 = data

            # Read out FogsMap
            data = self.file.read(SUB_BLOCK_LEN)
            self.MAP.FogsMap = data

            # Read out AmbMap
            data = self.file.read(SUB_BLOCK_LEN)
            self.MAP.AmbMap = data

        except Exception as e:
            raise RuntimeError(f"Failed to parse {self.file_path}."
                    + " (could map file be corrupt?"
                    + f"\nFailed with error {e}")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

    def get_map(self):
        return self.MAP


def bytes_to_int(bytes):
    return int.from_bytes(bytes, byteorder='big', signed=False) 


def read_map_file(file_path):
    # Open map as both 8 bit and 16 bit arrays
    with open(file_path, "rb") as f1:
        map_array_u8 = np.fromfile(f1, dtype=np.uint8)
    with open(file_path, "rb") as f2:
        map_array_u16 = np.fromfile(f2, dtype=np.uint16)

    # Initialize a pointer to keep track of where
    # we are in map array
    ptr = PtrU8()

    # extract information from map array
    HMap = map_array_u8[:BLOCK_LEN]
    ptr += BLOCK_LEN

    # 16-bit conversion
    ptr = ptr * u16()
    import pdb; pdb.set_trace()
    TMap1 = map_array_u16[ptr: ptr + BLOCK_LEN]
    ptr += BLOCK_LEN
    TMap2 = map_array_u16[ptr: ptr + BLOCK_LEN]
    ptr += BLOCK_LEN

    # 8-bit conversion
    ptr = ptr * u8()
    OMap = map_array_u8[ptr: ptr + BLOCK_LEN]
    ptr += BLOCK_LEN

    # 16-bit conversion
    ptr = ptr * u16()
    FMap = map_array_u16[ptr:ptr + BLOCK_LEN]
    ptr += BLOCK_LEN

    # 8-bit conversion
    ptr = ptr * u8()
    dawn_lmap = map_array_u8[ptr: ptr + BLOCK_LEN]
    ptr += BLOCK_LEN
    day_lmap = map_array_u8[ptr: ptr + BLOCK_LEN]
    ptr += BLOCK_LEN
    night_lmap = map_array_u8[ptr: ptr + BLOCK_LEN]
    ptr += BLOCK_LEN
    WMap = map_array_u8[ptr: ptr + BLOCK_LEN]
    ptr += BLOCK_LEN
    HMap0 = map_array_u8[ptr: ptr + BLOCK_LEN]
    ptr += BLOCK_LEN
    FogsMap = map_array_u8[ptr: ptr + SUB_BLOCK_LEN]
    ptr += SUB_BLOCK_LEN
    AmbMap = map_array_u8[ptr: ptr + SUB_BLOCK_LEN]

    import pdb; pdb.set_trace()


def read_rsc_file(file_path):
#    with open(file_path, "rb") as f:
#        data = f.read(4)
#    header = bytes_to_int(data)
#    import pdb; pdb.set_trace()
#    with open(file_path, "rb") as f:
#        data = f.read(4)
    with RSCReader(file_path) as reader:
        header = reader.get_header()
    import pdb; pdb.set_trace()


if __name__ == "__main__":
    rsc_object = Object()
    import pdb; pdb.set_trace()

#    map_file_path = "/home/alphagoat/Projects/CarnivoresIII/resources/Carnivores_2plus/HUNTDAT/AREAS/AREA1.MAP"
#
#    rsc_file_path = "/home/alphagoat/Projects/CarnivoresIII/resources/Carnivores_2plus/HUNTDAT/AREAS/AREA1.RSC"
#
##    read_map_file(map_file_path)
#    read_rsc_file(rsc_file_path)
#
