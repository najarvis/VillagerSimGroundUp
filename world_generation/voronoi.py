import math
from random import randint
from math import inf
import functools
import pygame

@functools.total_ordering
class point(object):

    def __init__(self, pos, color=False):
        """Basic point, this will be used for the "feature points"
        these will hold their position, as well as a separate x and y
        variable for easy use. Also a distance variable will be assigned
        for when calculating the voronoi diagram"""

        self.pos = pos
        self.x = pos[0]
        self.y = pos[1]
        self.distance = 0
        self.color = None
        if color: self.color = randint(0, 255)
        self.brightness = 0
        self.current_point = None

    def get_distance(self, p2):
        """Basic distance formula. Doesn't square root everything
        in order to speed up the process (AKA Manhattan Distance) """
        try:
            distance = float((p2.x - self.x) ** 2) + ((p2.y - self.y) ** 2)
        except ZeroDivisionError:
            distance = 0
        except AttributeError:
            distance = 0
        self.distance = distance
        return distance

    def add_color(self):
        if randint(0, 1):
            self.color = randint(1, 10) * 10
        else:
            self.color = 0

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __lt__(self, other):
        # Look into changing this to just .distance to avoid duplicate distance calculations
        return self.get_distance(self.current_point) < other.get_distance(self.current_point)

def voronoi_map(size=(256, 256), rpd=4, ppr=3, control_coefficients=[]):
        """Creates and returns an array of given size containing values calculated by a voronoi diagram.
        The updated version is more controlled, with regions per dimension (rpd) and points per region (ppr). The array
        is split up into rpd * rpd  regions, while each region contains ppr interest points. These points are used along
        with coefficients c1, c2, and c3 to customize the array.

        DEPRECATED IN FAVOR OF WORLEY NOISE

        Arguments:
            size:
                The size of the return array. This should probably just be an
                integer to keep the array square in the future.
            rpd:
                This is the amount of regions on each side of the diagram.
                A value of 4 would result in 16 regions, 4 on each side.
            ppr:
                The amount of interest points in a region. Randomly distributed
            control_coefficients:
                Coeffiecients that determine how the final outcome will be.
                A c1 of 1 and the rest 0's will result in 'bubbles', while
                a c1 of 1 and a c2 of -1 will result in straight lines that
                divide the diagram into regions
        Returns a 2-Dimensional array with size equal to the argument size."""

        w, h = size
        values = [[0 for i in range(w)] for j in range(h)]
        num_regions = rpd * rpd
        region_size = size[0] / rpd
        num_points = num_regions * ppr

        interest_points = []

        for region_y in range(rpd):
            for region_x in range(rpd):

                for p in range(ppr):
                    rx = randint(region_x * region_size, (region_x + 1) * region_size)
                    ry = randint(region_y * region_size, (region_y + 1) * region_size)
                    interest_points.append(point((rx, ry)))

        max_val = 0
        min_val = inf

        for y in range(h):
            for x in range(w):
                current_point = point((x, y))
                vor_value = 0
                for p in interest_points:
                    p.current_point = current_point

                #sort the points in a new list by their distance from the current point
                interest_points.sort()

                for interest_point, coefficient in zip(interest_points, control_coefficients):
                    vor_value += interest_point.distance * coefficient

                max_val = max(vor_value, max_val)
                min_val = min(vor_value, min_val)

                values[x][y] = vor_value

        max_val -= min_val
        # print max_val, min_val
        for y in range(h):
            for x in range(w):
                values[x][y] = (values[x][y] - min_val) / max_val

        return values

def random2(pos: pygame.Vector2) -> pygame.Vector2:
    # https://thebookofshaders.com/12/
    intermediate = pygame.Vector2(pos.dot(pygame.Vector2(127.1,311.7)), pos.dot(pygame.Vector2(269.5,183.3)))
    intermediate2 = pygame.Vector2(abs(math.sin(intermediate.x)), abs(math.sin(intermediate.y))) * 43758.5453
    return vec2_components(intermediate2)[0]

def vec2_components(vec: pygame.Vector2) -> tuple[pygame.Vector2, pygame.Vector2]:
    """Return the integer and fractional components of a vector separately"""
    x_components = math.modf(vec.x)
    y_components = math.modf(vec.y)
    f_st = pygame.Vector2(x_components[0], y_components[0])
    i_st = pygame.Vector2(x_components[1], y_components[1])
    return (f_st, i_st)

def worley_texture(size=(256, 256), rows=16, cols=16):
    surf = pygame.Surface(size)
    surf.lock()
    for x in range(size[0]):
        for y in range(size[1]):
            normalized_coords = pygame.Vector2(x / size[0], y / size[1])
            dists = worley_noise(normalized_coords, rows, cols)

            v = dists[1] - dists[0]
            col = min(255, int(v * 255))
            surf.set_at((x, y), (col, col, col))

    surf.unlock()
    return surf

def worley_noise(position: pygame.Vector2, rows: int = 4, cols: int = 4) -> list:
    """Based on the implementation in https://thebookofshaders.com/12/, 
    retreives the distances to the points in the 9 surrounding cells. Not a
    perfect implementation because it is possible for a coordinate on the
    edge of a cell to be closer to a point two cells away.
    
    position should be a pygame.Vector2 with the x and y coordinates normalized
    between 0 and 1. Note the vector itself should not be normalized.
    
    TODO: This always returns the same value. Find a way to "randomize" where the points are
    """

    dists = []

    normalized_coords = position
    normalized_coords.x *= rows
    normalized_coords.y *= cols

    # fractional and integer vector components of the coordinate. The integer
    # coordinate tells us which cell we are in, and the fractional coordinate
    # tells us where we are in that cell. 
    f_st, i_st = vec2_components(normalized_coords)

    # Only look at the surrounding cells
    for cell_x in range(-1, 2):
        for cell_y in range(-1, 2):
            neighbor = pygame.Vector2(cell_x, cell_y)

            # random2 is used to represent the feature point in a given cell
            r_point = random2(i_st + neighbor)

            diff = neighbor + r_point - f_st
            dist = diff.magnitude_squared() # Magnitude squared for speed up
            dists.append(dist)
    
    # Sort in order of increasing distance
    dists.sort()
    return dists

def worley_noise_val(dists, coefficients):
    v = 0
    for Fn, Cn in zip(dists, coefficients):
        v += Fn * Cn
    return v