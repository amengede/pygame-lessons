from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import pygame as pg
import numpy as np
# module for matrices/vectors (used in transformations)
import pyrr

################################ Initialisation ###############################
pg.init()
pg.display.set_mode((640,480),pg.OPENGL|pg.DOUBLEBUF)
CLOCK = pg.time.Clock()

glClearColor(0,0.2,0.2,1)
################################ Shaders ######################################
with open("shaders/vertex.txt",'r') as f:
    vertex_src = f.readlines()
with open("shaders/fragment.txt",'r') as f:
    fragment_src = f.readlines()

shader = compileProgram(compileShader(vertex_src,GL_VERTEX_SHADER),
                        compileShader(fragment_src,GL_FRAGMENT_SHADER))

glUseProgram(shader)

################################ Define Triangle ##############################
vertices = (
                 0.5,  0.5, 0, 1, 1,
                 0.5, -0.5, 0, 1, 0,
                -0.5, -0.5, 0, 0, 0,
                -0.5,  0.5, 0, 0, 1
            )
vertices = np.array(vertices,dtype=np.float32)

indices = (
                0, 1, 3,
                1, 2, 3
            )
indices = np.array(indices,dtype=np.uint32)

vao = glGenVertexArrays(1)
glBindVertexArray(vao)

vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER,vbo)
glBufferData(GL_ARRAY_BUFFER,vertices.nbytes,vertices,GL_STATIC_DRAW)

ebo = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,ebo)
glBufferData(GL_ELEMENT_ARRAY_BUFFER,indices.nbytes,indices,GL_STATIC_DRAW)

position = glGetAttribLocation(shader,"pos")
glEnableVertexAttribArray(position)
glVertexAttribPointer(position,3,GL_FLOAT,GL_FALSE,20,ctypes.c_void_p(0))

texture_coordinate = glGetAttribLocation(shader,"tex")
glEnableVertexAttribArray(texture_coordinate)
glVertexAttribPointer(texture_coordinate,2,GL_FLOAT,GL_FALSE,20,ctypes.c_void_p(12))
################################ Texture ######################################
texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D,texture)

glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

image = pg.image.load("gfx/wood.jpeg").convert()
image_width,image_height = image.get_rect().size
img_data = pg.image.tostring(image,'RGBA')

glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
glGenerateMipmap(GL_TEXTURE_2D)
################################ Transformations ##############################
"""
    model transformation, places the model into world coordinates.
    For this example, we'll rotate the rectangle around the x plane a bit
"""
model = pyrr.matrix44.create_from_axis_rotation(axis=np.array([1,0,0]),theta=np.radians(-55),dtype=np.float32)

"""
    view transformation, place it such that the camera is at the centre of the world.
    For this example, imagine the camera is placed at z=3, then the object would have to be shifted
    in the z-axis by -3 units
    because moving the camera backwards is the same as moving objects forwards
"""
view = pyrr.matrix44.create_from_translation(vec=np.array([0,0,-3]),dtype=np.float32)

"""
    projection transformation, turn 3D coordinates into 2D.

    this is done with
        pyrr.matrix44.create_perspective_projection(fovy, aspect, near, far, dtype=None)
            fovy: field of view y, how many degrees define the width of the view
            aspect: aspect ratio of view
            near: near distance, anything closer than this will not be drawn
            far: far distance, anything further than this will not be drawn

            note: the accuracy of the depth testing (covered in later lessons) decreases as
            the range between near and far increases.
"""
projection = pyrr.matrix44.create_perspective_projection(45, 640/480, 0.1, 10, dtype=np.float32)

"""
    Now we'll send these transformation matrices to the shader. In practice this would be done inside
    the game loop, as the transformations would be constantly changing. Right now we don't need to worry
    about this and can just send it once.
"""
#(shader_name, uniform_name)
model_location = glGetUniformLocation(shader,"model")
view_location = glGetUniformLocation(shader,"view")
projection_location = glGetUniformLocation(shader,"projection")

#(reference_to_location, number_of_matrices_to_load,
# whether_to_transpose_matrices (always set this to false), data_to_load)
glUniformMatrix4fv(model_location,1,GL_FALSE,model)
glUniformMatrix4fv(view_location,1,GL_FALSE,view)
glUniformMatrix4fv(projection_location,1,GL_FALSE,projection)
################################ Main Loop ####################################
running = True
while running:
    ################################ Inputs ###################################
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running = False
    ################################ Rendering ################################
    glClear(GL_COLOR_BUFFER_BIT)

    glBindTexture(GL_TEXTURE_2D,texture)
    glBindVertexArray(vao)
    glDrawElements(GL_TRIANGLES,6,GL_UNSIGNED_INT,None)
    pg.display.flip()

    CLOCK.tick()
    framerate = int(CLOCK.get_fps())
    pg.display.set_caption("Running at "+str(framerate)+" frames per second.")

pg.quit()