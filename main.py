import pygame
import pygame.gfxdraw
from game import *
from settings import *
import random
import math


class Gui:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

    def new(self):
        car = Car((400,400), 50)
        self.game = Game(car)

    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000 # Controls update speed (FPS per second)
            self.events()
            self.update()
            self.draw()

    def close(self):
        pygame.quit()
        quit()

    def update(self):

        pygame.display.set_caption(f"{TITLE} | FPS {round(self.clock.get_fps(),2)}")
        self.game.update()


    def draw(self):
        self.screen.fill(COLORS['background'])


        self.game.car.draw(self.screen)
      
        pygame.display.flip()

    def events(self):
        # catch all events here
        keys_pressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pass
        
        
        if keys_pressed[pygame.K_RIGHT]:
            if keys_pressed[pygame.K_RIGHT]:
                self.game.car.direction += math.pi/Car.TURN_SPEED
        if keys_pressed[pygame.K_LEFT]:
            self.game.car.direction -= math.pi/Car.TURN_SPEED
        if keys_pressed[pygame.K_UP]:
            self.game.car.speed += Car.ACCELERATION
        if keys_pressed[pygame.K_DOWN]:
            self.game.car.speed -= Car.ACCELERATION * 2
        


# create the game object
g = Gui()
g.new()
g.run()