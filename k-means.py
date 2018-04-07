"""A simple program that implements the k-means clustering algorithm."""
import abc
import collections
import math
import pygame
import sys
import time

NUM_ITERATIONS = 3
SIZE = (1024, 1024)
COLOR_WHITE = (255, 255, 255)
COLORS = [
    (0, 0, 0),
    (0, 0, 255),
    (0, 255, 0),
    (255, 0, 0),
]
    
RADIUS = 5

class Point(collections.namedtuple('Point', ['x', 'y'])):

    def distance_to(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx ** 2 + dy ** 2)


class IterationPresenterStrategy(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def present(self, iteration_num, clusters, centeroids):
        pass


class PrintingIterationPresenterStrategy(IterationPresenterStrategy):

    def present(self, iteration_num, clusters, centeroids):
        print('{0}:\n  clusters={1}\n  centeroids={2}\n'.format(
            iteration_num, clusters, centeroids))
        

class DrawingIterationPresenterStrategy(IterationPresenterStrategy):

    def __init__(self, screen):
        self._screen = screen
    
    def present(self, iteration_num, clusters, centeroids):
        screen.fill(COLOR_WHITE)
        for i, cluster in enumerate(clusters):
            for point in cluster:
                pygame.draw.circle(self._screen, COLORS[i % len(COLORS)], point, RADIUS)
        for i, centeroid in enumerate(centeroids):
            centeroid = Point(x=int(centeroid.x), y=int(centeroid.y))
            pygame.draw.circle(
                self._screen, COLORS[i % len(COLORS)], centeroid, RADIUS * 2, 1)
        pygame.display.update()
        time.sleep(0.05)


class ChainingIterationPresenterStrategy(IterationPresenterStrategy):

    def __init__(self, strategies):
        self._strategies = strategies

    def present(self, iteration_num, clusters, centeroids):
        for strategy in self._strategies:
            strategy.present(iteration_num, clusters, centeroids)
                
    
class KMeans(object):

    def __init__(self, num_clusters, iteration_presenter_strategy):
        self._num_clusters = num_clusters
        self._iteration_presenter_strategy = iteration_presenter_strategy
        self._centeroids = []
        self._clusters = []

    def add_point(self, point):
        if len(self._clusters) < self._num_clusters:
            self._centeroids.append(point)
            self._clusters.append([point])
            self._iteration_presenter_strategy.present(0, self._clusters, self._centeroids)
        else:
            self._clusters[self._find_closest_centeroid_idx(point)].append(point)
            self._iteration_presenter_strategy.present(0, self._clusters, self._centeroids)
            for i in range(NUM_ITERATIONS):
                self._clusters = self._cluster_points_one_iteration()
                self._iteration_presenter_strategy.present(i + 1, self._clusters, self._centeroids)
                self._centeroids = self._calculate_new_centeroids(self._clusters)

    def _cluster_points_one_iteration(self):
        new_clusters = []
        for i in range(self._num_clusters):
            new_clusters.append([])

        for cluster in self._clusters:
            for point in cluster:
                new_clusters[self._find_closest_centeroid_idx(point)].append(point)

        return new_clusters

    def _find_closest_centeroid_idx(self, point):
        closest_centeroid_distance = None
        closest_centeroid_idx = None
        assert self._centeroids
        for i, centeroid in enumerate(self._centeroids):
            distance = point.distance_to(centeroid)
            if (closest_centeroid_distance is None or
                distance < closest_centeroid_distance):
                closest_centeroid_distance = distance
                closest_centeroid_idx = i
        return closest_centeroid_idx

    def _calculate_new_centeroids(self, clusters):
        centeroids = []
        for cluster in clusters:
            xs, ys = zip(*cluster)
            mean_x = sum(xs) / len(xs)
            mean_y = sum(ys) / len(ys)
            centeroids.append(Point(x=mean_x, y=mean_y))
        return centeroids


def run_loop(screen, num_clusters):
    k_means_calculator = KMeans(
        num_clusters,
        ChainingIterationPresenterStrategy([
            PrintingIterationPresenterStrategy(),
            DrawingIterationPresenterStrategy(screen),
    ]))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                k_means_calculator.add_point(Point(x=pos[0], y=pos[1]))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('USAGE: {0} NUM_CLUSTERS\n'.format(sys.argv[0]))
        sys.exit(1)

    num_clusters = int(sys.argv[1])
        
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    screen.fill(COLOR_WHITE)
    pygame.display.update()
    run_loop(screen, num_clusters)
