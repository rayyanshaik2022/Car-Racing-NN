import pygame
import pygame.gfxdraw
from pygame import Color
from shapely.geometry import Polygon, LineString, Point
from math import *
import json

COLORS = {
    "grass" : Color("#3aba4d"),
    "red" : Color("#ff6347"),
    "blue" : Color("#47ceff"),
    "green" : Color("#45ff64"),
    "red" : Color("#ff4545")

}

WIDTH = 800
HEIGHT = 800
TITLE = "Race Track Builder"
FPS = 60

# Modes
INTERIOR_POLY = "Interior Polygon"
EXTERIOR_POLY = "Exterior Polygon"
CHECKPOINT = "Checkpoints"
SPAWN_DIRECTION = "Spawn Direction"
MODES = [INTERIOR_POLY, EXTERIOR_POLY, CHECKPOINT, SPAWN_DIRECTION]

class Gui:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.mode = INTERIOR_POLY

        self.angle_center_pos = 0.0

    def new(self):
        
        self.interior_poly_points = []
        self.exterior_poly_points = []
        self.checkpoint_lines = []

        self.interior_polygon = None
        self.exterior_polygon = None

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
        pygame.display.set_caption(
            f"{TITLE} || Mode: {self.mode}"
        )

    def draw(self):
        self.screen.fill(COLORS['grass'])

        # Draw interior polygon
        point_rad = 30
        for x, y in self.interior_poly_points:
            pygame.gfxdraw.aacircle(self.screen, x, y, point_rad, COLORS["red"])
        if (len(self.interior_poly_points) >= 3):
            pygame.gfxdraw.aapolygon(self.screen, self.interior_poly_points, COLORS["red"])
        
        # Draw interior polygon
        point_rad = 30
        for x, y in self.exterior_poly_points:
            pygame.gfxdraw.aacircle(self.screen, x, y, point_rad, COLORS["blue"])
        if (len(self.exterior_poly_points) >= 3):
            pygame.gfxdraw.aapolygon(self.screen, self.exterior_poly_points, COLORS["blue"])
        
        # Draw checkpoint lines
        for i, p in enumerate(self.checkpoint_lines):
            x1, y1 = p[0]
            x2, y2 = p[1]
            color = Color("#000000")
            if i == 0:
                color = COLORS["green"]
            elif i == len(self.checkpoint_lines) -1:
                color = COLORS["red"]
            pygame.gfxdraw.line(self.screen, int(x1), int(y1), int(x2), int(y2), color)
        
        pygame.display.flip()

    def events(self):
        # catch all events here
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.mode = INTERIOR_POLY
                if event.key == pygame.K_2:
                    self.mode = EXTERIOR_POLY
                if event.key == pygame.K_3:
                    self.mode = CHECKPOINT
                if event.key == pygame.K_4:
                    self.mode = SPAWN_DIRECTION
                if event.key == pygame.K_RETURN:
                    print("> Storing data ...")
                    output = {
                        "interior_poly" : self.interior_poly_points,
                        "exterior_poly" : self.exterior_poly_points,
                        "checkpoints" : self.checkpoint_lines
                    }

                    if type(self.angle_center_pos) == float:
                        output["direction"] = self.angle_center_pos
                    else:
                        output["direction"] = False

                    with open('map_data.json', 'w') as f:
                        json.dump(output, f, indent=4)
                        print("> Successfully stored data")


            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.mode == INTERIOR_POLY:
                    self.interior_poly_points.append([mx, my])
                    if len(self.interior_poly_points) >= 3:
                        self.interior_polygon = Polygon(self.interior_poly_points)
                if self.mode == EXTERIOR_POLY:
                    self.exterior_poly_points.append([mx, my])
                    if len(self.exterior_poly_points) >= 3:
                        self.exterior_polygon = Polygon(self.exterior_poly_points)
                if self.mode == CHECKPOINT:
                    
                    # Check if location is within proper bounds
                    pos = [mx, my]
                    p_pos = Point(pos)
                    if not (self.exterior_polygon and self.interior_polygon):
                        return
                    if not (self.exterior_polygon.contains(p_pos) and not self.interior_polygon.contains(p_pos)):
                        return

                    default_half_length = 800
                    half_length = default_half_length
                    degrees = 360; skip = 2

                    exterior_intersections = []
                    interior_intersections = []

                    for i in range(0, degrees, skip):
       
                        
                        p1 = [pos[0] + cos(radians(i))*half_length, pos[1] + sin(radians(i))*half_length]
                        p_p1 = Point(p1)
                        l1 = LineString([p1, pos])

                        try:
                            interior_i = self.interior_polygon.intersection(l1).coords
                            interior_i = [ x for x in interior_i]
                            interior_i.sort(key=lambda x: hypot(pos[0]-x[0], pos[1]-x[1]))
                            exterior_i = self.exterior_polygon.exterior.intersection(l1).coords
                        except:
                            continue

                        if len(interior_i) > 0:
                            dist = hypot(pos[0]-interior_i[0][0], pos[1]-interior_i[0][1])
                            interior_intersections.append([dist, interior_i[0]])
                        else: #intersects b
                            dist = hypot(pos[0]-exterior_i[0][0], pos[1]-exterior_i[0][1])
                            exterior_intersections.append([dist, exterior_i[0]])

                        
                    interior_intersections.sort(key=lambda x: x[0])
                    exterior_intersections.sort(key=lambda x: x[0])
                    

                    final_checkpoint_line = [interior_intersections[0][1], exterior_intersections[0][1]]
                    self.checkpoint_lines.append(final_checkpoint_line)

                if self.mode == SPAWN_DIRECTION:

                    if type(self.angle_center_pos) == float:
                        self.angle_center_pos = [mx, my]
                    else:
                        self.angle_center_pos = atan2(self.angle_center_pos[0]-mx, self.angle_center_pos[1]-my)
                        print("Angle set to: ", self.angle_center_pos * (180/pi))
# create the game object
g = Gui()
g.new()
g.run()