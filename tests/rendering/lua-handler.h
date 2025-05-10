struct dino_mesh {
    GLuint vertex_buffer;
    GLuint element_buffer;
    GLsizei element_count;
    GLuint texture;
};

struct dino_vertex {
    GLfloat position[4];
    GLfloat normal[4];
    GLfloat texcoord[2];
    GLfloat shininess;
    GLubyte specular[4];
};

struct car_resources {
    struct dino_mesh dino_model;
    struct dino_vertex *dino_vertex_array;
    GLuint *texture;
};

int fetch_car_file_assets(const char *filepath, struct car_resources *resources);
