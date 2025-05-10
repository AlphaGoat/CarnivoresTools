#version 330

uniform mat4 p_matrix, mv_matrix;

// Define attributes
attribute vec3 position, normal;
attribute vec2 texcoord;

void main() {
    vec4 eye_position = mv_matrix * vec4(position, 1.0);
    gl_Position = p_matrix * eye_position;
}
