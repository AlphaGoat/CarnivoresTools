#include "matplotlibcpp.h"
#include <math.h>
#include <vector>
#include <algorithm>
#include "fluid_dynamics.h"


int main() {
    /* Retrieve perlin noise */
    int GRID_HEIGHT = 128;
    int GRID_WIDTH = 128;
    int NUM_SEED_PTS_Y = 8;
    int NUM_SEED_PTS_X = 8;
    float **perlin_noise_matrix = perlin(GRID_HEIGHT, GRID_WIDTH, NUM_SEED_PTS_Y, NUM_SEED_PTS_X);

    /* Initialize vectors with set magnitude and angles determined 
     * by perlin noise */
    std::vector<float> y;
    std::vector<float> x;

    for (int i = 0; i < GRID_HEIGHT; i++) {
        for (int j = 0; j < GRID_WIDTH; j++) {
            y.push_back(sin(perlin_noise_matrix[i][j]));
            x.push_back(cos(perlin_noise_matrix[i][j]));
        }
    }
    matplotlibcpp::plot(x, y);

    return 1;
}