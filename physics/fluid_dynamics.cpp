#include <math.h>
#include <stdexcept>

typedef enum {
    BOTTOM_LEFT, TOP_LEFT, BOTTOM_RIGHT, TOP_RIGHT
} corner;


double fade_function(double t) {
    return 6 * pow(t, 5) - 15 * pow(t, 4) + 10 * pow(t, 3);
}


double joint_fade_function(double x, double y) {
    return fade_function(x) * fade_function(y);
}


float lerp(float t, float a1, float a2) {
    return a1 * t * (a2 - a1);
}


int ***init_coord_grid(int grid_height, int grid_width) {
    /* Initialize a coordinate grid of NxMx2, where N is the grid height
       and M is grid width*/

    /* Allocate memory for grid */
    int ***coord_grid = (int ***) calloc(grid_height, grid_width * 2 * sizeof(int));
    for (int i = 0; i < grid_height; i++) {
        coord_grid[i] = (int **) calloc(grid_width, 2 * sizeof(int));
        for (int j = 0; j < grid_width; j++) {
            coord_grid[i][j] = (int *) calloc(2, sizeof(int));
        }
    }

    /* Fill in coordinate values */
    for (int i = 0; i < grid_height; i++) {
        for (int j = 0; j < grid_width; j++) {
            coord_grid[i][j][0] = i;
            coord_grid[i][j][1] = j;
        }
    }

    return coord_grid;
}

float ***generate_random_gradients(int num_seed_pts_y, int num_seed_pts_x) {
    /* Generate a 2-d grid of random gradients */

    /* Allocate space for 2-D grid of gradient vectors */
    float ***rand_grads = (float ***) calloc(num_seed_pts_y + 1, (num_seed_pts_x + 1) * 2 * sizeof(float));
    for (int i = 0; i < num_seed_pts_y + 1; i++) {
        rand_grads[i] = (float **) calloc(num_seed_pts_x + 1, 2 * sizeof(float));
        for (int j = 0; j < num_seed_pts_x + 1; j++) {
            rand_grads[i][j] = (float *) calloc(2, sizeof(float));
        }
    }
    fprintf(stderr, "Memory for random gradients allocated.\n");

    /* lambda function for generating random values between [-1., 1.]*/
    auto rand_val = []() {
        return ((float) rand() / (float)(RAND_MAX / 2.0)) -1.;
    };

    /* Lambda function for calculating norm of a vector */
    auto l2_norm = [](float *vector) {
        return sqrt(pow(vector[0], 2.) + pow(vector[1], 2.));
    };

    for (int i = 0; i < num_seed_pts_y; i++) {
        for (int j = 0; j < num_seed_pts_x; j++) {
            /* Get random gradient vector */
            float grad_vector[2];
            grad_vector[0] = rand_val();
            grad_vector[1] = rand_val();

            /* normalize gradient vector */
            float norm = l2_norm(grad_vector);

            rand_grads[i][j][0] = grad_vector[0] / norm;
            rand_grads[i][j][1] = grad_vector[1] / norm;
        }
    }

    return rand_grads;
}


void calc_displacement_vector(
    float *disp_vector, int x, int y, int grid_height, int grid_width, int num_seed_pts_y, int num_seed_pts_x, corner c_
) {
    /* Calculate the displacement vector between a corner and given (y,x) coordinate */
    switch (c_) {
        case BOTTOM_LEFT: {
            float x0 = floor((float) x / (float) num_seed_pts_x) * (float) grid_width;
            float y0 = floor((float) y / (float) num_seed_pts_y) * (float) grid_height;
            disp_vector[0] = (float) y - y0;
            disp_vector[1] = (float) x - x0;
            break;
        }

        case BOTTOM_RIGHT: {
            float x1 = ceil((float) x / (float) num_seed_pts_x) * (float) grid_width;
            float y0 = floor((float) y / (float) num_seed_pts_y) * (float) grid_height;
            disp_vector[0] = (float) y - y0;
            disp_vector[1] = (float) x - x1;
            break;
        }

        case TOP_LEFT: {
            float x0 = floor((float) x / (float) num_seed_pts_x) * (float) grid_width;
            float y1 = ceil((float) y / (float) num_seed_pts_y) * (float) grid_height;
            disp_vector[0] = (float) y - y1;
            disp_vector[1] = (float) x - x0;
            break;
        }

        case TOP_RIGHT: {
            float x1 = ceil((float) x / (float) num_seed_pts_x) * (float) grid_width;
            float y1 = ceil((float) y / (float) num_seed_pts_y) * (float) grid_height;
            disp_vector[0] = (float) y - y1;
            disp_vector[1] = (float) x - x1;
            break;
        }

        default:
            throw std::runtime_error("Invalid enum flag.");
    }

}


