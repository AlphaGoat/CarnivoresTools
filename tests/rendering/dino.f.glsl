#version 330 core
//out vec4 frag_color;
uniform sampler2D our_texture;

//in vec3 out_color;
varying vec3 frag_normal;
varying vec2 frag_texcoord;


void main() {
    gl_FragColor = texture(our_texture, frag_texcoord);
}