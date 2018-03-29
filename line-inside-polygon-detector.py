"""A program that figures out whether the mouse is inside or outside
of a user-drawn polygon.
"""

import collections
import math
import pygame

SIZE = (1024, 1024)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
SNAPPING_THRESHOLD = 100

Point = collections.namedtuple('Point', ['x', 'y'])
Range = collections.namedtuple('Range', ['min', 'max'])


class LineSegment(object):

    def __init__(self, p1, p2):
        self._range = Range(min=min(p1.x, p2.x), max=max(p1.x, p2.x))
        self._slope = (p1.y - p2.y) / (p1.x - p2.x)
        self._y_intercept = p1.y - self._slope * p1.x

    def x_intercept(self, y):
        x_intercept = (y - self._y_intercept) / self._slope
        if self._range.min <= x_intercept <= self._range.max:
            return x_intercept
        else:
            return None

    def __repr__(self):
        return '{0}(y = {1}x + {2})'.format(
            self.__class__.__name__, self._slope, self._y_intercept)


def convert_to_line_segments(points):
    line_segments = []
    for i in range(len(points) - 1):
        line_segments.append(
            LineSegment(points[i], points[i + 1]))
    return line_segments


def get_x_range(points):
    min_x = points[0].x
    max_x = points[0].x
    for point in points[1:]:
        min_x = min(min_x, point.x)
        max_x = max(max_x, point.x)
    return (min_x, max_x)

    
def is_point_inside_polygon(line_segments, point):
    y = point.y
    x_intercepts = []
    for line_segment in line_segments:
        x_intercept = line_segment.x_intercept(y)
        if x_intercept is not None:
            x_intercepts.append(x_intercept)

    # TODO(aryann): This is a bit inefficient. We can prune the
    # line_segment list by getting rid of all points whose min_x is >
    # point.x.
    return len([x_intercept for x_intercept in x_intercepts
                if x_intercept <= point.x]) % 2 == 1


class State(object):
    START, MIDDLE, END = range(3)


def get_distance(p1, p2):
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    return math.sqrt(dx * dx + dy * dy)
    

def draw_lines(points):
    pygame.draw.lines(screen, COLOR_BLACK, False, points)

    
def run_loop(screen):
    points = []
    line_segments = None
    state = State.START
    
    while True:
        for event in pygame.event.get():
            if event.type not in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
                continue

            pos = pygame.mouse.get_pos()
            pos = Point(x=pos[0], y=pos[1])
            screen.fill(COLOR_WHITE)

            # TODO(aryann): Check for illegal polygons, and prevent
            # the last line segment from being drawn if that line
            # segment causes the shape to not be a polygon. Simple
            # algorithm for this is to ensure that no two line
            # segments intersect one another.
            if state == State.START:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    points = [pos]
                    state = State.MIDDLE
                
            elif state == State.MIDDLE:
                within_snapping_threshold = False
                if len(points) > 1:
                    start = points[0]
                    distance_to_start = get_distance(start, pos)
                    if distance_to_start < SNAPPING_THRESHOLD:
                        pos = start
                        within_snapping_threshold = True
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    points.append(pos)
                    if within_snapping_threshold:
                        line_segments = convert_to_line_segments(points)
                        state = State.END
                        pygame.draw.polygon(screen, COLOR_BLACK, points)
                    else:
                        draw_lines(points)

                elif event.type == pygame.MOUSEMOTION:
                    if len(points) > 1:
                        draw_lines(points)
                    if points:
                        pygame.draw.line(screen, COLOR_BLACK, points[-1], pos)
                        
            elif state == State.END:
                assert line_segments
                if event.type == pygame.MOUSEMOTION:
                    if is_point_inside_polygon(line_segments, pos):
                        color = COLOR_RED
                    else:
                        color = COLOR_BLACK
                    pygame.draw.polygon(screen, color, points)
                    
            else:
                raise ValueError('Unknown state: ' + str(state))
            

            pygame.display.update()
            

    
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    screen.fill(COLOR_WHITE)
    pygame.display.update()
    run_loop(screen)
