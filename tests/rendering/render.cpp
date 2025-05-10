#include <GL/glew.h>
#include <GL/glut.h>
#include <Python.h>
#include <arrayobject.h>


/* Utility function for converting `PyObject` to PyArray */
PyArrayObject *PyObject_2_double_array(PyObject *objin) {
    return (PyArrayObject *) PyArray_ContiguousFromObject(objin, NPY_DOUBLE, 2, 2);
}

PyArrayObject *PyObject_2_uint8_array(PyObject *objin) {
    return (PyArrayObject *) PyArray_ContiguousFromObject(objin, NPY_UINT8, 2, 2);
}


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

static void render_mesh(struct dino_mesh const *mesh) {
    glBindTexture(GL_TEXTURE_2D, mesh->texture);
    glBindBuffer(GL_ARRAY_BUFFER, mesh->vertex_buffer);
    glVertexAttribPointer(
        g_resources.flag_program.attributes.position
        3, GL_FLOAT, GL_FALSE, sizeof(struct flag_vertex),
        (void*)offsetof(struct flag_vertex, position)
    );
    glVertexAttribPointer(
        g_resources.flag_program.attributes.normal,
        3, GL_FLOAT, GL_FALSE, sizeof(struct dino_vertex),
        (void*)offsetof(struct din_vertex, normal)
    );
    glVertexAttribPointer(
        g_resources.flag_program.attributes.texcoord,
        2, GL_FLOAT, GL_FALSE, sizeof(struct dino_vertex),
        (void*)offsetof(struct flag_vertex, texcoord)
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


static void enact_flag_program(
    GLuint vertex_shader,
    GLuint fragment_shader,
    GLuint program
) {
    g_resources.dino_render_program.vertex_shader = vertex_shader;
    g_resources.dino_render_program.fragment_shader = fragment_shader;
    g_resources.dino_render_program.program = program;

    g_resources.dino_render_program.texture 
        = glGetUniformLocation(program, "texture");
    g_resources.dino_render_program.p_matrix 
        = glGetUniformLocation(program, "p_matrix");
    g_resources.dino_render_program.mv_matrix 
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
    *fragment_shader = make_shader(GL_FRAGMENT_SHADER, "flag.f.glsl");
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

    /* Initialize python interpreter and import our car file reader module */
    Py_Initialize();
    PyObject *module_name = PyUnicode_DecodeFSDefault("car_reader");
    PyObject *module = PyImport_Import(method_name);
    if (module == nullptr) {
        PyErr_Print();
        std::cerr << "Failed to import car_reader module";
        return -1;
    }
    // release reference to module name
    Py_DECREF(module_name);

    // Get __dict__ for module
    PyObject *dict = PyModule_GetDict(module);
    if (dict == nullptr) {
        PyErr_Print();
        std::cerr << "Failed to retrieve car_reader module dictionary.\n";
        return -1; 
    }
    Py_DECREF(module);

    // Build name of reader class
    PyObject *car_reader_name = PyDict_GetItemString(dict, "CARReaderWrapper");
    if (car_reader_name == nullptr) {
        PyErr_Print();
        std::cerr << "Failed to retrieve CARReaderWrapper object from car_reader module.\n";
        return -1;
    }
    Py_DECREF(dict);

    // Initialize instance of class
    if (PyCallable_Check(car_reader_name)) {
        PyObject *carpath = PyTuple(1, PyUnicode_FromString("/home/alphagoat/Projects/CarnivoresIII/resources/Carnivores_2plus/HUNTDAT/CERATO1.CAR"));
        PyObject *car_reader_object = PyObject_CallObject(car_reader_name, carpath);
        Py_DECREF(car_reader_name);
    } else {
        std::cout << "Failed to instantiate `CARReader` class." << std::endl;
        Py_DECREF(car_reader_name);
        return -1;
    }

    // huzzah, we now have an instance of the CarReader class, which means we can now
    // retrieve dino model vertices, faces, and textures. Wow.

    // Initialize Glut resources
    GLuint vertex_shader, fragment_shader, program;

    // Retrieve vertices, faces, and textures and store in program resources struct
    PyObject *vertex_obj = PyObject_CallMethodObjArgs(car_reader_object, "get_vertices", nullptr);
    PyArrayObject *vertex_array = PyObject_2_double_array(vertex_obj);
    Py_DECREF(vertex_obj);

    PyObject *triangles_obj = PyObject_CallMethodObjArgs(car_reader_object, "get_triangles", nullptr);
    PyArrayObject *triangles_array = PyObject_2_uint8_array(triangles_obj);
    Py_DECREF(triangles_obj);

    PyObject *uv_coord_obj = PyObject_CallMethodObjArgs(car_reader_object, "get_uv_coords", nullptr);
    PyArrayObject *uv_coord_array = PyObject_2_uint8_array(uv_coord_obj);
    Py_DECREF(uv_coord_obj);

    read_nparray_into_cstyle_array();



}


static void update(void) {
    int milliseconds = glutGet(GLUT_ELPASED_TIME);
    GLfloat seconds = (GLfloat)milliseconds * (1.0f/1000.0f);
    update_dino_mesh(&g_resources.dino, g_resources.dino_vretex_array, seconds);
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
        update_flag_program();
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

static void init_gl_state(void) {
    glEnable(GL_DEPTH_TEST);

    /* Discard back facing triangles to avoid 
     * overdrawing */
    glEnable(GL_CULL_FACE);
}

static void render(void) {
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    glUseProgram(g_resources.dino_render_program.program);

    glActiveTexture(GL_TEXTURE0);
    glUniform1i(g_resources.dino_render_program.uniforms.texture, 0);

    glUniformMatrix4fv(
        g_resources.flag_program.uniforms.p_matrix,
        1, GL_FALSE,
        g_resources.p_matrix
    );

    glUniformMatrix4fv(
        g_resources.dino_render_program.mv_matrix,
        1, GL_FALSE,
        g_resources.mv_matrix
    );

    glEnableVertexAttribArray(g_resources.dino_render_program.attributes.position);
    glEnableVertexAttribArray(g_resources.dino_render_program.attributes.normal);
    glEnableVertexAttribArray(g_resources.dino_render_program.attributes.texcoord);

    render_mesh(&g_resources.dino);

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
    glutIdleFunc(&update);
    glutDisplayFunc(&render);
    glurReshapeFunc(&reshape);
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
