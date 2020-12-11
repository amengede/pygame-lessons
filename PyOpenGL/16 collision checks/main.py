################ 3D Game ######################################################
import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr


pygame.init()

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT),
                                    pygame.DOUBLEBUF|pygame.OPENGL)
CLOCK = pygame.time.Clock()
pygame.mouse.set_visible(False)

################ OpenGL Setup #################################################
glClearColor(0.5,0.5,0.5,1)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
glEnable(GL_DEPTH_TEST)
glEnable(GL_CULL_FACE)
glCullFace(GL_BACK)
TEXTURE_RESOLUTION = 32

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

glUniform1i(glGetUniformLocation(shader,"material.diffuse"),0)
glUniform1i(glGetUniformLocation(shader,"material.specular"),1)

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
                tex = TEXTURES["wall"][l[6]]
                w = Wall(pos_a,pos_b,z,height,tex)
                GAME_OBJECTS.append(w)
                RESTRICTED.append(w)
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
                tex = TEXTURES["floor"][l[9]]
                floor = Floor(pos_a,pos_b,pos_c,pos_d,z,tex)
                GAME_OBJECTS.append(floor)
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
                tex = TEXTURES["ceiling"][l[9]]
                c = Ceiling(pos_a,pos_b,pos_c,pos_d,z,tex)
                GAME_OBJECTS.append(c)
            elif line[0]=='l':
                #light
                # l(x,y,z,r,g,b)
                beginning = line.find('(')
                line = line[beginning+1:-2].replace('\n','').split(',')
                l = [int(item) for item in line]
                position = np.array([l[0],l[1],l[2]],dtype=np.float32)
                colour = np.array([l[3],l[4],l[5]],dtype=np.float32)
                light = Light(position,colour)
                GAME_OBJECTS.append(light)
            elif line[0]=='p':
                #player
                # p(x,y,direction)
                line = line[2:-2].replace('\n','').split(',')
                l = [int(item) for item in line]
                player = Player(np.array([l[0],l[1],16],dtype=np.float32),l[2])
                GAME_OBJECTS.append(player)
            line = f.readline()
        return player

def importTextures(filename):
    with open(filename,'r') as f:
        line = f.readline()
        while line:
            if line[0]=='w':
                target = TEXTURES["wall"]
            elif line[0]=='f':
                target = TEXTURES["floor"]
            else:
                target = TEXTURES["ceiling"]
            beginning = line.find('(')
            line = line[beginning+1:-2].replace('\n','').split(',')
            ambient = float(line[0])
            diffuse = line[1]
            specular = line[2]
            shininess = int(line[3])

            target.append(Material(ambient,diffuse,specular,shininess))
            
            line = f.readline()

def clearLights():
    for i in range(MAX_LIGHTS):
        glUniform1fv(glGetUniformLocation(shader,f'pointLights[{i}].isOn'),1,False)

def checkCollisions(pointA,pointB):
    """
        Reference: https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
    """
    for wall in RESTRICTED:
        x3 = wall.pos_a[0] + wall.position[0]
        y3 = wall.pos_a[1] + wall.position[1]
        x4 = wall.pos_b[0] + wall.position[0]
        y4 = wall.pos_b[1] + wall.position[1]

          
        # Find the 4 orientations required for  
        # the general and special cases 
        o1 = orientation(pointA, pointB, (x3,y3)) 
        o2 = orientation(pointA, pointB, (x4,y4)) 
        o3 = orientation((x3,y3), (x4,y4), pointA) 
        o4 = orientation((x3,y3), (x4,y4), pointB) 
  
        # General case 
        if ((o1 != o2) and (o3 != o4)):
            #check foot
            if (wall.z + wall.height)<(player.position[2]):
                if (wall.z + wall.height)>(player.position[2]-player.height+4):
                    return True
                else:
                    continue
            #check head
            if wall.z>player.position[2]:
                continue
            #otherwise it's a regular wall
            return True
    return False

