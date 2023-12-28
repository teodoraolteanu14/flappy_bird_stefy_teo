import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60
screen_width = 864
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird - Stefy & Teo')

#define font
font = pygame.font.SysFont('Bauhaus 93', 60)
#define colors
white = (255, 255, 255)

#game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500 #milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False


bg = pygame.image.load('img/bg_nou.png')
ground_img = pygame.image.load('img/ground.png')

def draw_text(text, text_font, color, x, y):
    img = text_font.render(text, True, color)
    screen.blit(img, (x, y))

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False
    def update(self):
        #gravity
        if flying == True:
            self.vel += 0.5
             #limit the speed
            if(self.vel > 8):
                self.vel = 8
            if self.rect.bottom < 640:
                self.rect.y += int(self.vel)

        #while the bird is flying, it's not game over
        if game_over == False:
            #jump
            #verify if it was clicked only once
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            #handle the animation
            self.counter += 1
            flap_cooldown = 25
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            #rotate the bird
            #second variable is the angle of rotation (clockwise)
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            #point the bird towards the ground
            #game over
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y,position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()
        #position 1 is from the top, -1 is from the bottom
        #have some space between the pipes
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap/2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap/2)]
    def update(self):
        #move the pipe at the same speed as the ground
        self.rect.x -= scroll_speed
        #delete the pipe if it goes off the screen
        if self.rect.right < 0:
            self.kill()


bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

run = True
while run:
    clock.tick(fps)

    screen.blit(bg, (0, 0))

    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)


    # draw the ground
    screen.blit(ground_img, (ground_scroll, 640))

    #check the score
    if len(pipe_group) > 0:
        #if the bird is between the left and right side of the pipe, it has passed it
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
                and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            #if the bird passed the right side of the pipe, increase the score
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False
    draw_text(str(score), font, white, int(screen_width / 2), 20)

    #look for collision with the pipes and if the bird is above the screen
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True
    #check if the bird hit the ground
    if flappy.rect.bottom >= 640:
        game_over = True
        flying = False

    #if the bird has hit the ground, stop scrolling/generating pipes
    if game_over == False and flying == True:
        time_now = pygame.time.get_ticks()
        #if enough time has passed since the last pipe was generated
        if time_now - last_pipe > pipe_frequency:
            # generate pipes at random heights
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            #update the last pipe time
            last_pipe = time_now

        # draw and scroll the ground and the pipes
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0
        pipe_group.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True
    pygame.display.update()

pygame.quit()
