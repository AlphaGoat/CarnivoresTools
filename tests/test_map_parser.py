import unittest

from utils.read_map import MAPReader


class TestMapReader(unittest.TestCase):
    map_file_path = "resources/Carnivores_2plus/HUNTDAT/AREAS/AREA1.MAP"

    def test_map_reader(self):
        with MAPReader(self.map_file_path) as map_reader:
            map_content = map_reader.get_map()
