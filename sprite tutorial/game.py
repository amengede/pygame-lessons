import pygame

pygame.init()
screen = pygame.display.set_mode((300,200))
clock = pygame.time.Clock()
GREEN = (0,255,0)
RED = (255,0,0)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((20, 20))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (150, 100)
    
    def update(self):
        self.rect.x += 5
        if self.rect.left > 300:
            self.rect.right = 0

all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Update
    all_sprites.update()

    # Draw / render
    screen.fill(GREEN)
    all_sprites.draw(screen)
    pygame.display.update()

    clock.tick(60)

pygame.quit()