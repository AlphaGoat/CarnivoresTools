#include <glad/glad.h>
#include <GLFW.glfw2.h>
#include <iostream>


void framebuffer_size_callback(GLFWwindow *window, int width, int height);

// Callback function to resize viewport when user resizes window
void framebuffer_size_callback(GLFWwindow *window, int width, int height) {
    glViewPort(0, 0, width, height);
}


int main() {
    glfwInit();
    glwfWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    GLFWindow *window = glfwCreateWindow(800, 600, "Carnivores III", NULL, NULL);
    if (window == NULL) {
        std::cout << "Failed to create GLFW window" << std::endl;
        glfwTerminate();
        return -1;
    }

    glfwMakeContextCurrent(window);

    if (!gladLoadGLLoader((GLADloadproc) glfwGetProcAddress)) {
        std::cout << "Failed to initialize GLAD" << std::endl;
    }

    glViewport(0, 0, 800, 600);

    // Render loop
    while (!glfwWindowShouldClose(window)) {

        glfwPollEvents();
        glfwSwapBuffers(window);
    }

    // Clean up GLFW resources
    glfwTerminate();

    return 0;
}
