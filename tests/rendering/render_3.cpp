include "include/glad/glad.h"
#include <GLFW/glfw3.h>
//#include <GLES2/gl2.h>
#include <EGL/egl.h>
#include <stddef.h>
#include <math.h>
#include <stdio.h>
#include "lua-handler.h"
#include "file-util.h"
#include "gl-util.h"

#include <string>
#include <iostream>

#define PROJECTION_FOV_RATIO 0.7f
#define PROJECTION_NEAR_PLANE 0.0625f
#define PROJECTION_FAR_PLANE 256.0f

#define INITIAL_WINDOW_WIDTH 800
#define INITIAL_WINDOW_HEIGHT 600


void error_callback(int error, const char *msg) {
    std::string s;
    s = " [" + std::to_string(error) + "] " + msg + '\n';
    std::cerr << s << std::endl;
}

void error_loop() {
    GLenum err;
    while (( err = glGetError() ) != GL_NO_ERROR ) {
        std::cerr << err << std::endl;
    }
}


//void GLAPIENTRY GLErrorMessageCallback(
//    GLenum source,
//    GLenum type, 
//    GLuint id,
//    GLenum severity,
//    GLsizei length,
//    const GLchar *message,
//    const void *userParam
//) {
//    fprintf(stderr, "GL CALLBACK: %s type = 0x%x, severity = 0x%x, message = %s\n",
//        ( type == GL_DEBUG_TYPE_ERROR ? "** GL ERROR **" : ""),
//        type, severity, message);
//}


static struct {
    struct dino_mesh dino;
    struct dino_vertex *dino_vertex_array;

    struct {
        GLuint vertex_shader, fragment_shader, program;

        struct {
            GLint texture, p_matrix, mv_matrix; // Location flags for uniforms
        } uniforms;

        struct {
            GLuint position, normal, texcoord; // Location flags for attributes
        } attributes;
    } dino_program;

    GLfloat p_matrix[16], mv_matrix[16];
    GLfloat eye_offset[2];
    GLsizei window_size[2];
} g_resources;

static void update_p_matrix(GLfloat *matrix, int w, int h) {
    GLfloat wf = (GLfloat) w, hf = (GLfloat) h;
    GLfloat 
        r_xy_factor = fminf(wf, hf) * 1.0f/PROJECTION_FOV_RATIO,
        r_x = r_xy_factor/wf,
        r_y = r_xy_factor/hf,
        r_zw_factor = 1.0f/(PROJECTION_FAR_PLANE - PROJECTION_NEAR_PLANE),
        r_z = (PROJECTION_NEAR_PLANE + PROJECTION_FAR_PLANE) * r_zw_factor,
        r_w = -2.0f*PROJECTION_NEAR_PLANE*PROJECTION_FAR_PLANE*r_zw_factor;

    matrix[ 0] = r_x;  matrix[ 1] = 0.0f; matrix[ 2] = 0.0f; matrix[ 3] = 0.0f;
    matrix[ 4] = 0.0f; matrix[ 5] = r_y;  matrix[ 6] = 0.0f; matrix[ 7] = 0.0f;
    matrix[ 8] = 0.0f; matrix[ 9] = 0.0f; matrix[10] = r_z;  matrix[11] = 1.0f;
    matrix[12] = 0.0f; matrix[13] = 0.0f; matrix[14] = r_w;  matrix[15] = 0.0f;
}

static void update_mv_matrix(GLfloat *matrix, GLfloat *eye_offset) {
    static const GLfloat BASE_EYE_POSITION[3] = { 0.5f, -0.25f, -1.25f };

    matrix[ 0] = 1.0f; matrix[ 1] = 0.0f; matrix[ 2] = 0.0f; matrix[ 3] = 0.0f;
    matrix[ 4] = 0.0f; matrix[ 5] = 1.0f; matrix[ 6] = 0.0f; matrix[ 7] = 0.0f;
    matrix[ 8] = 0.0f; matrix[ 9] = 0.0f; matrix[10] = 1.0f; matrix[11] = 0.0f;
    matrix[12] = -BASE_EYE_POSITION[0] - eye_offset[0];
    matrix[13] = -BASE_EYE_POSITION[1] - eye_offset[1];
    matrix[14] = -BASE_EYE_POSITION[2];
    matrix[15] = 1.0f;
}


void framebuffer_size_callback(GLFWwindow *window, int width, int height) {
    glViewport(0, 0, width, height);
}


//static void update(void) {
//    int milliseconds = glutGet(GLUT_ELAPSED_TIME);
//    GLfloat seconds = (GLfloat)milliseconds * (1.0f/1000.0f);
//
//    update_dino_mesh
//}


//static void drag(int x, int y) {
//    float w = (float)g_resources.window_size[0];
//    float h = (float)g_resources.window_size[1];
//    g_resources.eye_offset[0] = (float)x/w - 0.5f;
//    g_resources.eye_offset[1] = (float)x/h + 0.5f;
//    update_mv_matrix(g_resources.mv_matrix, g_resources.eye_offset);
//}


