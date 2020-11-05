# http://kidscancode.org/lessons/
# http://opengameart.org
# open audio library: https://pypi.org/project/PyOpenAL/
import pygame
import random
from openal import *

WIDTH = 480
HEIGHT = 600
FPS = 60

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# initialize pygame and create window
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shmup!")
clock = pygame.time.Clock()

#images
""" Surface: array of 32 bit numbers. 32 bits = 4 bytes, typically (R,G,B,A) form.
Surface stores data, that's it. Blit copies data from one surface to another.

Rectangle: collection of numbers representing a 2D rectangle. (Left,Top,Width,Height)
Rectangle describes positions/regions. Used for collision checks and to specify
regions of the screen to blit surfaces to.
"""
background = pygame.image.load("gfx/starfield.png").convert()
background_rect = background.get_rect()
player_img = pygame.image.load("gfx/playerShip1_orange.png").convert()
player_img.set_colorkey(BLACK)
meteor_img = pygame.image.load("gfx/meteorBrown_med1.png").convert()
meteor_img.set_colorkey(BLACK)
bullet_img = pygame.image.load("gfx/laserRed16.png").convert()
bullet_img.set_colorkey(BLACK)

# sfx
# 16bit, 44100
sfx_music = oalOpen("sfx/Master of Puppets.wav")
sfx_music.set_gain(0.5)
sfx_music.play()
sfx_shoot = oalOpen("sfx/shoot.wav")
sfx_shoot.set_gain(0.5)
sfx_destroy = oalOpen("sfx/hit.wav")
sfx_destroy.set_gain(0.25)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #scale the image down to have width = 50, height = 38
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.radius = int(self.rect.width * .85 / 2)

    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
    
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        size = random.randrange(10, 50)
        self.image = pygame.transform.scale(meteor_img, (size, size))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.radius = int(self.rect.width * .85 / 2)
        self.mask = pygame.mask.from_surface(self.image)
    
    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)
            self.speedx = random.randrange(-3, 3)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (10, 20))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.y += self.speedy
        # kill if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()

all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
mobs = pygame.sprite.Group()

for i in range(8):
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

# Game loop
running = True
while running:
    # keep loop running at the right speed
    clock.tick(FPS)
    # Process input (events)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                sfx_shoot.play()
                player.shoot()

    # Update
    all_sprites.update()

    # Collision checks
    """groupcollide(group1,group2, dokill1, dokill2, collision_test)
        Check two groups for collisions between members. Return the dictionary
        of group1 members which collided, in the form {sprite1:[sprite2a,sprite2b,...]}, or empty dictionary.
        If dokill1 and dokill2 specify whether the members from group 1 or 2 should be killed (or both)
        collision_test is the type of test routine to use
    """
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True, pygame.sprite.collide_circle)
    for hit in hits:
        sfx_destroy.play()
        #asteroid has been destroyed, create new one
        m = Mob()
        all_sprites.add(m)
        mobs.add(m)

    """spritecollide(sprite, group, dokill, collision_test)
        Check all members of group for collision with sprite. Return the list
        of group members which collided, or empty list.
        If dokill=True, kill all group members which collided with the sprite
        collision_test is the type of test routine to use
    """
    hits = pygame.sprite.spritecollide(player, mobs, False, pygame.sprite.collide_mask)
    if hits:
        running = False

    # Draw / render
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    # *after* drawing everything, flip the display
    pygame.display.flip()

pygame.quit()
oalQuit()