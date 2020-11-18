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
with open("shaders/vertex.txt",'r') as f:
    vertex_src = f.readlines()
with open("shaders/fragment.txt",'r') as f:
    fragment_src = f.readlines()

shader = compileProgram(compileShader(vertex_src,GL_VERTEX_SHADER),
                        compileShader(fragment_src,GL_FRAGMENT_SHADER))

glUseProgram(shader)
################################ Define Triangle ##############################
vertices = (
                 0.5,  0.5, 0,
                 0.5, -0.5, 0,
                -0.5, -0.5, 0,
                -0.5,  0.5, 0
            )
vertices = np.array(vertices,dtype=np.float32)

"""
    Indexed drawing needs a set of indices to be defined. Basically, which vertices to draw. in which order.
"""
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
glVertexAttribPointer(position,3,GL_FLOAT,GL_FALSE,12,ctypes.c_void_p(0))

################################ Main Loop ####################################
running = True
while running:
    ################################ Inputs ###################################
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running = False

    ################################ Rendering ################################
    glClear(GL_COLOR_BUFFER_BIT)

    glBindVertexArray(vao)
    # draw the based on the indices, in triangle mode, drawing 6 points, where indices are
    # unsigned integers, last argument set to None for a weird legacy code thing.
    glDrawElements(GL_TRIANGLES,6,GL_UNSIGNED_INT,None)
    pg.display.flip()

    CLOCK.tick()
    framerate = int(CLOCK.get_fps())
    pg.display.set_caption("Running at "+str(framerate)+" frames per second.")

pg.quit()