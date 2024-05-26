"""
Main game loop

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

