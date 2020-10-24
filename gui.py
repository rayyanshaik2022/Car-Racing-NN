import pygame
import pygame.gfxdraw

from game import *
from settings import *


class Gui:
    def __init__(self, pop):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(TITLE)

        self.font = pygame.font.Font(pygame.font.get_default_font(), 25)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.nets = None

        self.pop = pop
        self.pop.train(True)

        nets = pop.population[:5]
        self.nets = nets

    def new(self):
        cars = [Car((0,0), CAR_SIZE) for i in range(len(self.nets))]
        self.game = Game(cars, MAP)

    def run(self):
        self.playing = True
        self.playing_generation = True
        while self.playing:
            if self.playing_generation:
                self.dt = self.clock.tick(FPS) / 1000 # Controls update speed (FPS per second)
                self.events()
                self.update()          
                self.close()
            else:
                self.pop.train(True)
                self.new()
                nets = self.pop.population[:5]
                self.nets = nets
                self.playing_generation = True

            self.draw()

            
            

    def close(self):

        if all(not car.alive for car in self.game.cars):
            self.playing_generation = False

    def update(self):

        pygame.display.set_caption(f"{TITLE} | FPS {round(self.clock.get_fps(),2)}")

        for i, car in enumerate(self.game.cars):
            move = self.nets[i].get_move(car)
            self.game.controller(i, move)

        self.game.update()

        '''
        # random movement
        for i, car in enumerate(self.game.cars):
            self.game.controller(i, random.choice(Game.MOVES))
        '''

    def draw(self):
        self.screen.fill(COLORS['grass'])

        pygame.draw.polygon(self.screen, COLORS["track"], self.game.map["exterior_poly"])
        pygame.draw.polygon(self.screen, COLORS["grass"], self.game.map["interior_poly"])

        # Draw end checkpoint
        last_checkpoint = self.game.map['checkpoints'][-1]
        pygame.draw.line(self.screen, COLORS['red'], last_checkpoint[0], last_checkpoint[1], 2)

        for car in self.game.cars:
            car.draw(self.screen)

        text = self.font.render(f"Generation: {self.pop.current_generation-1}", True, Color("#000000"))
        self.screen.blit(text, (15,15))
      
        pygame.display.flip()

    def events(self):
        # catch all events here
        keys_pressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pass
        
        # Manual user input - this will affect thow the agents move!
        if keys_pressed[pygame.K_RIGHT]:
            for car in self.game.cars:
                car.direction += math.pi/Car.TURN_SPEED
        if keys_pressed[pygame.K_LEFT]:
            for car in self.game.cars:
                car.direction -= math.pi/Car.TURN_SPEED
        if keys_pressed[pygame.K_UP]:
            for car in self.game.cars:
                car.speed += Car.ACCELERATION
        if keys_pressed[pygame.K_DOWN]:
            for car in self.game.cars:
                car.speed -= Car.ACCELERATION * 2
