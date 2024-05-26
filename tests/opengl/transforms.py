"""
Testing ModernGL transforms

Author: Peter Thomas
Date: 19 May 2024
"""
import struct
import moderngl

def main():
    # Create OpenGL context
    context = moderngl.create_context(standalone=True)

    program = context.program(
        vertex_shader="""
        #version 330

        // Output values for the shader. They end up in the buffer.
        out float value;
        out float product;

        void main() {
            // Implicit type conversion from int to float will happen here
            value = gl_VertexID;
            product = gl_VertexID * gl_VertexID;
        }
        """,
        # What out varyings to capture in our buffer!
        varyings=["value", "product"],
    )

    NUM_VERTICES = 10

    vao = context.vertex_array(program, [])

    # 20x32-bit floats
    # Num of vertices * num of varying per vertex (2) * size of float in bytes (4)
    buffer = context.buffer(reserve=NUM_VERTICES * 2 * 4)

    # Start a transform with buffer as the destination
    # We force the vertex shader to run 10 times
    vao.transform(buffer, vertices=NUM_VERTICES)

    data = struct.unpack("20f", buffer.read())
    for i in range(0, 20, 2):
        print("value = {}, product = {}".format(*data[i:i+2]))

if __name__ == "__main__":
    main()