def orientation(p, q, r): 
    # to find the orientation of an ordered triplet (p,q,r) 
    # function returns the following values: 
    # 0 : Colinear points 
    # 1 : Clockwise points 
    # 2 : Counterclockwise 
      
    # See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/  
    # for details of below formula.  
      
    val = (float(q[1] - p[1]) * (r[0] - q[0])) - (float(q[0] - p[0]) * (r[1] - q[1])) 
    if (val > 0): 
          
        # Clockwise orientation 
        return 1
    elif (val < 0): 
          
        # Counterclockwise orientation 
        return 2
    else: 
          
        # Colinear orientation 
        return 0

################ Classes ######################################################

class Player:
    def __init__(self,position,direction):
        self.position = position
        self.theta = direction
        self.phi = 0
        pygame.mouse.set_pos(SCREEN_WIDTH/2,SCREEN_HEIGHT/2)
        self.speed = 1
        self.height = 30
    
    def update(self):
        #take inputs
        keystate = pygame.key.get_pressed()
        walk_direction = 0
        walking = False

        #mouse
        new_pos = pygame.mouse.get_pos()
        pygame.mouse.set_pos(SCREEN_WIDTH/2,SCREEN_HEIGHT/2)
        self.theta -= t*(new_pos[0] - SCREEN_WIDTH/2)/15
        self.theta = self.theta%360
        self.phi -= t*(new_pos[1] - SCREEN_HEIGHT/2)/15
        self.phi = min(max(self.phi,-90),90)

        self.look()

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
        
        if walking:
            self.walk(walk_direction)

        projection_matrix = pyrr.matrix44.create_perspective_projection(45,SCREEN_WIDTH/SCREEN_HEIGHT,1,280,dtype=np.float32)
        glUniformMatrix4fv(glGetUniformLocation(shader,"projection"),1,GL_FALSE,projection_matrix)
        glUniform3fv(glGetUniformLocation(shader,"viewPos"),1,self.position)
    
    def walk(self,walk_direction):
        actual_direction = self.theta + walk_direction
        cos_ad = np.cos(np.radians(actual_direction),dtype=np.float32)
        sin_ad = np.sin(np.radians(actual_direction),dtype=np.float32)

        temp = np.array([0,0,0],dtype=np.float32)

        if not checkCollisions(self.position,self.position+8*np.array([cos_ad,0,0],dtype=np.float32)):
            temp += self.speed*t*np.array([cos_ad,0,0],dtype=np.float32)/20
        
        if not checkCollisions(self.position,self.position+8*np.array([0,sin_ad,0],dtype=np.float32)):
            temp += self.speed*t*np.array([0,sin_ad,0],dtype=np.float32)/20
        
        self.position += temp
    
    def look(self):
        cos_phi = np.cos(np.radians(self.phi),dtype=np.float32)
        sin_phi = np.sin(np.radians(self.phi),dtype=np.float32)
        cos_theta = np.cos(np.radians(self.theta),dtype=np.float32)
        sin_theta = np.sin(np.radians(self.theta),dtype=np.float32)

        #get lookat
        look_direction = np.array([cos_phi*cos_theta,cos_phi*sin_theta,sin_phi],dtype=np.float32)
        up = np.array([0,0,1],dtype=np.float32)
        camera_right = pyrr.vector3.cross(up,look_direction)
        camera_up = pyrr.vector3.cross(look_direction,camera_right)

        lookat_matrix = pyrr.matrix44.create_look_at(self.position,self.position + look_direction, camera_up, dtype=np.float32)
        glUniformMatrix4fv(glGetUniformLocation(shader,"view"),1,GL_FALSE,lookat_matrix)

    def draw(self):
        pass

