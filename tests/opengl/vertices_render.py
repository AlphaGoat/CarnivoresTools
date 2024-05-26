import moderngl

context = moderngl.create_context(standalone=True)

with open("vertex_shader.gl", "r") as f:
    vertex_shader_string = f.read()

with open("fragment_shader.gl", "r") as f:
    fragment_shader_string = f.read()

program = context.program(
    vertex_shaders=vertex_shader_string,
    fragment_shader=fragment_shader_string,
)

# buffer: dedicated area of GPU memory
