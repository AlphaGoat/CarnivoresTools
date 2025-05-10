#"import open3d
import open3d as o3d
import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation
from mpl_toolkits.mplot3d import Axes3D

from utils.read_map import RSCReader, MAPReader
from utils.math import get_bisecting_triangles_from_grid
from utils.images import convert_rgb555_to_rgb888


def render_flat_map(map_file_path,
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

    # Get texture map from MAP file and associated
    # textures
    tmap1 = carnivores_map.TMap1
    tmap2 = carnivores_map.TMap2
    fmap = carnivores_map.FMap
    
    # Generate a mesh from the standard 1024 x 1024 grid
    x = np.arange(0, 11, 1)
    y = np.arange(0, 11, 1)
    X, Y = np.meshgrid(x, y)
    X, Y = X.flatten(), Y.flatten()
    grid_coords = np.stack([X, Y], axis=-1)
#    hmap = carnivores_map.HMap
#    tri = Delaunay(grid_coords)
    tri1, tri2 = get_bisecting_triangles_from_grid(11, 11)

    triangulation_1 = Triangulation(X, Y, triangles=tri1)
    triangulation_2 = Triangulation(X, Y, triangles=tri2)

    plt.triplot(triangulation_1, color='black')
    plt.triplot(triangulation_2, color='black')
   
#    plt.triplot(grid_coords[:, 1], grid_coords[:, 0], tri.simplices)
    plt.plot(grid_coords[:, 1], grid_coords[:, 0], 'o')
    plt.show()


def plot_3d_mesh(map_file_path):
    with MAPReader(map_file_path) as map_reader:
        carnivores_map = map_reader.get_map()
    hmap = carnivores_map.HMap[0:10, 0:10]

    # Generate a mesh from the standard 1024 x 1024 grid
    x = np.arange(0, 11, 1)
    y = np.arange(0, 11, 1)
    X, Y = np.meshgrid(x, y)
    X, Y, Z = X.flatten(), Y.flatten(), hmap.flatten()
    grid_coords = np.stack([X, Y, Z], axis=-1)

    # Get bisecting triangles
    tri1, tri2 = get_bisecting_triangles_from_grid(11, 11)

    triangles = np.concatenate([tri1, tri2], axis=0)
    fig = plt.figure()
#    ax = fig.gca(projection='3d')
    ax = fig.add_subplot(projection='3d')
    ax.plot_trisurf(grid_coords[:, 0], grid_coords[:, 1], grid_coords[:, 2], triangles=triangles)
    plt.show()


def open3d_mesh_visualization(map_file_path,
                              rsc_file_path):
    """
    Render 3d visualization of a portion of the map
    """
    with MAPReader(map_file_path) as map_reader:
        carnivores_map = map_reader.get_map()
    
    with RSCReader(rsc_file_path) as rsc_reader:
        header = rsc_reader.get_header()
        map_textures = rsc_reader.get_textures()

    tmap1 = carnivores_map.TMap1[0:10, 0:10]
    tmap2 = carnivores_map.TMap2[0:10, 0:10]
    hmap = carnivores_map.HMap[0:11, 0:11]

    # Generate a mesh from the standard 1024 x 1024 grid
    x = np.arange(0, 11, 1)
    y = np.arange(0, 11, 1)
    X, Y = np.meshgrid(x, y)
    X, Y, Z = X.flatten(), Y.flatten(), hmap.flatten()
    grid_coords = np.stack([X, Y, Z], axis=-1)

    # Get bisecting triangles
    tri1, tri2 = get_bisecting_triangles_from_grid(11, 11)

    # fetch corresponding textures for each triangle
    textures1 = []
    for t1idx in np.nditer(tmap1.flatten()):
        rgb = convert_rgb555_to_rgb888(map_textures[t1idx].texture_array)
        textures1.append(rgb)


    textures2 = []
    for t2idx in np.nditer(tmap1.flatten()):
        rgb = convert_rgb555_to_rgb888(map_textures[t2idx].texture_array)
        textures2.append(rgb)

    triangles = np.concatenate([tri1, tri2], axis=0)
    textures = np.concatenate([textures1, textures2], axis=0)

    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(grid_coords)
    mesh.triangles = o3d.utility.Vector3iVector(triangles)

    # Create the mesh    
#    mesh = o3d.geometry.TriangleMesh(
#        o3d.utility.Vector3dVector(grid_coords),
#        o3d.utility.Vector3iVector(triangles)
#    )
#    import pdb; pdb.set_trace()
    mesh.textures = [o3d.geometry.Image(t) for t in textures]
#    import random
#    colors = []
#    for coord in grid_coords:
#        r = random.randint(0, 255)
#        g = random.randint(0, 255)
#        b = random.randint(0, 255)
#        colors.append((r, g, b))

#    mesh.vertex_colors = o3d.utility.Vector3dVector(colors)


    mesh.compute_vertex_normals()
#    v_uv = np.random.rand(len(triangles) * 3, 2)
#    mesh.triangle_uvs = o3d.utility.Vector2dVector(v_uv)

    o3d.visualization.draw_geometries([mesh])


if __name__ == "__main__":
    map_file_path = "/home/alphagoat/Projects/CarnivoresIII/resources/Carnivores_2plus/HUNTDAT/AREAS/AREA2.MAP"
    rsc_file_path = "/home/alphagoat/Projects/CarnivoresIII/resources/Carnivores_2plus/HUNTDAT/AREAS/AREA2.RSC"
#    render_flat_map(map_file_path, rsc_file_path)
    open3d_mesh_visualization(map_file_path, rsc_file_path)
#    plot_3d_mesh(map_file_path)
