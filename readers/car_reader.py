import numpy as np
from pathlib import Path
from typing import Union
from collections import OrderedDict
from typing import List, Tuple

from .common import read_data
from .common import OrderedClassMembers
from .common import Byte, Word, Short, Long, Single


class CarHeader():
    def __init__(self):
        self._internal_map = OrderedDict(
            name=None,
            extra=None,
            num_anims=None,
            num_sounds=None,
            num_points=None,
            num_triang=None,
            bytes_tex=None
        )


class HeaderBlock(metaclass=OrderedClassMembers):
    name: str = None
    extra: str=None
    num_anims: np.int32=None
    num_sounds: np.int32=None
    num_points: np.int32=None
    num_triang: np.int32=None
    bytes_tex: np.int32=None


class TrianglesBlock(metaclass=OrderedClassMembers):
    Tr_Point1 : np.int32 = None
    Tr_Point2 : np.int32 = None
    Tr_Point3 : np.int32 = None
    Tr_CoordX1 : np.int32 = None
    Tr_CoordX2 : np.int32 = None
    Tr_CoordX3 : np.int32 = None
    Tr_CoordY1 : np.int32 = None
    Tr_CoordY2 : np.int32 = None
    Tr_CoordY3 : np.int32 = None
    Tr_U1 : np.int32 = None
    Tr_U2 : np.int32 = None
    Tr_Parent : np.int32 = None
    Tr_U3 : np.int32 = None
    Tr_U4 : np.int32 = None
    Tr_U5 : np.int32 = None
    Tr_U6 : np.int32 = None

    def get_points(self):
        if self.Tr_Point1 is None or self.Tr_Point2 is None or self.Tr_Point3 is None:
            raise RuntimeError("Point values in triangle are null, has this object been initialized?")
        return (self.Tr_Point1, self.Tr_Point2, self.Tr_Point3)

    def get_uv_coords(self):
        return (
            (self.Tr_CoordX1, self.Tr_CoordY1),
            (self.Tr_CoordX3, self.Tr_CoordY2),
            (self.Tr_CoordX3, self.Tr_CoordY3),
        )


class PointsBlock(metaclass=OrderedClassMembers):
    P_CoordX : np.float32 = None
    P_CoordY : np.float32 = None
    P_CoordZ : np.float32 = None
    P_bone : np.float32 = None

    def get_coords(self):
        return (self.P_CoordY, self.P_CoordX, self.P_CoordZ)

    def get_bone(self):
        return self.P_bone


class Animation():
    name = None
    div = None
    num_frames = None
    class Frame(metaclass=OrderedClassMembers):
        pt_coords: List[Tuple[np.float32, np.float32, np.float32]] = []

    def __init__(self):
        self.frames: List[Animation.Frame] = []

    def get_frame_vertices(self, n=0):
        frame = self.frames[n]
        return frame.pt_coords

    def __len__(self):
        return len(self.frames)


class Sound():
    name = None
    length = None
    data = None

    # Hard coded metadata, PCM encoding parameters
    parameters = dict(
        nchannels=1,
        frequency=22050 # Hz
    )