void process_input(GLFWwindow *window) {
//    fprintf(stderr, "processing inputs\n");
    if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
        glfwSetWindowShouldClose(window, true);
    }
}


int bind_vertex_buffers(struct dino_vertex *vertex_array, int num_vertices) {
    // Generate vertex buffer
    unsigned int VBO;
    glGenBuffers(1, &VBO);
    glBindBuffer(GL_ARRAY_BUFFER, VBO);
    glBufferData(GL_ARRAY_BUFFER, num_vertices * 3, vertex_array->position, GL_STATIC_DRAW);
    return 0;
}


static void render_mesh(struct dino_mesh const *mesh) {
    glBindTexture(GL_TEXTURE_2D, mesh->texture);
    fprintf(stderr, "bind texture.\n");
    error_loop();

    glBindBuffer(GL_ARRAY_BUFFER, mesh->vertex_buffer);
//    glBufferData(GL_ARRAY_BUFFER, sizeof(vertex_array), vertex_array, GL_STATIC_DRAW);
    fprintf(stderr, "vertex buffer bound.\n");
    fprintf(stderr, "ARRAY BUFFER object: %d\n", mesh->vertex_buffer);
    error_loop();
    glVertexAttribPointer(
        g_resources.dino_program.attributes.position,
        3, GL_FLOAT, GL_FALSE, sizeof(struct dino_vertex),
        (void*)offsetof(struct dino_vertex, position)
    );
    fprintf(stderr, "Assign position pointer.\n");
    error_loop();
//    glVertexAttribPointer(
//        g_resources.dino_program.attributes.normal,
//        3, GL_FLOAT, GL_FALSE, sizeof(struct dino_vertex),
//        (void*)offsetof(struct dino_vertex, normal)
//    );
    glVertexAttribPointer(
        g_resources.dino_program.attributes.texcoord,
        2, GL_FLOAT, GL_FALSE, sizeof(struct dino_vertex),
        (void*)offsetof(struct dino_vertex, texcoord)
    );
    fprintf(stderr, "Assign texcoord pointer.\n");
    error_loop();
    fprintf(stderr, "bind vertex buffer.\n");
    error_loop();

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, mesh->element_buffer);
    fprintf(stderr, "bind elememnt buffer.\n");
    error_loop();
    glDrawElements(
        GL_TRIANGLES,
        mesh->element_count,
        GL_UNSIGNED_SHORT,
        (void*)0
    );
    fprintf(stderr, "draw elements.\n");
    error_loop();
}


static void render(GLFWwindow *window) {
//    fprintf(stderr, "Rendering mesh.\n");
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glUseProgram(g_resources.dino_program.program);
    fprintf(stderr, "Using program.\n");
    error_loop();
    
    glActiveTexture(GL_TEXTURE0);
    fprintf(stderr, "Activating texture.\n");
    error_loop();
    glUniform1i(g_resources.dino_program.uniforms.texture, 0);

    glUniformMatrix4fv(
        g_resources.dino_program.uniforms.mv_matrix,
        1, GL_FALSE,
        g_resources.mv_matrix
    );
    fprintf(stderr, "After assigning matrix.\n");
    error_loop();

    glEnableVertexAttribArray(g_resources.dino_program.attributes.position);
    fprintf(stderr, "After enabling position vertex array.\n");
    error_loop();
//    glEnableVertexAttribArray(g_resources.dino_program.attributes.normal);
//    fprintf(stderr, "After enabling normal vertex array.\n");
//    fprintf(stderr, "GL_MAX_VERTEX_ATTRIBS: %d\n", GL_MAX_VERTEX_ATTRIBS);
//    fprintf(stderr, "normal index: %d\n", g_resources.dino_program.attributes.normal);
//    error_loop();
    glEnableVertexAttribArray(g_resources.dino_program.attributes.texcoord);
    fprintf(stderr, "After enabling texcoord vertex array.\n");
    fprintf(stderr, "texcoord index: %d\n", g_resources.dino_program.attributes.texcoord);
    error_loop();
    fprintf(stderr, "After enabling vertices.\n");
    error_loop();

    render_mesh(&g_resources.dino);
//    render_mesh(&g_resources.background);

    glDisableVertexAttribArray(g_resources.dino_program.attributes.position);
//    glDisableVertexAttribArray(g_resources.dino_program.attributes.normal);
    glDisableVertexAttribArray(g_resources.dino_program.attributes.texcoord);

//    glutSwapBuffers()
    glfwSwapBuffers(window);
}


