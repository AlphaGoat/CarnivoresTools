/* Structures for holding mesh objects */
struct object_mesh {
    GLuint vertex_buffer, element_buffer;
    GLsizei element_count;
    GLuint texture;
}

struct object_vertex {
    GLfloat position[4];
    GLfloat normal[4];
    GLfloat texcoord[2];
    GLfloat shininess; // lighting attributes may be used later...
    GLubyte specular[4];
}
