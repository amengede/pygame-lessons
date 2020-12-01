from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import pygame as pg
import numpy as np
import pyrr

################################ Initialisation ###############################
pg.init()
pg.display.set_mode((640,480),pg.OPENGL|pg.DOUBLEBUF)
CLOCK = pg.time.Clock()

glClearColor(0.05,0.05,0.05,1)
glEnable(GL_DEPTH_TEST)
################################ Shaders ######################################
with open("shaders/vertex.txt",'r') as f:
    vertex_src = f.readlines()
with open("shaders/fragment.txt",'r') as f:
    fragment_src = f.readlines()

shader = compileProgram(compileShader(vertex_src,GL_VERTEX_SHADER),
                        compileShader(fragment_src,GL_FRAGMENT_SHADER))

with open("shaders/light_vertex.txt",'r') as f:
    vertex_src = f.readlines()
with open("shaders/light_fragment.txt",'r') as f:
    fragment_src = f.readlines()

lighting_shader = compileProgram(compileShader(vertex_src,GL_VERTEX_SHADER),
                        compileShader(fragment_src,GL_FRAGMENT_SHADER))

glUseProgram(shader)
ambient_location = glGetUniformLocation(shader,"ambient")
glUniform3fv(ambient_location,1,np.array([0.05,0.05,0.05],dtype=np.float32))

################################ Classes ######################################

class Camera:
    def __init__(self,position):
        self.position = position
        self.looking_at = np.array([6,6,0],dtype=np.float32)

    def update(self):
        """
            create lookat matrix, right we're using the same matrix each time,
            but in a more complex game this would be changing each frame
        """
        #direction the camera is looking in
        looking_direction = self.looking_at - self.position
        """
            the cross product produces a vector perpendicular to both vectors
        """
        up = np.array([0,0,1],dtype=np.float32)
        camera_right = pyrr.vector3.cross(up,looking_direction)
        camera_up = pyrr.vector3.cross(looking_direction,camera_right)

        # eye position, target position, up direction
        lookat_matrix = pyrr.matrix44.create_look_at(self.position,self.looking_at,camera_up,dtype=np.float32)

        projection = pyrr.matrix44.create_perspective_projection(45, 640/480, 1, 30, dtype=np.float32)

        glUseProgram(shader)
        view_location = glGetUniformLocation(shader,"view")
        glUniformMatrix4fv(view_location,1,GL_FALSE,lookat_matrix)
        projection_location = glGetUniformLocation(shader,"projection")
        glUniformMatrix4fv(projection_location,1,GL_FALSE,projection)

        glUseProgram(lighting_shader)
        view_location = glGetUniformLocation(lighting_shader,"view")
        glUniformMatrix4fv(view_location,1,GL_FALSE,lookat_matrix)
        projection_location = glGetUniformLocation(lighting_shader,"projection")
        glUniformMatrix4fv(projection_location,1,GL_FALSE,projection)

class Box:
    def __init__(self,position):
        glUseProgram(shader)
        self.position = position
        #model data
        self.vertices = (
                -0.5, -0.5, -0.5, 0, 0, 0, 0, -1,
                 0.5, -0.5, -0.5, 1, 0, 0, 0, -1,
                 0.5,  0.5, -0.5, 1, 1, 0, 0, -1,

                 0.5,  0.5, -0.5, 1, 1, 0, 0, -1,
                -0.5,  0.5, -0.5, 0, 1, 0, 0, -1,
                -0.5, -0.5, -0.5, 0, 0, 0, 0, -1,

                -0.5, -0.5,  0.5, 0, 0, 0, 0,  1,
                 0.5, -0.5,  0.5, 1, 0, 0, 0,  1,
                 0.5,  0.5,  0.5, 1, 1, 0, 0,  1,

                 0.5,  0.5,  0.5, 1, 1, 0, 0,  1,
                -0.5,  0.5,  0.5, 0, 1, 0, 0,  1,
                -0.5, -0.5,  0.5, 0, 0, 0, 0,  1,

                -0.5,  0.5,  0.5, 1, 0, -1, 0,  0,
                -0.5,  0.5, -0.5, 1, 1, -1, 0,  0,
                -0.5, -0.5, -0.5, 0, 1, -1, 0,  0,

                -0.5, -0.5, -0.5, 0, 1, -1, 0,  0,
                -0.5, -0.5,  0.5, 0, 0, -1, 0,  0,
                -0.5,  0.5,  0.5, 1, 0, -1, 0,  0,

                 0.5,  0.5,  0.5, 1, 0, 1, 0,  0,
                 0.5,  0.5, -0.5, 1, 1, 1, 0,  0,
                 0.5, -0.5, -0.5, 0, 1, 1, 0,  0,

                 0.5, -0.5, -0.5, 0, 1, 1, 0,  0,
                 0.5, -0.5,  0.5, 0, 0, 1, 0,  0,
                 0.5,  0.5,  0.5, 1, 0, 1, 0,  0,

                -0.5, -0.5, -0.5, 0, 1, 0, -1,  0,
                 0.5, -0.5, -0.5, 1, 1, 0, -1,  0,
                 0.5, -0.5,  0.5, 1, 0, 0, -1,  0,

                 0.5, -0.5,  0.5, 1, 0, 0, -1,  0,
                -0.5, -0.5,  0.5, 0, 0, 0, -1,  0,
                -0.5, -0.5, -0.5, 0, 1, 0, -1,  0,

                -0.5,  0.5, -0.5, 0, 1, 0, 1,  0,
                 0.5,  0.5, -0.5, 1, 1, 0, 1,  0,
                 0.5,  0.5,  0.5, 1, 0, 0, 1,  0,

                 0.5,  0.5,  0.5, 1, 0, 0, 1,  0,
                -0.5,  0.5,  0.5, 0, 0, 0, 1,  0,
                -0.5,  0.5, -0.5, 0, 1, 0, 1,  0
            )
        self.vertices = np.array(self.vertices,dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,self.vbo)
        glBufferData(GL_ARRAY_BUFFER,self.vertices.nbytes,self.vertices,GL_STATIC_DRAW)

        self.pos = glGetAttribLocation(shader,"pos")
        glEnableVertexAttribArray(self.pos)
        glVertexAttribPointer(self.pos,3,GL_FLOAT,GL_FALSE,32,ctypes.c_void_p(0))

        self.texture_coordinate = glGetAttribLocation(shader,"tex")
        glEnableVertexAttribArray(self.texture_coordinate)
        glVertexAttribPointer(self.texture_coordinate,2,GL_FLOAT,GL_FALSE,32,ctypes.c_void_p(12))

        self.normal = glGetAttribLocation(shader,"normal")
        glEnableVertexAttribArray(self.normal)
        glVertexAttribPointer(self.normal,3,GL_FLOAT,GL_FALSE,32,ctypes.c_void_p(20))

        # texture data
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,self.texture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        image = pg.image.load("gfx/wood.jpeg").convert()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')

        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def update(self):
        glUseProgram(shader)
        current_time = pg.time.get_ticks()/10

        rotation = pyrr.matrix44.create_from_z_rotation(np.radians(-0.5*current_time),dtype=np.float32)
        translation = pyrr.matrix44.create_from_translation(self.position,dtype=np.float32)

        model = pyrr.matrix44.multiply(rotation,translation)

        model_location = glGetUniformLocation(shader,"model")
        glUniformMatrix4fv(model_location,1,GL_FALSE,model)

    def draw(self):
        glUseProgram(shader)
        glBindTexture(GL_TEXTURE_2D,self.texture)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES,0,len(self.vertices))

