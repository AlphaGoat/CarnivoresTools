import numpy as np
from numpy.random import default_rng
import matplotlib.pyplot as plt

from utils.read_map import MAPReader, RSCReader
from utils.images import convert_rgb555_to_rgb888 # convert_rgb565_to_rgb_8bit



def render_textures(map_file_path,
                    rsc_file_path):
    """
    Render a top-down depiction of the flattened map
    with all textures
    """
    with MAPReader(map_file_path) as map_reader:
        carnivores_map = map_reader.get_map()
    
    with RSCReader(rsc_file_path) as rsc_reader:
        header = rsc_reader.get_header()
        textures = rsc_reader.get_textures()
        objects = rsc_reader.get_objects()

    rng = default_rng()
    sampled_indices = rng.choice(len(textures), size=16, replace=False)

    # Set up base plot
    fig = plt.figure(figsize=(8, 8))

    for i, idx in enumerate(sampled_indices):
        sampled_texture = textures[idx]
        texture_array = convert_rgb555_to_rgb888(sampled_texture.texture_array)
        fig.add_subplot(4, 4, i + 1)
        plt.imshow(texture_array)

#    plt.imshow(texture_array, interpolation="nearest")
    plt.show()


if __name__ == "__main__":
    map_file_path = "/home/alphagoat/Projects/CarnivoresIII/resources/Carnivores_2plus/HUNTDAT/AREAS/AREA2.MAP"
    rsc_file_path = "/home/alphagoat/Projects/CarnivoresIII/resources/Carnivores_2plus/HUNTDAT/AREAS/AREA2.RSC"
#    render_flat_map(map_file_path, rsc_file_path)
    render_textures(map_file_path, rsc_file_path)
