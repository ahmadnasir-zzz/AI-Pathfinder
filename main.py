import pygame
import time
from collections import deque
import heapq
import os

width = 600 
height = 600 
rows = 15 
box_size = width // rows 

title = "GOOD PERFORMANCE TIME APP" # naming the window title 

white, black = (255, 255, 255), (0, 0, 0)
green, red = (0, 255, 0), (255, 0, 0) 
blue, yellow = (0, 0, 255), (255, 255, 0) 
gray = (200, 200, 200) 

# following clockwise movement order
directions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]

class box:
    def __init__(self, r, c):
        self.r, self.c = r, c
        self.is_wall = False
        self.parent = None
        self.cost = float('inf')

def show_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("--- ai pathfinder menu ---")
    print(" 1: bfs \n 2: dfs \n 3: ucs \n 4: dls \n 5: iddfs \n 6: bidirectional")
    print("\n\n------------------------------------\n left click: start -> target -> walls \n key c: clear")

def draw_grid(win, grid, start, target, frontier, explored, path):
    win.fill(white) 
    for row in grid:
        for b in row:
            color = white
            if b.is_wall: color = black # painting walls black
            if explored and b in explored: color = gray # coloring visited nodes [
            if frontier and b in frontier: color = yellow # coloring frontier nodes 
            if path and b in path: color = blue # highlighting final path
            if b == start: color = green
            if b == target: color = red
            pygame.draw.rect(win, color, (b.c * box_size, b.r * box_size, box_size, box_size))
            pygame.draw.rect(win, (210, 210, 210), (b.c * box_size, b.r * box_size, box_size, box_size), 1)
    pygame.display.update() 

def reset(grid):
    for row in grid:
        for b in row:
            b.parent = None
            b.cost = float('inf')

def get_path(node):
    p = [] 
    while node:
        p.append(node)
        node = node.parent # moving back to parent
    return p



def run_bfs(win, grid, start, target):# search algorithms 
    q = deque([start]) 
    vis = {start}
    while q:
        curr = q.popleft() # popping from front
        if curr == target: return get_path(curr)
        for dr, dc in directions:
            r, c = curr.r + dr, curr.c + dc
            if 0 <= r < rows and 0 <= c < rows and not grid[r][c].is_wall:
                if grid[r][c] not in vis:
                    grid[r][c].parent = curr
                    vis.add(grid[r][c]); q.append(grid[r][c])
        draw_grid(win, grid, start, target, q, vis, None); time.sleep(0.01) # animating search
    return None

def run_dfs(win, grid, start, target):
    s = [start] 
    vis = {start}
    while s:
        curr = s.pop() # popping from end
        if curr == target: return get_path(curr)
        for dr, dc in directions:
            r, c = curr.r + dr, curr.c + dc
            if 0 <= r < rows and 0 <= c < rows and not grid[r][c].is_wall:
                if grid[r][c] not in vis:
                    grid[r][c].parent = curr
                    vis.add(grid[r][c]); s.append(grid[r][c])
        draw_grid(win, grid, start, target, s, vis, None); time.sleep(0.01)
    return None

def run_ucs(win, grid, start, target):
    pq = [(0, id(start), start)] 
    start.cost = 0; vis = {start}
    while pq:
        c, _, curr = heapq.heappop(pq) # popping lowest cost
        if curr == target: return get_path(curr)
        for dr, dc in directions:
            r, c = curr.r + dr, curr.c + dc
            if 0 <= r < rows and 0 <= c < rows and not grid[r][c].is_wall:
                if c + 1 < grid[r][c].cost:
                    grid[r][c].cost = c + 1; grid[r][c].parent = curr
                    vis.add(grid[r][c]); heapq.heappush(pq, (grid[r][c].cost, id(grid[r][c]), grid[r][c]))
        draw_grid(win, grid, start, target, [x[2] for x in pq], vis, None); time.sleep(0.01)
    return None

def run_dls(win, grid, start, target, limit, vis):
    if start == target: return get_path(start)
    if limit <= 0: return None # stopping at depth limit 
    vis.add(start)
    for dr, dc in directions:
        r, c = start.r + dr, start.c + dc
        if 0 <= r < rows and 0 <= c < rows and not grid[r][c].is_wall:
            if grid[r][c] not in vis:
                grid[r][c].parent = start
                res = run_dls(win, grid, grid[r][c], target, limit - 1, vis) # recursing deeper
                if res: return res
    return None

def run_iddfs(win, grid, start, target):
    for d in range(rows * rows): # looping through depths 
        reset(grid)
        res = run_dls(win, grid, start, target, d, set())
        if res: return res
    return None

def run_bidir(win, grid, start, target):
    q1, q2 = deque([start]), deque([target]) # starting from both ends
    v1, v2 = {start: None}, {target: None}
    while q1 and q2:
        c1 = q1.popleft() 
        for dr, dc in directions:
            r, c = c1.r + dr, c1.c + dc
            if 0 <= r < rows and 0 <= c < rows and not grid[r][c].is_wall:
                if grid[r][c] not in v1:
                    v1[grid[r][c]] = c1; q1.append(grid[r][c])
                    if grid[r][c] in v2: return build(grid[r][c], v1, v2)
        c2 = q2.popleft() 
        for dr, dc in directions:
            r, c = c2.r + dr, c2.c + dc
            if 0 <= r < rows and 0 <= c < rows and not grid[r][c].is_wall:
                if grid[r][c] not in v2:
                    v2[grid[r][c]] = c2; q2.append(grid[r][c])
                    if grid[r][c] in v1: return build(grid[r][c], v1, v2)
        draw_grid(win, grid, start, target, list(q1)+list(q2), set(v1.keys())|set(v2.keys()), None)
    return None

def build(node, v1, v2):
    p = [] # joining both paths
    c = node
    while c: p.append(c); c = v1[c]
    p.reverse()
    c = v2[node]
    while c: p.append(c); c = v2[c]
    return p

def main():
    pygame.init() 
    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption(title)
    grid = [[box(r, c) for c in range(rows)] for r in range(rows)]
    start = target = path = None
    show_menu() 
    run = True
    while run:
        draw_grid(win, grid, start, target, None, None, path)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False
            if pygame.mouse.get_pressed()[0]: # capturing mouse clicks 
                pos = pygame.mouse.get_pos()
                r, c = pos[1] // box_size, pos[0] // box_size
                if r < rows and c < rows:
                    if not start: start = grid[r][c]
                    elif not target and grid[r][c] != start: target = grid[r][c]
                    elif grid[r][c] not in [start, target]: grid[r][c].is_wall = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c: # resetting the grid
                    start = target = path = None
                    grid = [[box(r, c) for r in range(rows)] for r in range(rows)]
                    show_menu()
                if start and target:
                    reset(grid)
                    if event.key == pygame.K_1: path = run_bfs(win, grid, start, target)
                    if event.key == pygame.K_2: path = run_dfs(win, grid, start, target)
                    if event.key == pygame.K_3: path = run_ucs(win, grid, start, target)
                    if event.key == pygame.K_4: path = run_dls(win, grid, start, target, 20, set())
                    if event.key == pygame.K_5: path = run_iddfs(win, grid, start, target)
                    if event.key == pygame.K_6: path = run_bidir(win, grid, start, target)
    pygame.quit()

if __name__ == "__main__": main()