class Light:
    def __init__(self,position,colour):
        glUseProgram(lighting_shader)
        self.position = position
        self.colour = colour
        #model data
        self.vertices = (
                -0.1, -0.1, -0.1,
                 0.1, -0.1, -0.1,
                 0.1,  0.1, -0.1,

                 0.1,  0.1, -0.1,
                -0.1,  0.1, -0.1,
                -0.1, -0.1, -0.1,

                -0.1, -0.1,  0.1,
                 0.1, -0.1,  0.1,
                 0.1,  0.1,  0.1,

                 0.1,  0.1,  0.1,
                -0.1,  0.1,  0.1,
                -0.1, -0.1,  0.1,

                -0.1,  0.1,  0.1,
                -0.1,  0.1, -0.1,
                -0.1, -0.1, -0.1,

                -0.1, -0.1, -0.1,
                -0.1, -0.1,  0.1,
                -0.1,  0.1,  0.1,

                 0.1,  0.1,  0.1,
                 0.1,  0.1, -0.1,
                 0.1, -0.1, -0.1,

                 0.1, -0.1, -0.1,
                 0.1, -0.1,  0.1,
                 0.1,  0.1,  0.1,

                -0.1, -0.1, -0.1,
                 0.1, -0.1, -0.1,
                 0.1, -0.1,  0.1,

                 0.1, -0.1,  0.1,
                -0.1, -0.1,  0.1,
                -0.1, -0.1, -0.1,

                -0.1,  0.1, -0.1,
                 0.1,  0.1, -0.1,
                 0.1,  0.1,  0.1,

                 0.1,  0.1,  0.1,
                -0.1,  0.1,  0.1,
                -0.1,  0.1, -0.1
            )
        self.vertices = np.array(self.vertices,dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,self.vbo)
        glBufferData(GL_ARRAY_BUFFER,self.vertices.nbytes,self.vertices,GL_STATIC_DRAW)

        self.pos = glGetAttribLocation(lighting_shader,"pos")
        glEnableVertexAttribArray(self.pos)
        glVertexAttribPointer(self.pos,3,GL_FLOAT,GL_FALSE,12,ctypes.c_void_p(0))

    def update(self):
        glUseProgram(lighting_shader)
        model = pyrr.matrix44.create_from_translation(self.position,dtype=np.float32)

        model_location = glGetUniformLocation(lighting_shader,"model")
        glUniformMatrix4fv(model_location,1,GL_FALSE,model)

        lightColour_location = glGetUniformLocation(lighting_shader,"lightColour")
        glUniform3fv(lightColour_location,1,self.colour)

        glUseProgram(shader)
        pos_location = glGetUniformLocation(shader,"lightPos")
        col_location = glGetUniformLocation(shader,"lightCol")
        glUniform3fv(pos_location,1,self.position)
        glUniform3fv(col_location,1,self.colour)

    def draw(self):
        glUseProgram(lighting_shader)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES,0,len(self.vertices))
    
################################ Create game objects ##########################
camera = Camera(np.array([3,-2,5],dtype=np.float32))
box = Box(np.array([10,6,0],dtype=np.float32))
light = Light(np.array([6,6,3],dtype=np.float32),np.array([1,0,1],dtype=np.float32))
################################ Main Loop ####################################
running = True
while running:
    ################################ Inputs ###################################
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running = False
    ################################ Update ###################################
    camera.update()
    box.update()
    light.update()
    ################################ Rendering ################################
    """
        Now as well as resetting the colour, we also have to reset the depth buffer
    """
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    box.draw()
    light.draw()

    pg.display.flip()

    CLOCK.tick()
    framerate = int(CLOCK.get_fps())
    pg.display.set_caption("Running at "+str(framerate)+" frames per second.")

pg.quit()