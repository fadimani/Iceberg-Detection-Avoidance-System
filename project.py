import pygame
import cv2
from queue import PriorityQueue
import numpy as np



RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
OCEAN_BLUE = (43, 101, 236)
ICE = (64, 224, 208)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
BOAT_ORANGE = (255, 165 , 0)   #TURQUOISE = (64, 224, 208)

class NODE:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = OCEAN_BLUE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == ICE

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == BOAT_ORANGE

    def reset(self):
        self.color = OCEAN_BLUE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = ICE

    def make_end(self):
        self.color = BOAT_ORANGE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):     #drawing the nodes as they'll appear in the window
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width)) #the square coords and size in the screen

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


def h(p1, p2):#this is the fct that calculates the heuristic distance between the start and the end. aka H cost
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw,grid):
    while current in came_from:
        current = came_from[current]
        if current.color != ORANGE:
            current.make_path()

    for row in grid:
        for spot in row:
            if spot.color == RED or spot.color == GREEN:
                spot.reset()
    draw()

def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:

            reconstruct_path(came_from, end, draw,grid)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()
    return False

#this is for making the grid that we'll draw later
def make_grid(rows, width):
    grid = []
    gap = width // rows	  #integer division
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = NODE(i, j, gap, rows)
            grid[i].append(node)
        #print(grid[i][j].color)

    return grid

def segment_image(input):
    img = cv2.imread(input)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    hsv_img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    min_range = (100,5,68)
    max_range = (194,68,231)

    mask = cv2.inRange(hsv_img, min_range, max_range)

    result = cv2.bitwise_and(img, img, mask=mask)
    sub_result = cv2.resize(result, (50,50), interpolation = cv2.INTER_AREA)
    sub_result_grey = cv2.cvtColor(sub_result, cv2.COLOR_BGR2GRAY)
    th, sub_result_grey_otsu = cv2.threshold(sub_result_grey, 128, 192, cv2.THRESH_OTSU)
    return sub_result_grey_otsu



def fill_grid_from_map(grid,rows,input):
    img = segment_image(input)
    for i in range(rows):
        for j in range(rows):
            if (img[i,j]==192):
                grid[j][i].make_barrier()
    return grid


#here we're drawing the grid lines
def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    #filling the window with the default color
    win.fill(OCEAN_BLUE)

    #drawing the nodes
    for row in grid:
        for spot in row:
            spot.draw(win)

    #drawing the grid
    draw_grid(win, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col


def main(win, width,input):
    WIDTH = 800										#window size
    win = pygame.display.set_mode((WIDTH, WIDTH))    #this is where we set the window
    pygame.display.set_caption("Iceberg Detection and Avoidance System")
    ROWS = 50
    grid = make_grid(ROWS, width)
    grid = fill_grid_from_map(grid,ROWS,input)

    start = None   #the start node
    end = None		#the end node

    run = True
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():	#looping (listening) to pygame events
            if event.type == pygame.QUIT:	#event: pressing X on the pygame window
                run = False

            if pygame.mouse.get_pressed()[0]: # LEFT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()        #what pressing the left mouse does in this case

                elif not end and spot != start:
                    end = spot
                    end.make_end()				#what pressing the left mouse does in this case

                elif spot != end and spot != start:
                    spot.make_barrier()			#what pressing the left mouse does in this case

            elif pygame.mouse.get_pressed()[2]: # RIGHT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                ####################################################################################################
                if event.key == pygame.K_RIGHT and start and end:
                    start.reset()
                    spot = grid[start.row+1][start.col]
                    start = spot
                    start.make_start()
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_UP and start and end:
                    start.reset()
                    spot = grid[start.row][start.col-1]
                    start = spot
                    start.make_start()
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_LEFT and start and end:
                    start.reset()
                    spot = grid[start.row-1][start.col]
                    start = spot
                    start.make_start()
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_DOWN and start and end:
                    start.reset()
                    spot = grid[start.row][start.col+1]
                    start = spot
                    start.make_start()
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
                ####################################################################################################
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()
WIDTH = 800										#window size