class Wall:
    def __init__(self,pos_a,pos_b,z,height,texture):
        self.z = z
        self.position = np.array([pos_a[0],pos_a[1],self.z],dtype=np.float32)
        a_length = pyrr.vector.length(pos_a)
        wall_length = pyrr.vector.length(pos_b - pos_a)
        self.model = pyrr.matrix44.create_from_translation(self.position,dtype=np.float32)
        self.pos_a = np.array([0,0,0],dtype=np.float32)
        self.pos_b = pos_b - pos_a
        self.height = height
        self.texture = texture

        #calculate normal by hand
        u = np.array([pos_b[0]-pos_a[0],pos_b[1]-pos_a[1],self.z],dtype=np.float32)
        v = np.array([pos_b[0]-pos_a[0],pos_b[1]-pos_a[1],self.z+self.height],dtype=np.float32)
        self.normal = pyrr.vector.normalise(pyrr.vector3.cross(u,v))

        self.vertices = (self.pos_a[0], self.pos_a[1], 0,               self.normal[0], self.normal[1], self.normal[2], a_length/TEXTURE_RESOLUTION,    (self.z+self.height)/TEXTURE_RESOLUTION,
                         self.pos_b[0], self.pos_b[1], 0,               self.normal[0], self.normal[1], self.normal[2], wall_length/TEXTURE_RESOLUTION, (self.z+self.height)/TEXTURE_RESOLUTION,
                         self.pos_b[0], self.pos_b[1], self.height,     self.normal[0], self.normal[1], self.normal[2], wall_length/TEXTURE_RESOLUTION,  self.z/TEXTURE_RESOLUTION,
                         self.pos_a[0], self.pos_a[1], self.height,     self.normal[0], self.normal[1], self.normal[2], a_length/TEXTURE_RESOLUTION,     self.z/TEXTURE_RESOLUTION)
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
        self.texture.use()
        glUniformMatrix4fv(glGetUniformLocation(shader,"model"),1,GL_FALSE,self.model)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_FAN,0,4)

class Floor:
    def __init__(self,pos_a,pos_b,pos_c,pos_d,z,texture):
        self.z = z
        self.position = np.array([pos_a[0],pos_a[1],self.z],dtype=np.float32)
        self.model = pyrr.matrix44.create_from_translation(self.position,dtype=np.float32)
        self.pos_a = np.array([0,0,0],dtype=np.float32)
        self.pos_b = pos_b - pos_a
        self.pos_c = pos_c - pos_a
        self.pos_d = pos_d - pos_a
        self.texture = texture

        self.vertices = (self.pos_a[0], self.pos_a[1], 0, 0.0, 0.0, 1.0,  self.position[0]/TEXTURE_RESOLUTION,                   self.position[1]/TEXTURE_RESOLUTION,
                         self.pos_b[0], self.pos_b[1], 0, 0.0, 0.0, 1.0, (self.position[0] + self.pos_b[0])/TEXTURE_RESOLUTION, (self.position[1] + self.pos_b[1])/TEXTURE_RESOLUTION,
                         self.pos_c[0], self.pos_c[1], 0, 0.0, 0.0, 1.0, (self.position[0] + self.pos_c[0])/TEXTURE_RESOLUTION, (self.position[1] + self.pos_c[1])/TEXTURE_RESOLUTION,
                         self.pos_d[0], self.pos_d[1], 0, 0.0, 0.0, 1.0, (self.position[0] + self.pos_d[0])/TEXTURE_RESOLUTION, (self.position[1] + self.pos_d[1])/TEXTURE_RESOLUTION)
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
        self.texture.use()
        glUniformMatrix4fv(glGetUniformLocation(shader,"model"),1,GL_FALSE,self.model)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_FAN,0,4)

