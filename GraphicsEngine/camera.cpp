#include <cmath>
#include <SLD2/SDL.h>
#include <math.h>


float deg2rad(float deg) {
    return deg * M_PI / 2.;
}


Matrix absolute_to_relative(
    int x_cam, 
    int y_cam, 
    int z_cam, 
    float inclination, 
    float azimuth
) {
    Matrix A({
       {1., 0., 0., x_cam},
       {0., 1., 0., y_cam},
       {0., 0., 1., z_cam},
       {0., 0., 0., 0.}
    });

    Matrix B({
        {cos(-azimuth), -sin(-azimuth), 0., 0.},
        {sin(-azimuth), cos(-azimuth), 0., 0.},
        {0., 0., 1., 0.},
        {0., 0., 0., 0.}
    });

    Matrix C({
        {cos(-inclination), 0., -sin(-inclination), 0.},
        {0., 1., 0., 0.},
        {sin(-inclination), 0., cos(-inclination), 0.},
        {0., 0., 0., 0.}
    });

    Matrix D({
        {0., -1., 0., 0.},
        {-1., 0., 0., 0.},
        {0., 0., 1., 0.},
        {0., 0., 0., 0.}
    });

    relCoords = matmul(matmul(matmul(A, B), C), D);

    return relCoords;
}


Camera::Camera(int char_pos_x, int char_pos_y,
               int height, int width) {

    Camera::char_pos_x = char_pos_x;
    Camera::char_pos_y = char_pos_y;
    Camera::height = height;
    Camera::width = width;
}


void render_tile(int *x_pts,
                 int *y_pts,
                 int *z_pts) {

}