class CarReader():
    """
    Reads CAR file
    """
    def __init__(self, file_path: Union[str, Path]):
        self.file_path = file_path
        self.header = CarHeader()
        self.triangle_blocks = []
        self.points_blocks = []
        self.animations = []
        self.sounds = []
        self.texture = None

    def __enter__(self):
        self.file = open(self.file_path, 'rb')
        self._read_header()

        # Read in triangles
        for _ in range(self.header.num_triang):
            self.triangle_blocks.append(self._read_triangles_block())

        # Read in points
        for _ in range(self.header.num_points):
            self.points_blocks.append(self._read_points_block())

        # Read in texture
        self._read_texture_block()

        # Read in animations
        for _ in range(self.header.num_anims):
            self.animations.append(self._read_animation())

        # Read in sounds
        for _ in range(self.header.num_sounds):
            self.sounds.append(self._read_sound())

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

    def _read_header(self):
        # Read name
        data = self.file.read(24)
        self.header.name = data.decode("ascii")

        # read extra
        data = self.file.read(8)
        self.header.extra = data.decode("ascii")

        # read number of animations
        data = self.file.read(4)
        self.header.num_anims = np.frombuffer(data, '<i4')[0]

        # read number of sounds
        data = self.file.read(4)
        self.header.num_sounds = np.frombuffer(data, '<i4')[0]

        # read number of points
        data = self.file.read(4)
        self.header.num_points = np.frombuffer(data, '<i4')[0]

        # read number of triangles
        data = self.file.read(4)
        self.header.num_triang = np.frombuffer(data, '<i4')[0]

        # Texture length in bytes
        data = self.file.read(4)
        self.header.bytes_tex = np.frombuffer(data, '<i4')[0]

    def _read_triangles_block(self):
        triblock = TrianglesBlock()

        # Read points
        triblock.Tr_Point1 = read_data(self.file, Long)
        triblock.Tr_Point2 = read_data(self.file, Long)
        triblock.Tr_Point3 = read_data(self.file, Long)

        # Read Coordinates of Points
        triblock.Tr_CoordX1 = read_data(self.file, Long)
        triblock.Tr_CoordX2 = read_data(self.file, Long)
        triblock.Tr_CoordX3 = read_data(self.file, Long)
        triblock.Tr_CoordY1 = read_data(self.file, Long)
        triblock.Tr_CoordY2 = read_data(self.file, Long)
        triblock.Tr_CoordY3 = read_data(self.file, Long)

        # Unknown
        triblock.Tr_U1 = read_data(self.file, Long)
        triblock.Tr_U2 = read_data(self.file, Long)

        # index to parent triangle
        triblock.Tr_Parent = read_data(self.file, Long)

        # Unknown
        triblock.Tr_U3 = read_data(self.file, Long)
        triblock.Tr_U4 = read_data(self.file, Long)
        triblock.Tr_U5 = read_data(self.file, Long)
        triblock.Tr_U6 = read_data(self.file, Long)

        return triblock

    def _read_points_block(self):
        ptblock = PointsBlock()

        # Read in point coordinates
        ptblock.P_CoordX = read_data(self.file, Single) 
        ptblock.P_CoordY = read_data(self.file, Single)
        ptblock.P_CoordZ = read_data(self.file, Single)

        # Bone to which point is attached to
        ptblock.P_bone = read_data(self.file, Long)

        return ptblock

    def _read_texture_block(self):
        data = self.file.read(self.header.bytes_tex)
        
        # texture is 16-bit TGA encoded, always 256 pixels wide
        self.texture = np.frombuffer(data, '<u2').reshape((-1, 256))

    def _read_animation(self):
        anim = Animation()

        # Read in name of animation
        data = self.file.read(32)
        anim.name = data.decode("ascii")

        # Read in animation divisor
        anim.div = read_data(self.file, Long)

        # Read in number of frames in animation
        anim.num_frames = read_data(self.file, Long)

        # Read in point coordinates for each frame
        for _ in range(anim.num_frames):
            frame = anim.Frame()
            for _ in range(self.header.num_points):
                pt_coord_x = read_data(self.file, Short)
                pt_coord_y = read_data(self.file, Short)
                pt_coord_z = read_data(self.file, Short)
                frame.pt_coords.append((pt_coord_x, pt_coord_y, pt_coord_z))
            anim.frames.append(frame)

        return anim

    def _read_sound(self):
        sound = Sound()

        # Read in name
        data = self.file.read(32)
        sound.name = data.decode("ascii")

        # Read in byte-length
        sound.length = read_data(self.file, Long)

        # Read in sound data
        sound.data = self.file.read(sound.length)

        return sound
