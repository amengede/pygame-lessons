################ 3D Game ######################################################
import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr


pygame.init()

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 720
SCREEN = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT),
                                    pygame.DOUBLEBUF|pygame.OPENGL)
CLOCK = pygame.time.Clock()
pygame.mouse.set_visible(False)

################ OpenGL Setup #################################################
glClearColor(0,0,0,1)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
glEnable(GL_DEPTH_TEST)

################ Shaders ######################################################

with open("shaders/vertex.txt",'r') as f:
    vertex_src = f.readlines()
with open("shaders/fragment.txt",'r') as f:
    fragment_src = f.readlines()

shader = compileProgram(compileShader(vertex_src,GL_VERTEX_SHADER),
                        compileShader(fragment_src,GL_FRAGMENT_SHADER))

glUseProgram(shader)
MAX_LIGHTS = 8
current_lights = 0
################ Helper Functions #############################################

def importData(filename):
    """
        Reads a file and loads all objects, returns a reference to the player
        object.
    """
    with open(filename,'r') as f:
        line = f.readline()
        while line:
            if line[0]=='w':
                #wall
                # w(a_x,a_y,b_x,b_y,z,height,tex)
                beginning = line.find('(')
                line = line[beginning+1:-2].replace('\n','').split(',')
                l = [int(item) for item in line]
                pos_a = np.array([l[0],l[1]],dtype=np.float32)
                pos_b = np.array([l[2],l[3]],dtype=np.float32)
                z = l[4]
                height = l[5]
                tex = l[6]
                w = Wall(pos_a,pos_b,z,height,tex)
                GAME_OBJECTS.add(w)
                RESTRICTED.add(w)
            elif line[0]=='f':
                #floor
                # w(a_x,a_y,b_x,b_y,c_x,c_y,d_x,d_y,z,tex)
                beginning = line.find('(')
                line = line[beginning+1:-2].replace('\n','').split(',')
                l = [int(item) for item in line]
                pos_a = np.array([l[0],l[1]],dtype=np.float32)
                pos_b = np.array([l[2],l[3]],dtype=np.float32)
                pos_c = np.array([l[4],l[5]],dtype=np.float32)
                pos_d = np.array([l[6],l[7]],dtype=np.float32)
                z = l[8]
                tex = l[9]
                floor = Floor(pos_a,pos_b,pos_c,pos_d,z,tex)
                GAME_OBJECTS.add(floor)
            elif line[0]=='c':
                #ceiling
                # c(a_x,a_y,b_x,b_y,c_x,c_y,d_x,d_y,z,tex)
                beginning = line.find('(')
                line = line[beginning+1:-2].replace('\n','').split(',')
                l = [int(item) for item in line]
                pos_a = np.array([l[0],l[1]],dtype=np.float32)
                pos_b = np.array([l[2],l[3]],dtype=np.float32)
                pos_c = np.array([l[4],l[5]],dtype=np.float32)
                pos_d = np.array([l[6],l[7]],dtype=np.float32)
                z = l[8]
                tex = l[9]
                c = Ceiling(pos_a,pos_b,pos_c,pos_d,z,tex)
                GAME_OBJECTS.add(c)
            elif line[0]=='l':
                #light
                # l(x,y,z,r,g,b)
                beginning = line.find('(')
                line = line[beginning+1:-2].replace('\n','').split(',')
                l = [int(item) for item in line]
                position = np.array([l[0],l[1],l[2]],dtype=np.float32)
                colour = np.array([l[3],l[4],l[5]],dtype=np.float32)
                light = Light(position,colour)
                GAME_OBJECTS.add(light)
            elif line[0]=='p':
                #player
                # p(x,y,direction)
                line = line[2:-2].replace('\n','').split(',')
                l = [int(item) for item in line]
                player = Player(np.array([l[0],l[1],16],dtype=np.float32),l[2])
                GAME_OBJECTS.add(player)
            line = f.readline()
        return player

def importTextures():
    floor_0 = Texture("tex/floor0.jpg")
    TEXTURES["floor"].append(floor_0)
    floor_1 = Texture("tex/floor1.jpg")
    TEXTURES["floor"].append(floor_1)
    wall = Texture("tex/wall.jpg")
    TEXTURES["wall"].append(wall)
    wall_1 = Texture("tex/wall1.jpg")
    TEXTURES["wall"].append(wall_1)
    ceiling_0 = Texture("tex/ceiling0.jpg")
    TEXTURES["ceiling"].append(ceiling_0)
    ceiling_1 = Texture("tex/ceiling1.jpg")
    TEXTURES["ceiling"].append(ceiling_1)

