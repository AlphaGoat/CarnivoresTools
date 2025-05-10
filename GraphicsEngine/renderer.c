#include <GL/glew.h>
#include <GL/glut.h>


/* Function to preserve the aspect ratio of 
 * textures when window is resized */
static void reshape(int w, int h) {
    g_resources.window_size[0] = w;
    g_resources.window_size[1] = h;
    glViewport(0, 0, w, h);
}



int initialize_viewport(int window_height, int window_width) {
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE);
    glutInitWindowSize(window_height, window_width);
    glutCreateWindow("Carnivores Renderer");
    glutIdleFunc(&update_timer);

}
