from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import pygame as pg
import numpy as np

################################ Initialisation ###############################
pg.init()
pg.display.set_mode((640,480),pg.OPENGL|pg.DOUBLEBUF)
CLOCK = pg.time.Clock()

glClearColor(0,0.2,0.2,1)

################################ Shaders ######################################
vertex_src = """
#version 330 core
layout (location = 1) in vec3 aPos; // the position variable has attribute position 0
out vec4 vertexColor; // specify a color output to the fragment shader

void main()
{
    gl_Position = vec4(aPos, 1.0);
}


"""
fragment_src = """

#version 330 core
out vec4 Color;
uniform vec3 colorChange;
void main()
{
    Color = vec4(colorChange,1);
}  

"""
"""
    Compile the source code. In c++, each shader has to be compiled individually, linked etc.
    The compileProgram function takes care of this in python. Just provide source code and tell the program
    what sort of shader is being compiled.
"""
shader = compileProgram(compileShader(vertex_src,GL_VERTEX_SHADER),
                        compileShader(fragment_src,GL_FRAGMENT_SHADER))

"""
    The shaders have been compiled and linked into one program, now tell opengl to use it.
    This loads the graphics program onto the GPU.
"""
glUseProgram(shader)
################################ Define Triangle ##############################
"""
    By default, opengl's coordinate system is:
        x: -1: left, 0: center, 1: right
        y: -1: bottom, 0: center, 1: top
        z: -1: at the viewer (not visible), 0: medium distance (at the screen), 1: far away (into screen)
   
    As with the colours, the reason for decimals is it's easier to control accuracy of data.
"""
vertices = (
                -0.5, -0.5, 0,
                 0.5, -0.5, 0,
                   0,  0.5, 0
            )
"""
    OpenGL doesn't like Python's data structures, but it runs with numpy's array type.
    So take the data and convert it to a numpy array, set the data type to a 32 bit float.
"""
vertices = np.array(vertices,dtype=np.float32)
"""
    Make a Vertex Array Object, this stores the data and its definitions.
"""
vao = glGenVertexArrays(1)
glBindVertexArray(vao)
"""
    We'll now load the vertex data into OpenGL, the way this is done is:
        create vertex buffer object -> bind vbo -> load in data -> (optional) unbind vbo
    unbinding is optional as every time a new object is loaded, a new vbo is created and bound.
"""
# generate one new buffer, store a reference to it as "vbo"
vbo = glGenBuffers(1)
# bind this buffer to opengl's array buffer, so that any calls to GL_ARRAY_BUFFER will be made on vbo
glBindBuffer(GL_ARRAY_BUFFER,vbo)
"""
    Load in the data,
        glBufferData(buffer to load to,     size of data in bytes,      data to load,   draw mode)
        draw mode: opengl can load data onto different memory types on the graphics card,
        it doesn't technically matter which draw type is used (in most cases),
        however graphics cards have different memory types which are optimised for read or write speed.
            GL_STREAM_DRAW: data is set once and used a few times
            GL_STATIC_DRAW: data is set once and used many times
            GL_DYNAMIC_DRAW: data is set and used many times
"""
glBufferData(GL_ARRAY_BUFFER,vertices.nbytes,vertices,GL_STATIC_DRAW)

"""
    Data has been loaded to vbo, but OpenGL doesn't know what it represents, right now it's just a bunch of numbers.
    So, grab the position attribute from the shader, and define the vbo data.
    Note that none of the code below is explicitly talking about "vbo" as vbo is the currently bound
    """
"""
    define an attribute:
    glVertexAttribPointer(attribute_location,   no_of_points_per_vertex,    data_type,
                            normalise,  stride,    pointer_to_first_vertex)
       
        attribute_location: We're defining the "position" data
        no_of_points_per_vertex: Each vertex has an (x,y,z) position
        data_type: floats (decimals)
        normalise: best just to set this to false
        size_per_vertex: take element 0 as the first x coordinate, then the next x coordinate occurs 3 elements later.
        Each element is a 32 bit float, so that's
            4 bytes per element * 3 elements to next vertex = 12 bytes of stride
       
        pointer_to_first_vertex: data starts at index 0, so make a c void pointer to zero.
        (weird compatibility thing.)
"""
position = glGetAttribLocation(shader,"aPos")
value = glGetUniformLocation(shader, "colorChange")
glEnableVertexAttribArray(position)
print(position,value)
glVertexAttribPointer(position,3,GL_FLOAT,GL_FALSE,12,ctypes.c_void_p(0))
################################ Main Loop ####################################
running = True
while running:
    glUniform3f(value, 1,1,1)
    ################################ Inputs ###################################
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running = False

    ################################ Rendering ################################
    glClear(GL_COLOR_BUFFER_BIT)
    # bind our triangle, this recalls all the data and definitions that were
    # defined earlier
    glBindVertexArray(vao)
    # draw the data, in triangle mode starting at vertex 0 and drawing 3 vertices
    glDrawArrays(GL_TRIANGLES,0,3)
    pg.display.flip()

    CLOCK.tick()
    framerate = int(CLOCK.get_fps())
    pg.display.set_caption("Running at "+str(framerate)+" frames per second.")

pg.quit()