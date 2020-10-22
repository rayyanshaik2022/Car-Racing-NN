from pygame.math import Vector2 as Vector
import pygame.gfxdraw
from pygame import Color
from math import sin, cos, atan2, pi
from settings import *
import json
from shapely.geometry import Polygon, LineString
from shapely.coords import CoordinateSequence

def points_to_mesh(points : list) -> list:
    """
    Converts list of points to a list of lines
    that form a polygon
    """

    if len(points) < 3:
        return None
    
    lines = []
    last_index = len(points)-1

    for i, point in enumerate(points):
        if i != last_index:
            lines.append( (point, points[i]) )
        else:
            # do here

class Game:

    TURN_RIGHT = "turn_right"
    TURN_LEFT = "turn_left"
    ACCELERATE = "accelerate"
    BRAKE = "brake"
    IDLE = "idle"

    def __init__(self, cars, map_file):
        self.timer = 0
        self.cars = cars

        with open(map_file, 'r') as f:
            self.map = json.load(f)
            print("> Successfully loaded map")
        
        self.exterior_polygon = Polygon(self.map['exterior_poly'])
        self.interior_polygon = Polygon(self.map['interior_poly'])
        self.checkpoints = [LineString(x) for x in self.map['checkpoints']]
    
    def update(self):
        self.timer += 1
        self.update_collisions()
        self.update_car()

    def update_collisions(self):
        # Collisions between car lines and walls
        for car in self.cars:
            car.vision_intersections = [[] for i in range(Car.VISION_LINES)]


    def update_car(self):

        for car in self.cars:
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

    # number if vision lines in a 180 view in front of the car
    VISION_LINES = 6
    VISION_DISTANCE = 60

    def __init__(self, pos, size):

        self.pos = Vector(*pos)
        self.direction = pi * 3/2
        self.speed = 0
        self.acceleration = Car.ACCELERATION
        self.steer_angle = 0
        self.size = size
        self.wheel_base = size/2

        # Sensory Attributes
        self.vision_intersections = [[] for i in range(Car.VISION_LINES)]

        # Training attributes
        self.fitness = 0

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
    
    def calculate_vision(self):

        center = self.pos
        direction = self.direction

        total_lines = Car.VISION_LINES
        lines = []

        for i in range(total_lines):
            p1 = [center.x, center.y]
            angle = (direction+pi/2) - pi * (i)/(total_lines-1)
            p2 = [center.x + cos(angle)*Car.VISION_DISTANCE, center.y + sin(angle)*Car.VISION_DISTANCE]
            lines.append([p1, p2])
        
        return lines

    def draw(self, screen):
        
        # Draw lines
        for i, p in enumerate(self.calculate_vision()):
            p1, p2 = p
            if self.vision_intersections[i] == []:
                x1, y1 = int(p1[0]), int(p1[1])
                x2, y2 = int(p2[0]), int(p2[1])
                pygame.gfxdraw.line(screen, x1, y1, x2, y2, COLORS['white'])
            else:
                print(self.vision_intersections[i])
                x1, y1 = int(p1[0]), int(p1[1])
                x2, y2 = self.vision_intersections[i][0]
                pygame.gfxdraw.line(screen, x1, y1, int(x2), int(y2), COLORS['red'])

        pygame.gfxdraw.polygon(screen, self.calculate_polygon(), Color("#0000FF"))