def clearLights():
    for i in range(MAX_LIGHTS):
        glUniform1fv(glGetUniformLocation(shader,f'pointLights[{i}].isOn'),1,False)
################ Classes ######################################################

class Player(pygame.sprite.Sprite):
    def __init__(self,position,direction):
        pygame.sprite.Sprite.__init__(self)
        self.radius = 16
        self.position = position
        self.theta = direction
        self.phi = 0
        pygame.mouse.set_pos(SCREEN_WIDTH/2,SCREEN_HEIGHT/2)
        self.rect = pygame.rect.Rect(self.position[0]-self.radius,
                                        self.position[1]-self.radius,
                                        self.radius,self.radius)
        self.speed = 2
        self.height = 30
    
    def update(self):
        #take inputs
        keystate = pygame.key.get_pressed()
        walk_direction = 0
        walking = False

        #mouse
        new_pos = pygame.mouse.get_pos()
        pygame.mouse.set_pos(SCREEN_WIDTH/2,SCREEN_HEIGHT/2)
        self.theta -= t*(new_pos[0] - SCREEN_WIDTH/2)/10
        self.theta = self.theta%360
        self.phi -= t*(new_pos[1] - SCREEN_HEIGHT/2)/10
        self.phi = min(max(self.phi,-90),90)

        #keys
        if keystate[pygame.K_a]:
            walking = True
            walk_direction = 90
        if keystate[pygame.K_d]:
            walk_direction = -90
            walking = True
        if keystate[pygame.K_w]:
            walk_direction = 0
            walking = True
        if keystate[pygame.K_s]:
            walk_direction = 180
            walking = True
        
        cos_phi = np.cos(np.radians(self.phi),dtype=np.float32)
        sin_phi = np.sin(np.radians(self.phi),dtype=np.float32)
        cos_theta = np.cos(np.radians(self.theta),dtype=np.float32)
        sin_theta = np.sin(np.radians(self.theta),dtype=np.float32)
        
        if walking:
            actual_direction = self.theta + walk_direction
            cos_ad = np.cos(np.radians(actual_direction),dtype=np.float32)
            sin_ad = np.sin(np.radians(actual_direction),dtype=np.float32)
            self.position += self.speed*t*np.array([cos_ad,sin_ad,0],dtype=np.float32)/10
        #get lookat
        look_direction = np.array([cos_phi*cos_theta,cos_phi*sin_theta,sin_phi],dtype=np.float32)
        up = np.array([0,0,1],dtype=np.float32)
        camera_right = pyrr.vector3.cross(up,look_direction)
        camera_up = pyrr.vector3.cross(look_direction,camera_right)

        lookat_matrix = pyrr.matrix44.create_look_at(self.position,self.position + look_direction, camera_up, dtype=np.float32)
        projection_matrix = pyrr.matrix44.create_perspective_projection(45,640/480,1,280,dtype=np.float32)

        glUniformMatrix4fv(glGetUniformLocation(shader,"view"),1,GL_FALSE,lookat_matrix)
        glUniformMatrix4fv(glGetUniformLocation(shader,"projection"),1,GL_FALSE,projection_matrix)
        glUniform3fv(glGetUniformLocation(shader,"viewPos"),1,self.position)

    def draw(self):
        pass

