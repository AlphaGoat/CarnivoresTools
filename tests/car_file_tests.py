"""
Visualize an object from carnivores II file
"""
import sounddevice
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt

from utils.images import convert_rgb555_to_rgb888
from readers import CarReader


def plot_texture(texture):
    texture = convert_rgb555_to_rgb888(texture)
    fig = plt.figure(figsize=(8, 8))
    plt.imshow(texture)
    plt.show()


def plot_point_cloud(points):
    coords = []
    bones = []
    for pt in points:
        coords.append(pt.get_coords())
        bones.append(pt.get_bone())

    coords_array = np.array(coords)
    bones_array = np.array(bones)

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector((coords))
    pcd.paint_uniform_color([0.5, 0.5, 0.5])
    pcd.estimate_normals()
    pcd.orient_normals_consistent_tangent_plane(1)
    o3d.visualization.draw([pcd])


def plot_tri_mesh(triangles, points):
    vertex_coords = []
    faces = []

    for pt in points:
        vertex_coords.append(pt.get_coords())

    for tri in triangles:
        faces.append(tri.get_points())

    faces = np.array(faces)
    vertex_coords = np.array(vertex_coords)

    mesh = o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(vertex_coords),
                                     o3d.utility.Vector3iVector(faces))
    mesh.compute_vertex_normals()
    o3d.visualization.draw_geometries([mesh])


def plot_carnivoresII_dino(texture, triangles, points):

    # Convert 16-bit TGA to 8-bit RGB
    texture = convert_rgb555_to_rgb888(texture)

    # Get points, triangles, and bones of mesh
    vertex_coords = []
    faces = []
    uv_coords = []

    for pt in points:
        vertex_coords.append(pt.get_coords())

    for tri in triangles:
        faces.append(tri.get_points())
        uv_coords.append(tri.get_uv_coords())

    vertex_coords = np.array(vertex_coords)
    faces = np.array(faces)
    uv_coords = np.array(uv_coords)

    # normalize coordinates
    normalized_uv_coords = np.zeros((len(uv_coords), 3, 2), dtype=np.float32)
    normalized_uv_coords[..., 0] = uv_coords[..., 0] / texture.shape[0]
    normalized_uv_coords[..., 1] = uv_coords[..., 1] / texture.shape[1]
    normalized_uv_coords = normalized_uv_coords.reshape((-1, 2))

    # Define mesh and plot
    mesh = o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(vertex_coords),
                                     o3d.utility.Vector3iVector(faces))
    mesh.compute_vertex_normals()
#    mesh.triangle_normals = o4d.utility.Vector3dVector(-1. *
#            np.asarray(mesh.triangle_normals))

    mesh.triangle_uvs = o3d.utility.Vector2dVector(normalized_uv_coords)
    mesh.textures = [o3d.geometry.Image(texture)]
    mesh.triangle_material_ids = o3d.utility.IntVector([0] * len(faces))

    o3d.visualization.draw_geometries([mesh])


def plot_sounds(sounds):
    fig = plt.figure(figsize=(8, 8))
    for i, sound in enumerate(sounds):
        signal = np.frombuffer(sound.data, np.int16)
        fig.add_subplot(len(sounds), 1, i + 1)
        plt.plot(signal)
    plt.show()


def play_sound(sound):
    signal = np.frombuffer(sound.data, np.int16) / (2**15)
    import pdb; pdb.set_trace()
    sounddevice.play(signal, sound.parameters['frequency'])


def plot_animation(texture, points, triangles, animation):
    # Initialize visualization window
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name=animation.name, width=1920, height=1080, left=10, top=10)
    vis.get_render_option().point_size = 1.0
    vis.get_render_option().background_color = np.zeros(3)

    texture = convert_rgb555_to_rgb888(texture)

    # Get points, triangles, and bones of mesh
    vertex_coords = []
    faces = []
    uv_coords = []

    for pt in points:
        vertex_coords.append(pt.get_coords())

    for tri in triangles:
        faces.append(tri.get_points())
        uv_coords.append(tri.get_uv_coords())

    vertex_coords = np.array(vertex_coords)
    faces = np.array(faces)
    uv_coords = np.array(uv_coords)

    # normalize coordinates
    normalized_uv_coords = np.zeros((len(uv_coords), 3, 2), dtype=np.float32)
    normalized_uv_coords[..., 0] = uv_coords[..., 0] / texture.shape[0]
    normalized_uv_coords[..., 1] = uv_coords[..., 1] / texture.shape[1]
    normalized_uv_coords = normalized_uv_coords.reshape((-1, 2))

    # Define mesh and plot
    mesh = o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(vertex_coords),
                                     o3d.utility.Vector3iVector(faces))
    mesh.compute_vertex_normals()

    mesh.triangle_uvs = o3d.utility.Vector2dVector(normalized_uv_coords)
    mesh.textures = [o3d.geometry.Image(texture)]
    mesh.triangle_material_ids = o3d.utility.IntVector([0] * len(faces))

    vis.add_geometry(mesh)

    while True:
        for frame in animation.frames:
            new_vtx_coords = np.array(frame.pt_coords)
#            mesh = o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(new_vtx_coords),
#                                             o3d.utility.Vector3iVector(faces))
#            mesh.compute_vertex_normals()

#            mesh.triangle_uvs = o3d.utility.Vector2dVector(normalized_uv_coords)
#            mesh.textures = [o3d.geometry.Image(texture)]
#            mesh.triangle_material_ids = o3d.utility.IntVector([0] * len(faces))
            mesh.vertices = o3d.utility.Vector3dVector(new_vtx_coords)
            mesh.compute_vertex_normals()

    #        vis.update_geometry(mesh)
            vis.update_geometry(mesh)

            vis.poll_events()
            vis.update_renderer()
            vis.clear_geometries()

    vis.destroy_window()


if __name__ == "__main__":
    car_file_path = "./resources/Carnivores_2plus/HUNTDAT/CERATO1.CAR"
    with CarReader(car_file_path) as car_reader:
        header = car_reader.header
        triangles = car_reader.triangle_blocks
        points = car_reader.points_blocks
        texture = car_reader.texture
        animations = car_reader.animations
        sounds = car_reader.sounds
    import pdb; pdb.set_trace()

#    plot_texture(texture)
#    plot_point_cloud(points)
#    plot_tri_mesh(triangles, points)
    plot_carnivoresII_dino(texture, triangles, points)
#    plot_sounds(sounds)

    # select sound at random
#    import random
#    sound = random.choice(sounds)
#    play_sound(sound)

    # select animation at random
#    import random
#    animation = random.choice(animations)
#    plot_animation(texture, points, triangles, animation)
    