static void enact_dino_render_program(
    GLuint vertex_shader,
    GLuint fragment_shader,
    GLuint program
) {
    g_resources.dino_program.vertex_shader = vertex_shader;
    g_resources.dino_program.fragment_shader = fragment_shader;

    g_resources.dino_program.program = program;

    g_resources.dino_program.uniforms.texture 
        = glGetUniformLocation(program, "our_texture");
    g_resources.dino_program.uniforms.p_matrix
        = glGetUniformLocation(program, "p_matrix");
    g_resources.dino_program.uniforms.mv_matrix
        = glGetUniformLocation(program, "mv_matrix");

    g_resources.dino_program.attributes.position 
        = glGetAttribLocation(program, "position");
//    g_resources.dino_program.attributes.normal
//        = glGetAttribLocation(program, "normal");
    g_resources.dino_program.attributes.texcoord
        = glGetAttribLocation(program, "texcoord");
//    g_resources.dino_program.attributes.shininess
//        = glGetAttribLocation(program, "shininess");
//    g_resources.dino_program.attributes.specular
//        = glGetAttribLocation(program, "specular");
}


static int make_dino_program(
    GLuint *vertex_shader,
    GLuint *fragment_shader,
    GLuint *program
) {
    *vertex_shader = make_shader(GL_VERTEX_SHADER, "dino.v.glsl");
    if (*vertex_shader == 0)
        return 0;
    *fragment_shader = make_shader(GL_FRAGMENT_SHADER, "dino.f.glsl");
    if (*fragment_shader == 0)
        return 0;

    *program = make_program(*vertex_shader, *fragment_shader);
    if (*program == 0)
        return 0;

    return 1;
}


static void delete_flag_program(void) {
    glDetachShader(
        g_resources.dino_program.program,
        g_resources.dino_program.vertex_shader
    );
    glDetachShader(
        g_resources.dino_program.program,
        g_resources.dino_program.fragment_shader
    );
    glDeleteProgram(g_resources.dino_program.program);
    glDeleteShader(g_resources.dino_program.vertex_shader);
    glDeleteShader(g_resources.dino_program.fragment_shader);
}


static int make_resources() {
    /* Retrieve resources from CAR file */
    GLuint vertex_shader, fragment_shader, program;

    const char *filepath = "../resources/Carnivores_Fallen_Kings_partial_beta_2.1.2/Carnivores_Fallen_Kings_partial_beta_2.1.2/-Game/HUNTDAT/ANIMALS/1PRIMARKIA/0COMMON/baryt.car";
//    car_resources dino_resources;
    car_resources *dino_resources = (car_resources *) malloc(sizeof(car_resources));

    // Fetch vertices, element array, and texture from car file
//    if (!fetch_car_file_assets(filepath, &dino_resources)) {
    if (!fetch_car_file_assets(filepath, dino_resources)) {
        fprintf(stderr, "Failed to fetch assets from %s\n.", filepath);
        return 0;
    }
    fprintf(stderr, "CAR assets retrieved. Making dino program...\n");

    if (!make_dino_program(&vertex_shader, &fragment_shader, &program))
        return 0;
    fprintf(stderr, "dino program initialized\n");

    enact_dino_render_program(vertex_shader, fragment_shader, program);

    g_resources.eye_offset[0] = 0.0f;
    g_resources.eye_offset[1] = 0.0f;
    g_resources.window_size[0] = INITIAL_WINDOW_WIDTH;
    g_resources.window_size[1] = INITIAL_WINDOW_HEIGHT;

    update_p_matrix(
        g_resources.p_matrix,
        INITIAL_WINDOW_WIDTH,
        INITIAL_WINDOW_HEIGHT
    );
    update_mv_matrix(g_resources.mv_matrix, g_resources.eye_offset);

    return 1;
}


int main() {
    fprintf(stderr, "Initializing GLFW.\n");
    glfwInit();
    glfwSetErrorCallback(error_callback);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    fprintf(stderr, "GLFW initialized.\n");

//    glEnable(GLFW_DEBUG_OUTPUT);

    GLFWwindow *window = glfwCreateWindow(800, 600, "LearnOpenGL", NULL, NULL);
    fprintf(stderr, "Window created.\n");
    if (window == NULL) {
        fprintf(stderr, "Failed to create GLFW window.\n");
        glfwTerminate();
        return 0;
    }
    glfwMakeContextCurrent(window);
//    glViewport(0, 0, 800, 600);

    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);

    // glad: load all OpenGL function pointers
    if (!gladLoadGLLoader((GLADloadproc) glfwGetProcAddress)) {
        fprintf(stderr, "Failed to initialize GLAD\n");
        return 0;
    }

    if (!make_resources()) {
        fprintf(stderr, "Failed to load resources\n");
        return 0;
    }
    fprintf(stderr, "Resources made.\n");
    error_loop();

    // Render loop
    while (!glfwWindowShouldClose(window)) {
        // Process inputs
        process_input(window);
        fprintf(stderr, "process input\n");
        error_loop();
        render(window);
        glfwPollEvents();
        fprintf(stderr, "At end of rendering loop.\n");
        error_loop();
        break;
    }

    // Clean and delete all GLFW resources
    glfwTerminate();
    return 1;
}
