# tutorial: http://kidscancode.org/lessons/
# graphics: http://opengameart.org
# open audio library: https://pypi.org/project/PyOpenAL/
# sound effect generation: https://www.bfxr.net/
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
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)

meteor_img = pygame.image.load("gfx/meteorBrown_med1.png").convert()
meteor_img.set_colorkey(BLACK)

bullet_img = pygame.image.load("gfx/laserRed16.png").convert()
bullet_img.set_colorkey(BLACK)

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = f'gfx/regularExplosion0{i}.png'
    img = pygame.image.load(filename).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = f'gfx/sonicExplosion0{i}.png'
    img = pygame.image.load(filename).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

# sfx
# 16bit, 44100
sfx_music = oalOpen("sfx/Master of Puppets.wav")
sfx_music.set_gain(0.5)
#sfx_music.play()
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
        self.shield = 100
        self.radius = int(self.rect.width * .85 / 2)
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()

    def update(self):
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
	        self.hidden = False
	        self.rect.centerx = WIDTH // 2
	        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            sfx_shoot.play()
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)

    def hide(self):
        # hide the player temporarily
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH // 2, HEIGHT + 200)

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        size = random.randrange(10, 50)
        self.original_image = pygame.transform.scale(meteor_img, (size, size))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 4)
        self.speedx = random.randrange(-1, 1)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()
        self.radius = int(self.rect.width * .85 / 2)
        self.mask = pygame.mask.from_surface(self.image)
    
    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)
            self.speedx = random.randrange(-3, 3)

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.original_image, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = new_image.get_rect()
            self.rect.center = old_center
            self.mask = pygame.mask.from_surface(self.image)

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

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center
    
font_name = pygame.font.match_font('arial')
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = int((pct / 100) * BAR_LENGTH)
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, BLACK, outline_rect, 2)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
mobs = pygame.sprite.Group()

for i in range(8):
    newmob()
score = 0

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

    # Update
    all_sprites.update()

    # Collision checks
    """groupcollide(group1,group2, dokill1, dokill2, collision_test)
        Check two groups for collisions between members. Return the dictionary
        of group1 members which collided, in the form {sprite1:[sprite2a,sprite2b,...]}, or empty dictionary.
        If dokill1 and dokill2 specify whether the members from group 1 or 2 should be killed (or both)
        collision_test is the type of test routine to use
    """
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True, pygame.sprite.collide_mask)
    for hit in hits:
        sfx_destroy.play()
        #asteroid has been destroyed, create new one
        score += 50 - hit.radius
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        newmob()

    """spritecollide(sprite, group, dokill, collision_test)
        Check all members of group for collision with sprite. Return the list
        of group members which collided, or empty list.
        If dokill=True, kill all group members which collided with the sprite
        collision_test is the type of test routine to use
    """
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        newmob()
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100
    if player.lives == 0 and not death_explosion.alive():
        running = False

    # Draw / render
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, "Score: "+str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)
    # *after* drawing everything, flip the display
    pygame.display.flip()

pygame.quit()
oalQuit()