class Ceiling:
    def __init__(self,pos_a,pos_b,pos_c,pos_d,z,texture):
        self.z = z
        self.position = np.array([pos_a[0],pos_a[1],self.z],dtype=np.float32)
        self.model = pyrr.matrix44.create_from_translation(self.position,dtype=np.float32)
        self.pos_a = np.array([0,0,0],dtype=np.float32)
        self.pos_b = pos_b - pos_a
        self.pos_c = pos_c - pos_a
        self.pos_d = pos_d - pos_a
        self.texture = texture

        self.vertices = (self.pos_a[0], self.pos_a[1], 0, 0.0, 0.0, -1.0,  self.position[0]/TEXTURE_RESOLUTION,                   self.position[1]/TEXTURE_RESOLUTION,
                         self.pos_b[0], self.pos_b[1], 0, 0.0, 0.0, -1.0, (self.position[0] + self.pos_b[0])/TEXTURE_RESOLUTION, (self.position[1] + self.pos_b[1])/TEXTURE_RESOLUTION,
                         self.pos_c[0], self.pos_c[1], 0, 0.0, 0.0, -1.0, (self.position[0] + self.pos_c[0])/TEXTURE_RESOLUTION, (self.position[1] + self.pos_c[1])/TEXTURE_RESOLUTION,
                         self.pos_d[0], self.pos_d[1], 0, 0.0, 0.0, -1.0, (self.position[0] + self.pos_d[0])/TEXTURE_RESOLUTION, (self.position[1] + self.pos_d[1])/TEXTURE_RESOLUTION)
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
        self.texture.use()
        glUniformMatrix4fv(glGetUniformLocation(shader,"model"),1,GL_FALSE,self.model)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_FAN,0,4)

class Light:
    def __init__(self,position,colour):
        self.position = position
        self.colour = colour
        self.active = True
        
    def update(self):
        global current_lights
        if self.active and current_lights<MAX_LIGHTS:
            glUniform1fv(glGetUniformLocation(shader,f'pointLights[{current_lights}].isOn'),1,True)

            glUniform3fv(glGetUniformLocation(shader,f'pointLights[{current_lights}].position'),1,self.position)
            glUniform1fv(glGetUniformLocation(shader,f'pointLights[{current_lights}].strength'),1,1)

            glUniform1fv(glGetUniformLocation(shader,f'pointLights[{current_lights}].constant'),1,1.0)
            glUniform1fv(glGetUniformLocation(shader,f'pointLights[{current_lights}].linear'),1,0.045)
            glUniform1fv(glGetUniformLocation(shader,f'pointLights[{current_lights}].quadratic'),1,0.0075)

            glUniform3fv(glGetUniformLocation(shader,f'pointLights[{current_lights}].ambient'),1,0.05*self.colour)
            glUniform3fv(glGetUniformLocation(shader,f'pointLights[{current_lights}].diffuse'),1,1.0*self.colour)
            glUniform3fv(glGetUniformLocation(shader,f'pointLights[{current_lights}].specular'),1,0.6*self.colour)
            current_lights += 1
    
    def draw(self):
        pass

class Material:
    def __init__(self,ambient,diffuse,specular,shininess):
        #ambient
        self.ambient = np.array([ambient,ambient,ambient],dtype=np.float32)

        #diffuse
        self.diffuse = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,self.diffuse)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        image = pygame.image.load(diffuse)
        image_width, image_height = image.get_rect().size
        image_data = pygame.image.tostring(image,"RGBA")
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,image_data)

        #specular
        self.specular = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,self.specular)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        image = pygame.image.load(diffuse)
        image_width, image_height = image.get_rect().size
        image_data = pygame.image.tostring(image,"RGBA")
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,image_data)

        #shininess
        self.shininess = 32

    def use(self):
        glUniform3fv(glGetUniformLocation(shader,"material.ambient"),1,self.ambient)
        glUniform1fv(glGetUniformLocation(shader,"material.shininess"),1,self.shininess)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.diffuse)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D,self.specular)

################ Game Objects #################################################
GAME_OBJECTS = []
RESTRICTED = []
TEXTURES = {"floor":[],"wall":[],"ceiling":[]}
importTextures('textures.txt')
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
    for obj in GAME_OBJECTS:
        obj.update()
    ################ Render ###################################################
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    for obj in GAME_OBJECTS:
        obj.draw()
    ################ Framerate ################################################
    t = CLOCK.get_time()
    CLOCK.tick()
    fps = CLOCK.get_fps()
    pygame.display.set_caption("Running at "+str(int(fps))+" fps")
    pygame.display.flip()
