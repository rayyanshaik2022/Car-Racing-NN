from pygame.math import Vector2 as Vector
import pygame.gfxdraw
from pygame import Color
from math import sin, cos, atan2, pi

class Game:

    TURN_RIGHT = "turn_right"
    TURN_LEFT = "turn_left"
    ACCELERATE = "accelerate"
    BRAKE = "brake"
    IDLE = "idle"

    def __init__(self, car):
        self.timer = 0
        self.car = car
    
    def update(self):
        self.timer += 1
        self.update_car()

    def update_car(self):

        car = self.car

         #Vector2 frontWheel = carLocation + wheelBase/2 * new Vector2( cos(carHeading) , sin(carHeading) );
        #Vector2 backWheel = carLocation - wheelBase/2 * new Vector2( cos(carHeading) , sin(carHeading) 
        
        if car.speed > car.MAX_SPEED:
            car.speed = car.MAX_SPEED
        if car.speed < 0:
            car.speed = 0

        front_wheel = car.pos + car.wheel_base * Vector(cos(car.direction), sin(car.direction))
        back_wheel = car.pos - car.wheel_base * Vector(cos(car.direction), sin(car.direction))
        
        #backWheel += carSpeed * dt * new Vector2(cos(carHeading) , sin(carHeading));
        #frontWheel += carSpeed * dt * new Vector2(cos(carHeading+steerAngle) , sin(carHeading+steerAngle)
        dt = 1
        front_wheel += car.speed * dt * Vector(cos(car.direction), sin(car.direction))
        back_wheel += car.speed * dt * Vector(cos(car.direction+car.steer_angle), sin(car.direction+car.steer_angle))
        
        #carLocation = (frontWheel + backWheel) / 2;
        #carHeading = atan2( frontWheel.Y - backWheel.Y , frontWheel.X - backWheel.X );

        car.pos = (front_wheel + back_wheel)/2
        car.direction = atan2(front_wheel.y-back_wheel.y, front_wheel.x-back_wheel.x)


class Car:

    MAX_SPEED = 5
    ACCELERATION = 0.05
    TURN_SPEED = 60

    def __init__(self, pos, size):

        self.pos = Vector(*pos)
        self.direction = pi
        self.speed = 0
        self.acceleration = Car.ACCELERATION
        self.steer_angle = 0
        self.size = size
        self.wheel_base = size/2

    def calculate_polygon(self):

        p1 = [-self.size/4, -self.size/2]
        p2 = [self.size/4, -self.size/2]
        p3 = [self.size/4, self.size/2]
        p4 = [-self.size/4, self.size/2]

        points = [p1, p2, p3, p4]
        for i, p in enumerate(points):
            points[i] = [p[0]*cos(self.direction+pi/2) - p[1]*sin(self.direction+pi/2), p[0]*sin(self.direction+pi/2)+p[1]*cos(self.direction+pi/2)]   
            points[i][0] += self.pos.x
            points[i][1] += self.pos.y

        return points
    
    def draw(self, screen):

        pygame.gfxdraw.polygon(screen, self.calculate_polygon(), Color("#0000FF"))