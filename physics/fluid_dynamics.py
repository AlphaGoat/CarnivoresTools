import numpy as np
from typing import Tuple
from pydantic import confloat
from numpy.typing import NDArray


def generate_wind_field(altitude_map: NDArray[np.uint16]):
    pass


def generate_perlin_noise_2d(
    map_shape: Tuple[int, int],
    num_seed_points: Tuple[int, int]=(8, 8),
    dampen_factor: confloat(ge=0.0, le=1.0)=1.0,
    num_iter: int=100,
) -> NDArray[np.float32]:
    """
    2-D perlin noise that only takes into account the 
    (x, y) coordinates of the map
    """
    # Define the fade function and the joint fade function,
    # which is simply the product of the fade function along
    # the x and y axis
    def fade_function(t):
        return 6 * t**5 - 15 * t**4 + 10 * t**3

    joint_fade_fn = lambda y, x: fade_function(y) * fade_function(x)

    # Get coordinate mesh
    x = np.arange(map_shape[1])
    y = np.arange(map_shape[0])

    Y, X = np.meshgrid(y, x)

    # Generate random gradients for each point in grid
    rand_grads = np.random.randint(low=0, high=100, 
            size=(num_seed_points[0], num_seed_points[1], 2))

    # Have values wrap around
    rand_grads[:, 0, :] = rand_grads[:, num_seed_points[1] - 1, :]
    rand_grads[0, :, :] = rand_grads[num_seed_points[0] - 1, :, :]

    # Divide coordinates by the number of seed points
    # along each axis
    norm_Y = Y / num_seed_points[0]
    norm_X = X / num_seed_points[1]

    # Get corner points of square containing each point
    x0 = np.floor(norm_X)
    y0 = np.floor(norm_Y)
    x1 = np.mod(x0 + 1, num_seed_points[1])
    y1 = np.mod(y0 + 1, num_seed_points[0])

    # Convert into indices for corner points
    indices_00 = np.stack([y0.astype(np.int32),
                           x0.astype(np.int32)],
                           axis=-1)
    indices_01 = np.stack([y0.astype(np.int32),
                           x1.astype(np.int32)],
                           axis=-1)
    indices_10 = np.stack([y1.astype(np.int32),
                           x0.astype(np.int32)],
                           axis=-1)
    indices_11 = np.stack([y1.astype(np.int32),
                           x1.astype(np.int32)],
                           axis=-1)

    # Get vectors from corner to point (x, y)
    v_00 = np.stack([norm_Y - y0, norm_X - x0], axis=-1)
    v_10 = np.stack([norm_Y - y1, norm_X - x0], axis=-1)
    v_01 = np.stack([norm_Y - y0, norm_X - x1], axis=-1)
    v_11 = np.stack([norm_Y - y1, norm_X - x1], axis=-1)

    # Get scalar displacement values
    import pdb; pdb.set_trace()
    delta_00 = np.dot(v_00, np.take(rand_grads, indices_00))
    delta_01 = np.dot(v_01, np.take(rand_grads, indices_01))
    delta_10 = np.dot(v_10, np.take(rand_grads, indices_10))
    delta_11 = np.dot(v_11, np.take(rand_grads, indices_11))

    # Define the noise function for each point (y, x)
    def noise(y, x):
        out =  joint_fade_fn(1 - y, 1 - x) * delta_00
        out += joint_fade_fn(y, 1 - x) * delta_10
        out += joint_fade_fn(1 - y, x) * delta_01
        out += joint_fade_fn(y, x) * delta_11
        return out

    vector_field = np.sum([dampen_factor**i * noise(y, x) for i in num_iter])

    return vector_field





def generate_curl_noise(altitude_map: NDArray[np.uint16]):
    pass


def curl_noise(
    x: float,
    y: float, 
    z: float,
    eps: float=1e-3,
) -> float:
#    dpdx0 = snoise()
    pass


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    def plot_vector_field(vector_field):
        # Get coordinates
        fig = plt.figure()
        ax = plt.subplot(1, 1, 1)
        y = np.arange(vector_field.shape[0])
        x = np.arange(vector_field.shape[1])
        Y, X = np.meshgrid(y, x)

        U = vector_field[..., 0]
        V = vector_field[..., 1]

        ax.quiver(X, Y, U, V)
        ax.suptitle("Perlin Noise")
        plt.show()

    
    vector_field = generate_perlin_noise_2d((1024, 1024),
                                            num_seed_points=(8, 8),
                                            dampen_factor=1.0,
                                            num_iter=100)
    plot_vector_field(vector_field)

