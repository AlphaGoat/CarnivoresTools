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

void init_mesh(
    struct dino_mesh *out_mesh,
    struct dino_vertex const *vertex_data, 
    GLsizei vertex_count,
    GLushort const *element_data, 
    GLsizei element_count,
    GLenum hint
);
struct dino_vertex *init_dino_mesh(struct dino_mesh *out_mesh);
void init_background_mesh(struct dino_mesh *out_mesh);
void update_dino_mesh(
    struct dino_mesh const *mesh,
    struct dino_vertex *vertex_data,
    GLfloat time
);
