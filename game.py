import json
from math import atan2, cos, hypot, pi, radians, sin

import numpy as np
import pygame.gfxdraw
from pygame import Color
from pygame.math import Vector2 as Vector
from shapely.coords import CoordinateSequence
from shapely.geometry import LineString, MultiLineString, Point, Polygon

from settings import *


def line_intersect(a : MultiLineString, b : tuple):
    b = LineString(b)
    intersection = a.intersection(b)
    if type(intersection) == Point:
        return intersection.x, intersection.y
    return False

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
            lines.append( (point, points[i+1]) )
        else:
            lines.append( (point, points[0]) )
    
    return lines

class Game:

    TURN_RIGHT = "turn_right"
    TURN_LEFT = "turn_left"
    ACCELERATE = "accelerate"
    BRAKE = "brake"
    IDLE = "idle"

    MOVES = [TURN_RIGHT, TURN_LEFT, ACCELERATE, BRAKE, IDLE]

    def __init__(self, cars, map_file):
        self.timer = 0
        self.cars = cars

        with open("Tracks/"+map_file, 'r') as f:
            self.map = json.load(f)
        
        self.exterior_polygon = Polygon(self.map['exterior_poly'])
        self.interior_polygon = Polygon(self.map['interior_poly'])
        self.exterior_lines = points_to_mesh(self.map['exterior_poly'])
        self.interior_lines = points_to_mesh(self.map['interior_poly'])
        self.exterior_multiline = MultiLineString(self.exterior_lines)
        self.interior_multiline = MultiLineString(self.interior_lines)

        self.checkpoints = [LineString(x) for x in self.map['checkpoints']]

        spawn_point = (self.map['checkpoints'][0][0][0]+self.map['checkpoints'][0][1][0])/2, (self.map['checkpoints'][0][0][1]+self.map['checkpoints'][0][1][1])/2
        checkpoint1 = (self.map['checkpoints'][1][0][0]+self.map['checkpoints'][1][1][0])/2, (self.map['checkpoints'][1][0][1]+self.map['checkpoints'][1][1][1])/2
        new_angle = atan2(spawn_point[0]-checkpoint1[0], spawn_point[1]-checkpoint1[1])
        for car in self.cars:
            car.pos.x = spawn_point[0]
            car.pos.y = spawn_point[1]
            if self.map["direction"]:
                car.direction = self.map["direction"] + pi/2
            else:
                car.direction = new_angle
            car.checkpoints = [False for i in range(len(self.checkpoints))]
    
    def update(self):
        self.timer += 1
        self.update_collisions()
        self.update_car()
    
    def controller(self, i, action):
        if action == Game.TURN_RIGHT:
            self.cars[i].direction += pi/Car.TURN_SPEED
        elif action == Game.TURN_LEFT:
            self.cars[i].direction -= pi/Car.TURN_SPEED
        elif action == Game.ACCELERATE:
            self.cars[i].speed += Car.ACCELERATION
        elif action == Game.BRAKE:
            self.cars[i].speed -= Car.ACCELERATION
        else:
            pass

    def update_collisions(self):
        # Collisions between car lines and walls
        for car in self.cars:
            if not car.alive:
                continue

            p_pos = Point(car.pos.x, car.pos.y)
            if (self.interior_polygon.intersects( p_pos )) or \
                (not self.exterior_polygon.intersects( p_pos )):
                
                car.alive = False
                car.time_alive = self.timer
                continue

            car.vision_intersections = [[] for i in range(Car.VISION_LINES)]

            # Vision line collisions
            for i, v_line in enumerate(car.calculate_vision()):

                interior_intersection = line_intersect(self.interior_multiline, v_line)
                exterior_intersection = line_intersect(self.exterior_multiline, v_line)
                if interior_intersection:
                    car.vision_intersections[i].append(interior_intersection)

                if exterior_intersection:
                    car.vision_intersections[i].append(exterior_intersection)


            # Checkpoint collisions
            acceptable_distance = 10
            if car.checkpoints[-1]:
                car.time_alive = self.timer//10
                car.alive = False
                continue
            if p_pos.distance(self.checkpoints[car.objective]) < acceptable_distance:
                car.checkpoints[car.objective] = True
                car.objective += 1

    def update_car(self):

        for car in self.cars:

            if not car.alive:
                continue
            #Vector2 frontWheel = carLocation + wheelBase/2 * new Vector2( cos(carHeading) , sin(carHeading) );
            #Vector2 backWheel = carLocation - wheelBase/2 * new Vector2( cos(carHeading) , sin(carHeading) 
            
            if car.speed > car.MAX_SPEED:
                car.speed = car.MAX_SPEED
            if car.speed < 0:
                car.speed = 0

            if car.speed == 0:
                car.static_time += 1
            
            if car.static_time > 2*60:
                car.alive = False
                continue

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

    MAX_SPEED = 4
    ACCELERATION = 0.05
    TURN_SPEED = 60

    # number if vision lines in a 180 view in front of the car
    VISION_LINES = 5
    VISION_DISTANCE = 75

    def __init__(self, pos, size):

        self.pos = Vector(*pos)
        self.direction = pi * 3/2
        self.speed = Car.MAX_SPEED
        self.acceleration = Car.ACCELERATION
        self.steer_angle = 0
        self.size = size
        self.wheel_base = size/2
        self.color = Color("#0000FF")

        # Sensory Attributes
        self.vision_intersections = [[] for i in range(Car.VISION_LINES)]

        # Training attributes
        self.fitness = 0
        self.alive = True
        self.checkpoints = []
        self.objective = 1
        self.time_alive = 0
        self.static_time = 0

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
                x1, y1 = int(p1[0]), int(p1[1])
                x2, y2 = self.vision_intersections[i][0]
                pygame.gfxdraw.line(screen, x1, y1, int(x2), int(y2), COLORS['red'])
        

        pygame.draw.polygon(screen, self.color, self.calculate_polygon())
