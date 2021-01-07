from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import pygame as pg
import numpy as np
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

with open("shaders/vertex2.txt",'r') as f:
    vertex_src = f.readlines()
with open("shaders/fragment2.txt",'r') as f:
    fragment_src = f.readlines()

shader2D = compileProgram(compileShader(vertex_src,GL_VERTEX_SHADER),
                            compileShader(fragment_src,GL_FRAGMENT_SHADER))

glUseProgram(shader2D)
FRAMEBUFFER = glGenFramebuffers(1)
glBindFramebuffer(GL_FRAMEBUFFER,FRAMEBUFFER)
COLORBUFFER = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, COLORBUFFER)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 640, 480, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
glBindTexture(GL_TEXTURE_2D, 0)
glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,COLORBUFFER,0)

RBO = glGenRenderbuffers(1)
glBindRenderbuffer(GL_RENDERBUFFER,RBO)
glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, 640,480)
glBindRenderbuffer(GL_RENDERBUFFER,0)

glBindFramebuffer(GL_FRAMEBUFFER,0)

################################ Define Triangle ##############################
glUseProgram(shader)
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
################################ Screen Surface ############################
glUseProgram(shader2D)
screen_vertices = (
            -1,  1, 0, 1,
            -1, -1, 0, 0,
             1, -1, 1, 0,

            -1,  1, 0, 1,
             1, -1, 1, 0,
             1,  1, 1, 1
            )
screen_vertices = np.array(screen_vertices,dtype=np.float32)

screen_vao = glGenVertexArrays(1)
glBindVertexArray(screen_vao)

screen_vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER,screen_vbo)
glBufferData(GL_ARRAY_BUFFER,screen_vertices.nbytes,screen_vertices,GL_STATIC_DRAW)

position = glGetAttribLocation(shader2D,"pos")
glEnableVertexAttribArray(position)
glVertexAttribPointer(position,2,GL_FLOAT,GL_FALSE,16,ctypes.c_void_p(0))

texture_coordinate = glGetAttribLocation(shader2D,"tex")
glEnableVertexAttribArray(texture_coordinate)
glVertexAttribPointer(texture_coordinate,2,GL_FLOAT,GL_FALSE,16,ctypes.c_void_p(8))
################################ Texture ######################################
glUseProgram(shader)
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
glUseProgram(shader)
trans_location = glGetUniformLocation(shader,"myTransformation")
################################ Main Loop ####################################
running = True
while running:
    ################################ Inputs ###################################
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running = False
    ################################ Transformations ##########################
    glUseProgram(shader)
    current_time = current_time = pg.time.get_ticks()/10

    translation = pyrr.matrix44.create_from_translation(np.array([0,1,0]),dtype=np.float32)
    scale = pyrr.matrix44.create_from_scale(np.array([2,0.5,1]),dtype=np.float32)
    rotation = pyrr.matrix44.create_from_z_rotation(np.radians(current_time),dtype=np.float32)
    second_rotation = pyrr.matrix44.create_from_x_rotation(np.radians(current_time/2),dtype=np.float32)

    translation_then_rotation = pyrr.matrix44.multiply(translation,rotation)
    rotation_then_translation = pyrr.matrix44.multiply(rotation,translation)

    interesting = pyrr.matrix44.multiply(rotation_then_translation,second_rotation)

    glUniformMatrix4fv(trans_location,1,GL_FALSE,rotation)
    ################################ Rendering ################################
    glBindFramebuffer(GL_FRAMEBUFFER, FRAMEBUFFER)
    glClear(GL_COLOR_BUFFER_BIT)

    glUseProgram(shader)
    glBindTexture(GL_TEXTURE_2D,texture)
    glBindVertexArray(vao)
    glDrawElements(GL_TRIANGLES,6,GL_UNSIGNED_INT,None)

    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glClear(GL_COLOR_BUFFER_BIT)
    glUseProgram(shader2D)
    glBindTexture(GL_TEXTURE_2D,COLORBUFFER)
    glBindVertexArray(screen_vao)
    glDrawArrays(GL_TRIANGLES,0,6)

    pg.display.flip()

    CLOCK.tick()
    framerate = int(CLOCK.get_fps())
    pg.display.set_caption("Running at "+str(framerate)+" frames per second.")

pg.quit()