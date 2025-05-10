#include <GL/glew.h>

void init_mesh(
    struct dino_mesh *out_mesh,
    struct dino_vertex const *vertex_data, GLsizei num_vertices,
    GLushort const *element_data, GLsizei num_elements,
    GLenum hint
) {
    glGenBuffers(1, &out_mesh->vertex_buffer);
    glGenBuffers(1, &out_mesh->element_buffer);
    out_mesh->element_count = element_count;

    /* Bind vertex array to buffer */
    glBindBuffer(GL_ARRAY_BUFFER, out_mesh->vertex_bufffer);
    glBufferData(
        GL_ARRAY_BUFFER,
        num_vertices * sizeof(struct dino_vertex),
        vertex_data,
        hint
    );

    /* Bind element array to buffer */
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, out_mesh->element_buffer);
    glBufferData(
        GL_ELEMENT_ARRAY_BUFFER,
        num_elements * sizeof(GLushort),
        element_data,
        GL_STATIC_DRAW
    );
}