float **perlin(int grid_height, int grid_width, int num_seed_pts_y, int num_seed_pts_x) {
    // Initialize coordinate grid
    fprintf(stderr, "Making perlin noise.\n");
    int ***coord_grid = init_coord_grid(grid_height, grid_width);
    fprintf(stderr, "Coordinate grid allocated.\n");

    // Generate random gradients for each of the seed points
    float ***rand_grads = generate_random_gradients(num_seed_pts_y, num_seed_pts_x);
    fprintf(stderr, "Random gradients.\n");

    /* Lambda function for calculating dot product between gradient and displacement vectors */
    auto dot_product = [](float *v1, float *v2) {
        return v1[0] * v2[0] + v1[1] * v2[1];
    };

    // Calculate displacement vectors between each coordinate and the four closest seed points

    float **perlin_noise_matrix = (float**) calloc(grid_height, grid_width * sizeof(float));
    for (int i = 0; i < grid_height; i++) {
        perlin_noise_matrix[i] = (float*) calloc(grid_width, sizeof(float));
        for (int j = 0; j < grid_width; j++) {
            int y = coord_grid[i][j][0];
            int x = coord_grid[i][j][1];

            float disp00[2];
            float disp01[2];
            float disp10[2];
            float disp11[2];

            calc_displacement_vector(disp00, x, y, grid_height, 
                    grid_width, num_seed_pts_y, num_seed_pts_x, BOTTOM_LEFT);
            calc_displacement_vector(disp01, x, y, grid_height, 
                    grid_width, num_seed_pts_y, num_seed_pts_x, BOTTOM_RIGHT);
            calc_displacement_vector(disp10, x, y, grid_height, 
                    grid_width, num_seed_pts_y, num_seed_pts_x, TOP_LEFT);
            calc_displacement_vector(disp11, x, y, grid_height, 
                    grid_width, num_seed_pts_y, num_seed_pts_x, TOP_RIGHT);

            int x0 = (int) (floor((float) x / (float) num_seed_pts_x));
            int x1 = (int) (ceil((float) x / (float) num_seed_pts_x));
            int y0 = (int) (floor((float) y / (float) num_seed_pts_y));
            int y1 = (int) (ceil((float) y / (float) num_seed_pts_y));

            fprintf(stderr, "x0:%d\n", x0);
            fprintf(stderr, "y0:%d\n", y0);
            fprintf(stderr, "x1:%d\n", x1);
            fprintf(stderr, "y1:%d\n", y1);

            /* Take dot product between displacement vectors and appropriate gradient vector */  
            float *grad00 = rand_grads[y0][x0];
            float dot00 = dot_product(grad00, disp00);

            float *grad01 = rand_grads[y0][x1];
            float dot01 = dot_product(grad01, disp01);

            float *grad10 = rand_grads[y1][x0];
            float dot10 = dot_product(grad10, disp10);

            float *grad11 = rand_grads[y1][x1];
            float dot11 = dot_product(grad11, disp11);

            float xf = x - floor(x);
            float yf = y - floor(y);

            float u = fade_function(xf);
            float v = fade_function(yf);

            perlin_noise_matrix[i][j] = lerp(u,
                    lerp(v, dot00, dot10),
                    lerp(v, dot01, dot11)
            );
        }
    }

    /* Free grid and vector matrices */
    free(coord_grid);
    free(rand_grads);

    /* Return perlin noise matrix */
    return perlin_noise_matrix;
}