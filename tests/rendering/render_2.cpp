#include <stdlib.h>
#include <GL/glew.h>
#include <GL/glut.h>
#include <math.h>
#include "lua-handler.h"
//#include "mesh.h"
#include "gl-util.h"
#include "lua.h"
#include "lualib.h"
#include "lauxlib.h"


/* Utility function for converting `PyObject` to PyArray */
//PyArrayObject *P<yObject_3_double_array(PyObject *objin) {
//    return (PyArrayObject *) PyArray_ContiguousFromObject(objin, NPY_DOUBLE, 2, 2);
//}
//
//PyArrayObject *PyObject_2_uint8_array(PyObject *objin) {
//    return (PyArrayObject *) PyArray_ContiguousFromObject(objin, NPY_UINT8, 2, 2);
//}


static struct {
    struct dino_mesh dino_model;
    struct dino_vertex *dino_vertex_array;

    struct {
        GLuint vertex_shader, fragment_shader, program;

        struct {
            GLint texture, p_matrix, mv_matrix;
        } uniforms;

        struct {
            GLint position, normal, texcoord;
        } attributes;
    } dino_render_program;

    GLfloat p_matrix[16], mv_matrix[16];
    GLfloat eye_offset[2];
    GLsizei window_size[2];
} g_resources;

static void init_gl_state(void) {
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_CULL_FACE);
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
}

#define PROJECTION_FOV_RATIO 0.7f
#define PROJECTION_NEAR_PLANE 0.0625f
#define PROJECTION_FAR_PLANE 256.0f

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

static void render_mesh(struct dino_mesh const *mesh) {
    glBindTexture(GL_TEXTURE_2D, mesh->texture);
    glBindBuffer(GL_ARRAY_BUFFER, mesh->vertex_buffer);
    glVertexAttribPointer(
        g_resources.dino_render_program.attributes.position,
        3, GL_FLOAT, GL_FALSE, sizeof(struct dino_vertex),
        (void*)offsetof(struct dino_vertex, position)
    );
    glVertexAttribPointer(
        g_resources.dino_render_program.attributes.normal,
        3, GL_FLOAT, GL_FALSE, sizeof(struct dino_vertex),
        (void*)offsetof(struct dino_vertex, normal)
    );
    glVertexAttribPointer(
        g_resources.dino_render_program.attributes.texcoord,
        2, GL_FLOAT, GL_FALSE, sizeof(struct dino_vertex),
        (void*)offsetof(struct dino_vertex, texcoord)
    );

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, mesh->element_buffer);
    glDrawElements(
        GL_TRIANGLES,
        mesh->element_count,
        GL_UNSIGNED_SHORT,
        (void*)0
    );
}

#define INITIAL_WINDOW_WIDTH 1098
#define INITIAL_WINDOW_HEIGHT 1020


static void enact_dino_render_program(
    GLuint vertex_shader,
    GLuint fragment_shader,
    GLuint program
) {
    g_resources.dino_render_program.vertex_shader = vertex_shader;
    g_resources.dino_render_program.fragment_shader = fragment_shader;
    g_resources.dino_render_program.program = program;

    g_resources.dino_render_program.uniforms.texture 
        = glGetUniformLocation(program, "texture");
    g_resources.dino_render_program.uniforms.p_matrix 
        = glGetUniformLocation(program, "p_matrix");
    g_resources.dino_render_program.uniforms.mv_matrix 
        = glGetUniformLocation(program, "mv_matrix");

    g_resources.dino_render_program.attributes.position 
        = glGetAttribLocation(program, "position");
    g_resources.dino_render_program.attributes.normal
        = glGetAttribLocation(program, "normal");
    g_resources.dino_render_program.attributes.texcoord
        = glGetAttribLocation(program, "texcoord");
}


static int make_dino_render_program(
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

static void delete_dino_render_program(void) {
    glDetachShader(
        g_resources.dino_render_program.program,
        g_resources.dino_render_program.vertex_shader
    );
    glDetachShader(
        g_resources.dino_render_program.program,
        g_resources.dino_render_program.fragment_shader
    );
    glDeleteProgram(g_resources.dino_render_program.program);
    glDeleteProgram(g_resources.dino_render_program.vertex_shader);
    glDeleteProgram(g_resources.dino_render_program.fragment_shader);
}

static void update_dino_render_program(void) {
    printf("reloading program\n");
    GLuint vertex_shader, fragment_shader, program;

    if (make_dino_render_program(&vertex_shader, &fragment_shader, &program)) {
        delete_dino_render_program();
        enact_dino_render_program(vertex_shader, fragment_shader, program);
    }
}


static int make_resources(void) {
    GLuint vertex_shader, fragment_shader, program;

    const char *filepath = "/home/alphagoat/Projects/CarnivoresIII/resources/Carnivores_2plus/HUNTDAT/CERATO1.CAR";
    car_resources *dino_resources = (car_resources*) malloc(sizeof(struct car_resources));

    /* Read CAR file and fill out vertex and mesh information */
    if (!fetch_car_file_assets(filepath, dino_resources)) {
        fprintf(stderr, "Failed to fetch resources from car file.\n");
        return 0;
    }

    g_resources.dino_model = dino_resources->dino_model;
    g_resources.dino_vertex_array = dino_resources->dino_vertex_array;
//    g_resources.texture = dino_resources->texture;

//    if (g_resources.texture == 0)
//        return 0;

    if (!make_dino_render_program(&vertex_shader, &fragment_shader, &program))
        return 0;

    enact_dino_render_program(vertex_shader, fragment_shader, program);

    g_resources.eye_offset[0] = 0.0f;
    g_resources.eye_offset[1] = 0.0f;
    g_resources.window_size[0] = INITIAL_WINDOW_WIDTH;
    g_resources.window_size[1] = INITIAL_WINDOW_HEIGHT;

    // update_p_matrix
    // update_mv_matrix
//    free(dino_resources);
    
    return 1;

}



void init_mesh(
    struct dino_mesh *out_mesh,
    struct dino_vertex const *vertex_data, GLsizei vertex_count,
    GLushort const *element_data, GLsizei element_count,
    GLenum hint
) {
    glGenBuffers(1, &out_mesh->vertex_buffer);
    glGenBuffers(1, &out_mesh->element_buffer);
    out_mesh->element_count = element_count;

    glBindBuffer(GL_ARRAY_BUFFER, out_mesh->vertex_buffer);
    glBufferData(
        GL_ARRAY_BUFFER,
        vertex_count * sizeof(struct dino_vertex),
        vertex_data,
        hint
    );

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, out_mesh->element_buffer);
    glBufferData(
        GL_ELEMENT_ARRAY_BUFFER,
        element_count * sizeof(GLushort),
        element_data,
        GL_STATIC_DRAW
    );
}