class Wall(pygame.sprite.Sprite):
    def __init__(self,pos_a,pos_b,z,height,texture):
        pygame.sprite.Sprite.__init__(self)
        self.z = z
        self.position = np.array([pos_a[0],pos_a[1],self.z],dtype=np.float32)
        self.pos_a = np.array([0,0,0],dtype=np.float32)
        self.pos_b = pos_b - pos_a
        self.height = height
        self.texture = texture

        #calculate normal by hand
        u = np.array([pos_b[0]-pos_a[0],pos_b[1]-pos_a[1],self.z],dtype=np.float32)
        v = np.array([pos_b[0]-pos_a[0],pos_b[1]-pos_a[1],self.z+self.height],dtype=np.float32)
        self.normal = pyrr.vector.normalise(pyrr.vector3.cross(u,v))

        self.vertices = (self.pos_a[0], self.pos_a[1], 0,               self.normal[0], self.normal[1], self.normal[2], 0.0, 1.0,
                         self.pos_b[0], self.pos_b[1], 0,               self.normal[0], self.normal[1], self.normal[2], 1.0, 1.0,
                         self.pos_b[0], self.pos_b[1], self.height,     self.normal[0], self.normal[1], self.normal[2], 1.0, 0.0,
                         self.pos_a[0], self.pos_a[1], self.height,     self.normal[0], self.normal[1], self.normal[2], 0.0, 0.0)
        self.vertices = np.array(self.vertices,dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,self.vbo)
        glBufferData(GL_ARRAY_BUFFER,self.vertices.nbytes,self.vertices,GL_STATIC_DRAW)

        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(0))
        #normal
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(self.vertices.itemsize*3))
        #texture coordinates
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2,2,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(self.vertices.itemsize*6))
    
    def update(self):
        self.model = pyrr.matrix44.create_from_translation(self.position,dtype=np.float32)

    def draw(self):
        #material properties
        glUniform3fv(glGetUniformLocation(shader,"material.ambient"),1,TEXTURES["wall"][self.texture].ambient)
        glUniform3fv(glGetUniformLocation(shader,"material.specular"),1,TEXTURES["wall"][self.texture].specular)
        glUniform1fv(glGetUniformLocation(shader,"material.shininess"),1,TEXTURES["wall"][self.texture].shininess)
        glUniformMatrix4fv(glGetUniformLocation(shader,"model"),1,GL_FALSE,self.model)
        glBindVertexArray(self.vao)
        glBindTexture(GL_TEXTURE_2D,TEXTURES["wall"][self.texture].id)
        glDrawArrays(GL_TRIANGLE_FAN,0,4)

class Floor(pygame.sprite.Sprite):
    def __init__(self,pos_a,pos_b,pos_c,pos_d,z,texture):
        pygame.sprite.Sprite.__init__(self)
        self.z = z
        self.position = np.array([pos_a[0],pos_a[1],self.z],dtype=np.float32)
        self.pos_a = np.array([0,0,0],dtype=np.float32)
        self.pos_b = pos_b - pos_a
        self.pos_c = pos_c - pos_a
        self.pos_d = pos_d - pos_a
        self.texture = texture

        self.vertices = (self.pos_a[0], self.pos_a[1], 0, 0.0, 0.0, 1.0, 0.0, 0.0,
                         self.pos_b[0], self.pos_b[1], 0, 0.0, 0.0, 1.0, 0.0, 1.0,
                         self.pos_c[0], self.pos_c[1], 0, 0.0, 0.0, 1.0, 1.0, 1.0,
                         self.pos_d[0], self.pos_d[1], 0, 0.0, 0.0, 1.0, 1.0, 0.0)
        self.vertices = np.array(self.vertices,dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,self.vbo)
        glBufferData(GL_ARRAY_BUFFER,self.vertices.nbytes,self.vertices,GL_STATIC_DRAW)

        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(0))
        #normal
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(self.vertices.itemsize*3))
        #texture coordinates
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2,2,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(self.vertices.itemsize*6))
    
    def update(self):
        self.model = pyrr.matrix44.create_from_translation(self.position,dtype=np.float32)

    def draw(self):
        #material properties
        glUniform3fv(glGetUniformLocation(shader,"material.ambient"),1,TEXTURES["floor"][self.texture].ambient)
        glUniform3fv(glGetUniformLocation(shader,"material.specular"),1,TEXTURES["floor"][self.texture].specular)
        glUniform1fv(glGetUniformLocation(shader,"material.shininess"),1,TEXTURES["floor"][self.texture].shininess)
        glUniformMatrix4fv(glGetUniformLocation(shader,"model"),1,GL_FALSE,self.model)
        glBindVertexArray(self.vao)
        glBindTexture(GL_TEXTURE_2D,TEXTURES["floor"][self.texture].id)
        glDrawArrays(GL_TRIANGLE_FAN,0,4)

