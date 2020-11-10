import pygame, sys # import pygame and sys
 
clock = pygame.time.Clock() # set up the clock
 
from pygame.locals import * # import pygame modules
pygame.init() # initiate pygame
 
pygame.display.set_caption('Pygame Window') # set the window name
 
WINDOW_SIZE = (600,400) # set up window size
 
screen = pygame.display.set_mode(WINDOW_SIZE,0,32) # initiate screen
game_map = [['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','2','2','2','2','2','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['2','2','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','2','2'],
            ['1','1','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1']]
grass = pygame.transform.scale(pygame.image.load('grass.png'), (int(WINDOW_SIZE[0]/len(game_map[0])), int(WINDOW_SIZE[1]/len(game_map))))
dirt = pygame.transform.scale(pygame.image.load('dirt.png'), (int(WINDOW_SIZE[0]/len(game_map[0])), int(WINDOW_SIZE[1]/len(game_map))))
TILE_WIDTH = grass.get_width()
tiles = []
TILE_HEIGHT = grass.get_height()
class Player:
    def __init__(self):
        self.x = 20
        self.speed = 1
        self.directions = {'down': True, 'left': True, 'up':True,'right':True}
        self.y = 100
        self.y_momentum = 0
        self.ground_y = 0
        self._image = pygame.transform.scale(pygame.image.load('player.png'), (15,45))
        self.rect = pygame.Rect(self.x,self.y,self._image.get_width(),self._image.get_height())
        self.direction = 'right'
    def update(self):
        self.rect = pygame.Rect(self.x,self.y,self._image.get_width(),self._image.get_height())
    def draw(self):
        screen.blit(self._image,(self.x,self.y))
    def tileCollisions(self,tiles):
        self.directions = {'down': True, 'left': True, 'up':False,'right':True}
        for tile in tiles:
            #if the player isn't colliding at their current position, but moving
            #would cause a collision, then set it so the player can't move.
            original_rect = self.rect
            left_rect = self.rect.move(-self.speed,0)
            right_rect = self.rect.move(self.speed,0)
            vert_rect = self.rect.move(0,self.y_momentum)
            ground_check = self.rect.move(0,1)
            top_check = self.rect.move(0,-1)

            if not original_rect.colliderect(tile['rect']):
                if right_rect.colliderect(tile['rect']):
                    self.directions['right'] =  False
                if left_rect.colliderect(tile['rect']):
                    self.directions['left'] = False
            
            if ground_check.colliderect(tile['rect']):
                self.y = tile['rect'].y - self._image.get_height()
                self.directions['up'] = True
                self.directions['down'] = False
                self.y_momentum = 0
            
            if top_check.colliderect(tile['rect']):
                self.directions['up'] = False
                self.y_momentum *= -1

        #print(self.directions)
player = Player()
while True: # game loop
    """option 1: add tile info outside game loop
    option 2: add tile info inside game loop then clear info each frame"""
    screen.fill((146,244,255)) # clear screen by filling it with blue
    y = 0
    for arr in game_map:
        x = 0
        for num in arr:
            if num == '1':
                screen.blit(dirt, (x * TILE_WIDTH, y * TILE_HEIGHT,TILE_WIDTH,TILE_HEIGHT))
                image = dirt
            elif num == '2':
                screen.blit(grass, (x * TILE_WIDTH, y * TILE_HEIGHT,TILE_WIDTH,TILE_HEIGHT))
                image = grass
                tiles.append({'rect':Rect(x*TILE_WIDTH,y*TILE_HEIGHT,TILE_WIDTH,TILE_HEIGHT), 'image': image})
            x += 1
        y += 1
    for event in pygame.event.get(): # event loop
        if event.type == QUIT: # check for window quit
            pygame.quit() # stop pygame
            sys.exit() # stop script
    keys = pygame.key.get_pressed()
    player.tileCollisions(tiles)
    if keys[K_LEFT] and player.directions['left']:
        player.direction = 'left'
        player.x -= player.speed
    if keys[K_RIGHT] and player.directions['right']:
        player.direction = 'right'
        player.x += player.speed
    if keys[K_UP] and player.directions['up']:
        player.y_momentum = -5
        player.directions['down'] = True
    if player.directions['down']:
        player.y += player.y_momentum
        player.y_momentum += 0.2
    player.update()
    player.draw()
    pygame.display.update() # update display
    clock.tick(60)
    fps = clock.get_fps()
    pygame.display.set_caption("Running at "+str(int(fps))+" fps")
    tiles = []