static void update(void) {
    int milliseconds = glutGet(GLUT_ELAPSED_TIME);
    GLfloat seconds = (GLfloat)milliseconds * (1.0f/1000.0f);
//    TODO: add update function when implementing animations
//    update_dino_mesh(&g_resources.dino, g_resources.dino_vertex_array, seconds);
    glutPostRedisplay();
}


/* Function to allow us to move the view when dragging
 * the mouse */
static void drag(int x, int y) {
    float w = (float)g_resources.window_size[0];
    float h = (float)g_resources.window_size[1];
    g_resources.eye_offset[0] = (float)x/w - 0.5;
    g_resources.eye_offset[1] = -(float)y/h + 0.5;
    update_mv_matrix(g_resources.mv_matrix, g_resources.eye_offset);
}


/* Function to snap view back in place when mouse
 * button is released */
static void mouse(int button, int state, int x, int y) {
    if (button == GLUT_LEFT_BUTTON && state == GLUT_UP) {
        g_resources.eye_offset[0] = 0.0f;
        g_resources.eye_offset[1] = 0.0f;
        update_mv_matrix(g_resources.mv_matrix, g_resources.eye_offset);
    }
}


/* Reload GLSL program by pressing 'R' */
static void keyboard(unsigned char key, int x, int y) {
    if (key == 'r' || key == 'R') {
        update_dino_render_program();
    }
}


/* Function to preserve the aspect ratio
 * of textures in window when window is resized */
static void reshape(int w, int h) {
    g_resources.window_size[0] = w;
    g_resources.window_size[1] = h;
    update_p_matrix(g_resources.p_matrix, w, h);
    glViewport(0, 0, w, h);
}

//static void init_gl_state(void) {
//    glEnable(GL_DEPTH_TEST);
//
//    /* Discard back facing triangles to avoid 
//     * overdrawing */
//    glEnable(GL_CULL_FACE);
//}

static void render(void) {
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    glUseProgram(g_resources.dino_render_program.program);

    glActiveTexture(GL_TEXTURE0);
    glUniform1i(g_resources.dino_render_program.uniforms.texture, 0);

    glUniformMatrix4fv(
        g_resources.dino_render_program.uniforms.p_matrix,
        1, GL_FALSE,
        g_resources.p_matrix
    );

    glUniformMatrix4fv(
        g_resources.dino_render_program.uniforms.mv_matrix,
        1, GL_FALSE,
        g_resources.mv_matrix
    );

    glEnableVertexAttribArray(g_resources.dino_render_program.attributes.position);
    glEnableVertexAttribArray(g_resources.dino_render_program.attributes.normal);
    glEnableVertexAttribArray(g_resources.dino_render_program.attributes.texcoord);

    render_mesh(&g_resources.dino_model);

    glDisableVertexAttribArray(g_resources.dino_render_program.attributes.position);
    glDisableVertexAttribArray(g_resources.dino_render_program.attributes.normal);
    glDisableVertexAttribArray(g_resources.dino_render_program.attributes.texcoord);
    glutSwapBuffers();
}


int main(int argc, char* argv[]) {

    /* opengl initialization */
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_RGB | GLUT_DEPTH | GLUT_DOUBLE);
    glutInitWindowSize(INITIAL_WINDOW_WIDTH, INITIAL_WINDOW_HEIGHT);
    glutCreateWindow("Dino Runner");
//    glutIdleFunc(&update);
    glutDisplayFunc(&render);
    glutReshapeFunc(&reshape);
    glutMotionFunc(&drag);
    glutMouseFunc(&mouse);
    glutKeyboardFunc(&keyboard);

    glewInit();
    if (!GLEW_VERSION_2_0) {
        fprintf(stderr, "OpenGL 2.0 not available\n");
        return 1;
    }

    init_gl_state();
    if (!make_resources()) {
        fprintf(stderr, "Failed to load resources\n");
        return 1;
    }

    glutMainLoop();
    return 0;
}