class Ceiling(pygame.sprite.Sprite):
    def __init__(self,pos_a,pos_b,pos_c,pos_d,z,texture):
        pygame.sprite.Sprite.__init__(self)
        self.z = z
        self.position = np.array([pos_a[0],pos_a[1],self.z],dtype=np.float32)
        self.pos_a = np.array([0,0,0],dtype=np.float32)
        self.pos_b = pos_b - pos_a
        self.pos_c = pos_c - pos_a
        self.pos_d = pos_d - pos_a
        self.texture = texture

        self.vertices = (self.pos_a[0], self.pos_a[1], 0, 0.0, 0.0, 1.0, 0.0, 0.0,
                         self.pos_b[0], self.pos_b[1], 0, 0.0, 0.0, 1.0, 0.0, 1.0,
                         self.pos_c[0], self.pos_c[1], 0, 0.0, 0.0, 1.0, 1.0, 1.0,
                         self.pos_d[0], self.pos_d[1], 0, 0.0, 0.0, 1.0, 1.0, 0.0)
        self.vertices = np.array(self.vertices,dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,self.vbo)
        glBufferData(GL_ARRAY_BUFFER,self.vertices.nbytes,self.vertices,GL_STATIC_DRAW)

        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(0))
        #normal
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(self.vertices.itemsize*3))
        #texture coordinates
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2,2,GL_FLOAT,GL_FALSE,self.vertices.itemsize*8,ctypes.c_void_p(self.vertices.itemsize*6))
    
    def update(self):
        self.model = pyrr.matrix44.create_from_translation(self.position,dtype=np.float32)

    def draw(self):
        #material properties
        glUniform3fv(glGetUniformLocation(shader,"material.ambient"),1,TEXTURES["ceiling"][self.texture].ambient)
        glUniform3fv(glGetUniformLocation(shader,"material.specular"),1,TEXTURES["ceiling"][self.texture].specular)
        glUniform1fv(glGetUniformLocation(shader,"material.shininess"),1,TEXTURES["ceiling"][self.texture].shininess)
        #model matrix
        glUniformMatrix4fv(glGetUniformLocation(shader,"model"),1,GL_FALSE,self.model)
        #draw it
        glBindVertexArray(self.vao)
        glBindTexture(GL_TEXTURE_2D,TEXTURES["ceiling"][self.texture].id)
        glDrawArrays(GL_TRIANGLE_FAN,0,4)

class Light(pygame.sprite.Sprite):
    def __init__(self,position,colour):
        pygame.sprite.Sprite.__init__(self)
        self.position = position
        self.colour = colour
        self.active = True
        
    def update(self):
        global current_lights
        if self.active and current_lights<MAX_LIGHTS:
            glUniform1fv(glGetUniformLocation(shader,f'pointLights[{current_lights}].isOn'),1,True)

            glUniform3fv(glGetUniformLocation(shader,f'pointLights[{current_lights}].position'),1,self.position)

            glUniform1fv(glGetUniformLocation(shader,f'pointLights[{current_lights}].constant'),1,1.0)
            glUniform1fv(glGetUniformLocation(shader,f'pointLights[{current_lights}].linear'),1,0.045)
            glUniform1fv(glGetUniformLocation(shader,f'pointLights[{current_lights}].quadratic'),1,0.0075)

            glUniform3fv(glGetUniformLocation(shader,f'pointLights[{current_lights}].ambient'),1,0.1*self.colour)
            glUniform3fv(glGetUniformLocation(shader,f'pointLights[{current_lights}].diffuse'),1,1.0*self.colour)
            glUniform3fv(glGetUniformLocation(shader,f'pointLights[{current_lights}].specular'),1,0.6*self.colour)
            current_lights += 1
    
    def draw(self):
        pass

class Texture:
    def __init__(self,filepath):
        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,self.id)

        #set properties
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        #data
        image = pygame.image.load(filepath)
        image_width, image_height = image.get_rect().size
        image_data = pygame.image.tostring(image,"RGBA")
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,image_data)

        #material properties
        self.ambient = np.array([1,1,1],dtype=np.float32)
        self.specular = np.array([1,1,1],dtype=np.float32)
        self.shininess = 32

################ Game Objects #################################################
GAME_OBJECTS = pygame.sprite.Group()
RESTRICTED = pygame.sprite.Group()
TEXTURES = {"floor":[],"wall":[],"ceiling":[]}
importTextures()
player = importData('level.txt')
################ Game Loop ####################################################
running = True
t = 0
while running:
    ################ Events ###################################################
    for event in pygame.event.get():
        if event.type==pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
            running = False
    ################ Update ###################################################
    current_lights = 0
    clearLights()
    GAME_OBJECTS.update()
    ################ Render ###################################################
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    for obj in GAME_OBJECTS.sprites():
        obj.draw()
    ################ Framerate ################################################
    t = CLOCK.get_time()
    CLOCK.tick()
    fps = CLOCK.get_fps()
    pygame.display.set_caption("Running at "+str(int(fps))+" fps")
    pygame.display.flip()
