#include <SLD2/SDL.h>
#include <math.h>


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
