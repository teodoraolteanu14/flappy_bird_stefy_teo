import pygame
from pygame.locals import *
import random

pygame.init()

# ensure the game runs as the same rate
clock = pygame.time.Clock()
fps = 60  # frames per second

# create the game window and set the caption
screen_width = 864
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird - Stefy & Teo')

# define font
font = pygame.font.SysFont('Bauhaus 93', 60)
# define colors
white = (255, 255, 255)

# game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False

# we load the images
bg = pygame.image.load('img/bg_nou.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')


def draw_text(text, text_font, color, x, y):
    img = text_font.render(text, True, color)
    screen.blit(img, (x, y))


# reset the game
def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)  # allows inheriting functionalities
        self.images = []
        self.index = 0
        self.counter = 0
        # we load each image of the bird, making the animation effect
        for num in range(1, 4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()  # create a rectangle from the boundaries of the img
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        # gravity
        if flying == True:
            self.vel += 0.5
            # limit the speed
            if (self.vel > 8):
                self.vel = 8
            if self.rect.bottom < 640:
                self.rect.y += int(self.vel)

        # while the bird is flying, it's not game over
        if game_over == False:
            # jump
            # verify if it was clicked only once
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # handle the animation
            self.counter += 1
            flap_cooldown = 25
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0  # animation is complete and we start again
            self.image = self.images[self.index]

            # rotate the bird
            # second variable is the angle of rotation (clockwise)
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            # point the bird towards the ground
            # game over
            self.image = pygame.transform.rotate(self.images[self.index], -90)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()
        # position 1 is from the top, -1 is from the bottom
        # have some space between the pipes
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        # move the pipe at the same speed as the ground
        self.rect.x -= scroll_speed
        # delete the pipe if it goes off the screen
        if self.rect.right < 0:
            self.kill()


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        # check if the mouse is over the button
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            # the mouse is being clicked
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        # draw the button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action


bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

# restart button instance
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)

run = True


def jump():
    global flying, game_over
    if flying == False and game_over == False:
        flying = True
    if game_over == False:
        flappy.vel = -10  # Set the velocity for jump


# game loop
while run:
    clock.tick(fps)

    # show the background on the screen
    screen.blit(bg, (0, 0))

    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)

    # draw the ground
    screen.blit(ground_img, (ground_scroll, 640))

    # check the score
    if len(pipe_group) > 0:
        # if the bird is between the left and right side of the pipe, it has passed it
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            # if the bird passed the right side of the pipe, increase the score
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False
    draw_text(str(score), font, white, int(screen_width / 2), 20)

    # look for collision with the pipes and if the bird is above the screen
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True
    # check if the bird hit the ground
    if flappy.rect.bottom >= 640:
        game_over = True
        flying = False

    # if the bird has hit the ground, stop scrolling/generating pipes
    if game_over == False and flying == True:
        time_now = pygame.time.get_ticks()
        # if enough time has passed since the last pipe was generated
        if time_now - last_pipe > pipe_frequency:
            # generate pipes at random heights
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            # update the last pipe time
            last_pipe = time_now

        # draw and scroll the ground and the pipes
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0
        pipe_group.update()

    # reset when the game is over
    if game_over == True:
        if button.draw() == True:
            game_over = False
            # the score is also being reset
            score = reset_game()

    for event in pygame.event.get():
        # stops running when closing the window
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            jump()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                jump()
    pygame.display.update()  # gets everything updated

pygame.quit()
