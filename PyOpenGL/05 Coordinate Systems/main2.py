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

"""
    Depth testing is used here to make sure triangles are drawn in the proper order
"""
glEnable(GL_DEPTH_TEST)
################################ Define Cube ##################################
vertices = (
                -0.5, -0.5, -0.5, 0, 0,
                 0.5, -0.5, -0.5, 1, 0,
                 0.5,  0.5, -0.5, 1, 1,

                 0.5,  0.5, -0.5, 1, 1,
                -0.5,  0.5, -0.5, 0, 1,
                -0.5, -0.5, -0.5, 0, 0,

                -0.5, -0.5,  0.5, 0, 0,
                 0.5, -0.5,  0.5, 1, 0,
                 0.5,  0.5,  0.5, 1, 1,

                 0.5,  0.5,  0.5, 1, 1,
                -0.5,  0.5,  0.5, 0, 1,
                -0.5, -0.5,  0.5, 0, 0,

                -0.5,  0.5,  0.5, 1, 0,
                -0.5,  0.5, -0.5, 1, 1,
                -0.5, -0.5, -0.5, 0, 1,

                -0.5, -0.5, -0.5, 0, 1,
                -0.5, -0.5,  0.5, 0, 0,
                -0.5,  0.5,  0.5, 1, 0,

                 0.5,  0.5,  0.5, 1, 0,
                 0.5,  0.5, -0.5, 1, 1,
                 0.5, -0.5, -0.5, 0, 1,

                 0.5, -0.5, -0.5, 0, 1,
                 0.5, -0.5,  0.5, 0, 0,
                 0.5,  0.5,  0.5, 1, 0,

                -0.5, -0.5, -0.5, 0, 1,
                 0.5, -0.5, -0.5, 1, 1,
                 0.5, -0.5,  0.5, 1, 0,

                 0.5, -0.5,  0.5, 1, 0,
                -0.5, -0.5,  0.5, 0, 0,
                -0.5, -0.5, -0.5, 0, 1,

                -0.5,  0.5, -0.5, 0, 1,
                 0.5,  0.5, -0.5, 1, 1,
                 0.5,  0.5,  0.5, 1, 0,

                 0.5,  0.5,  0.5, 1, 0,
                -0.5,  0.5,  0.5, 0, 0,
                -0.5,  0.5, -0.5, 0, 1
            )
vertices = np.array(vertices,dtype=np.float32)

vao = glGenVertexArrays(1)
glBindVertexArray(vao)

vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER,vbo)
glBufferData(GL_ARRAY_BUFFER,vertices.nbytes,vertices,GL_STATIC_DRAW)

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
model = pyrr.matrix44.create_from_axis_rotation(axis=np.array([1,0,0]),theta=np.radians(-55),dtype=np.float32)
view = pyrr.matrix44.create_from_translation(vec=np.array([0,0,-3]),dtype=np.float32)
projection = pyrr.matrix44.create_perspective_projection(45, 640/480, 0.1, 10, dtype=np.float32)

model_location = glGetUniformLocation(shader,"model")
view_location = glGetUniformLocation(shader,"view")
projection_location = glGetUniformLocation(shader,"projection")

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
    ################################ Update ###################################
    """
        update the model matrix each frame
    """
    current_time = pg.time.get_ticks()/10
    model = pyrr.matrix44.create_from_axis_rotation(axis=np.array([1,0.5,0]),theta=np.radians(-0.5*current_time),dtype=np.float32)

    glUniformMatrix4fv(model_location,1,GL_FALSE,model)
    ################################ Rendering ################################
    """
        Now as well as resetting the colour, we also have to reset the depth buffer
    """
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glBindTexture(GL_TEXTURE_2D,texture)
    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLES,0,len(vertices))
    pg.display.flip()

    CLOCK.tick()
    framerate = int(CLOCK.get_fps())
    pg.display.set_caption("Running at "+str(framerate)+" frames per second.")

pg.quit()