"""
Generate a 3-d mesh from .MAP file

Author: Peter Thomas
Date: 19 May 2024
"""
import numpy as np
from matplotlib import cm
import matplotlib.pyplot as plt

from utils.read_map import MAPReader


plt.style.use('_mpl-gallery')


def plot_mesh(map_file_path, plot=False):
    # Read in attributes from map file
    with MAPReader(map_file_path) as map_reader:
        MAP = map_reader.get_map()

    # Plot height map
    HMap = MAP.HMap

    x = np.arange(0, 1024, 1)
    y = np.arange(0, 1024, 1)
    X, Y = np.meshgrid(x, y)

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    ax.plot_surface(X, Y, HMap, cmap=cm.Blues)
    ax.set(xticklabels=[],
           yticklabels=[],
           zticklabels=[])
    if plot:
        fig.savefig("map_mesh.png")
    plt.show()


if __name__ == "__main__":
    map_file_path = "/home/alphagoat/Projects/CarnivoresIII/resources/Carnivores_2plus/HUNTDAT/AREAS/AREA1.MAP"
    plot_mesh(map_file_path)
