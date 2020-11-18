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
"""
    Each vertex now contains an (x,y,z) position as well as an (s,t) texture coordinate.

        s: 0: left of image, 1: right of image
        t: 0: bottom of image, 1: top of image
"""
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
"""
    Create a texture object and bind it
"""
texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D,texture)

"""
    Set wrapping and filtering properties for texture
"""
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

"""
    load the texture, get its size, then convert it to a format opengl will understand.
"""
image = pg.image.load("gfx/wood.jpeg").convert()
image_width,image_height = image.get_rect().size
img_data = pg.image.tostring(image,'RGBA')
"""
    Load data to texture,
    (load_target, mipmap level (zero is a good value here as we haven't defined a mipmap),
    data format, width, height, must be zero for legacy reason, format, data_type, data)
"""
glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
glGenerateMipmap(GL_TEXTURE_2D)

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