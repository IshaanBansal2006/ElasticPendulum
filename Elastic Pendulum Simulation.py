#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pygame
import sys
from pygame.locals import *
import math
from math import sin, cos, tan, pi
import numpy as np
from numpy.linalg import inv

def spring(start, end, nodes, width, lead1, lead2):
    """!
    Return a list of points corresponding to a spring.

    @param r1 (array-like) The (x, y) coordinates of the first endpoint.
    @param r2 (array-like) The (x, y) coordinates of the second endpoint.
    @param nodes (int) The number of spring "nodes" or coils.
    @param width (int or float) The diameter of the spring.
    @param lead1 (int) The starting flat piece of the spring.
    @param lead2 (int) The ending flat piece of the spring.
    @return An array of x coordinates and an array of y coordinates, and the start and end points
    """

    # Check that nodes is at least 1.
    nodes = max(int(nodes), 1)

    # Convert to numpy array to account for inputs of different types/shapes.
    start, end = np.array(start).reshape((2,)), np.array(end).reshape((2,))

    # If both points are coincident, return the x and y coords of one of them.
    if (start == end).all():
        return start[0], start[1]

    # Calculate length of spring (distance between endpoints).
    length = np.linalg.norm(np.subtract(end, start))

    # Calculate unit vectors tangent (u_t) and normal (u_t) to spring.
    u_t = np.subtract(end, start) / length
    u_n = np.array([[0, -1], [1, 0]]).dot(u_t)

    # Add some magic here
    p1 = start + lead1*u_t
    p2 = end - lead2*u_t

    length -= (lead1+lead2)

    # Initialize array of x (row 0) and y (row 1) coords of the nodes+2 points.
    spring_coords = np.zeros((2, nodes + 2))
    spring_coords[:,0], spring_coords[:,-1] = p1, p2

    # Check that length is not greater than the total length the spring
    # can extend (otherwise, math domain error will result), and compute the
    # normal distance from the centerline of the spring.
    normal_dist = math.sqrt(max(0, width**2 - (length**2 / nodes**2))) / 2

    # Compute the coordinates of each point (each node).
    for i in range(1, nodes + 1):
        spring_coords[:,i] = (
            p1
            + ((length * (2 * i - 1) * u_t) / (2 * nodes))
            + (normal_dist * (-1)**i * u_n))

    return spring_coords[0,:], spring_coords[1,:], p1, p2

class Spring():
	def __init__(self, color, start, end, nodes, width, lead1, lead2):
		self.start = start
		self.end = end
		self.nodes = nodes
		self.width = width
		self.lead1 = lead1
		self.lead2 = lead2
		self.weight = 3
		self.color = color

	def update(self, start, end):
		self.start = start
		self.end = end

		self.x, self.y, self.p1, self.p2 = spring(self.start, self.end, self.nodes, self.width, self.lead1, self.lead2)
		self.p1 = (int(self.p1[0]), int(self.p1[1]))
		self.p2 = (int(self.p2[0]), int(self.p2[1]))

	def render(self):
		pygame.draw.line(screen, self.color, self.start, self.p1, self.weight)
		prev_point = self.p1
		for point in zip(self.x, self.y):
			pygame.draw.line(screen, self.color, prev_point, point, self.weight)
			prev_point = point
		pygame.draw.line(screen, self.color, self.p2, self.end, self.weight)
	


def G(y,t): 
	x_d, θ_d, x, θ = y[0], y[1], y[2], y[3]

	x_dd = (l0+x) * θ_d**2 - k/m*x + g*cos(θ)
	θ_dd = -2.0/(l0+x) * x_d * θ_d - g/(l0+x) * sin(θ)	

	return np.array([x_dd, θ_dd, x_d, θ_d])

def RK4_step(y, t, dt):
	k1 = G(y,t)
	k2 = G(y+0.5*k1*dt, t+0.5*dt)
	k3 = G(y+0.5*k2*dt, t+0.5*dt)
	k4 = G(y+k3*dt, t+dt)

	return dt * (k1 + 2*k2 + 2*k3 + k4) / 6

def update(x, θ):
	x_coord = scale*(l0+x) * sin(θ) + offset[0]
	y_coord = scale*(l0+x) * cos(θ) + offset[1]

	return (int(x_coord), int(y_coord))

def render(point):
	x, y = point[0], point[1]

	if prev_point:
		pygame.draw.line(trace, LT_BLUE, prev_point, (x, y), 5)

	screen.fill(WHITE)	
	if is_tracing:
		screen.blit(trace, (0,0))

	#pygame.draw.line(screen, BLACK, offset, (x,y), 5)
	s.update(offset, point)
	s.render()
	pygame.draw.circle(screen, BLACK, offset, 8)
	pygame.draw.circle(screen, BLUE, (x, y), int(m*10))

	return (x, y)

w, h = 1024, 768
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
BLUE = (0,0,255)
LT_BLUE = (230,230,255)
offset = (w//2, h//4)
scale = 100
is_tracing = True

screen = pygame.display.set_mode((w,h))
screen.fill(WHITE)
trace = screen.copy()
pygame.display.update()
clock = pygame.time.Clock()

# parameters
m = 6.0
l0 = 3.5
g = 9.81
k = 100.0

prev_point = None
t = 0.0
delta_t = 0.02
y = np.array([0.0, 0.0, 0.0, 2.0])

pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 38)

s = Spring(BLACK, (0,0), (0,0), 25, 30, 90, 90)

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		if event.type == KEYDOWN:
			if event.key == K_t:
				is_tracing = not(is_tracing)
			if event.key == K_c:
				trace.fill(WHITE)

	point = update(y[2], y[3])
	prev_point = render(point)

	time_string = 'Time: {} seconds'.format(round(t,1))
	text = myfont.render(time_string, False, (0, 0, 0))
	screen.blit(text, (10,10))

	t += delta_t
	y = y + RK4_step(y, t, delta_t) 

	clock.tick(60)
	pygame.display.update()


# In[ ]:




