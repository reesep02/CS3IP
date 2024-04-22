import pygame
import random
import time
from memory_profiler import profile

# Maze dimensions and setup
width = 600
height = 600
cell_size = 20
maze_rows = 30
maze_columns = 30
start_position = (0, 0)
end_position = (maze_rows - 1, maze_columns - 1)  # red finshing cell goal position
total_agents = 3

# Definitions for colours used
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
purple = (128, 0, 128)
orange = (255, 165, 0)
agent_colours = [blue, purple, orange]

# Initialises the maze with all cells set as walls (1)
maze = [[1] * maze_columns for _ in range(maze_rows)]

def recursive_backtracking(current):
    maze[current[0]][current[1]] = 0 # marks the current cell as a path
    directions = [(0, 2), (0, -2), (2, 0), (-2, 0)] # set to 2 to provide adequate space for paths (0) between the placement of walls (1)
    random.shuffle(directions)
    for direction in directions:
        new_cell = (current[0] + direction[0], current[1] + direction[1])
        if 0 <= new_cell[0] < maze_rows and 0 <= new_cell[1] < maze_columns and maze[new_cell[0]][new_cell[1]] == 1:
            maze[current[0] + direction[0] // 2][current[1] + direction[1] // 2] = 0 # makes a path when leading to unvisited cells
            recursive_backtracking(new_cell) # recursively backtracks the new cell given

recursive_backtracking(start_position)

# Initialise agent states for position, routes travelled, and perception memory for cells visited
agents_positions = [list(start_position) for _ in range(total_agents)]
agents_memory = [set() for _ in range(total_agents)]
shared_dead_ends = set()
agents_movements = [[] for _ in range(total_agents)]
agents_visited_cells = [[] for _ in range(total_agents)]
agents_restarted = [False for _ in range(total_agents)]
complete = [False] * total_agents

@profile #measures the usage of the function below
def run_simulation():
    pygame.init()
    screen = pygame.display.set_mode((width, height)) #creates pygame window
    pygame.display.set_caption("Multi-Agent Maze Navigation")
    clock = pygame.time.Clock() # controls the pygame framerate

    start_time = time.time() # records the start time of the simulation

    running = True
    while running:
        for event in pygame.event.get(): #fetches all events from the event queue
            if event.type == pygame.QUIT:
                running = False

        for i, agent_position in enumerate(agents_positions): # for loop to iterate over each agent to determine their move
            if not complete[i]:
                possible_moves = [
                    (agent_position[0] - 1, agent_position[1]),
                    (agent_position[0] + 1, agent_position[1]),
                    (agent_position[0], agent_position[1] - 1),
                    (agent_position[0], agent_position[1] + 1)
                ]
                valid_moves = [move for move in possible_moves if is_valid_move(move) and move not in agents_memory[i] and move not in shared_dead_ends] #filter for ensuring the moves chosen are within the bounds of the maze, not walls, and not dead ends from memory

                if valid_moves:
                    new_pos = random.choice(valid_moves)
                    agents_memory[i].add(tuple(agent_position)) # adds the current position of the agent to memory
                    agents_movements[i].append(tuple(new_pos))
                    update_agent_position(i, new_pos) #updates the agent's position on the map
                    if tuple(new_pos) == end_position:
                        complete[i] = True
                else:
                    if agents_movements[i]:
                        last_move = agents_movements[i][-1] #represents the last cell the agent visited prior to restarting
                        shared_dead_ends.add(last_move) #coordinates of the cell are appended to the shared perception history
                    agents_positions[i] = list(start_position)
                    agents_memory[i].clear()
                    agents_movements[i].clear()
                    agents_restarted[i] = True

        screen.fill(white)
        draw_maze(screen)
        draw_agents(screen, agents_positions)
        pygame.display.flip()
        clock.tick(10) # 10fps frame rate

    pygame.quit()
    end_time = time.time() # records the end time of the simulation
    print(f"The simulation ran for {end_time - start_time} seconds") # prints the duration of the simulation in seconds

def is_valid_move(pos):
    return 0 <= pos[0] < maze_rows and 0 <= pos[1] < maze_columns and maze[pos[0]][pos[1]] == 0 # checks if the cell position lies in a row and column within the valid range of the maze and the cell is not a wall

def update_agent_position(index, new_pos): # function responsible for updating the position of the agent from index to the new_pos
    agents_positions[index] = list(new_pos) # updates the list at the index which corresponds to the agent with the new position new_pos
    agents_visited_cells[index].append(new_pos) #appends the new position to the agent's individual perception
    print(f"Agent {index + 1} moved to {new_pos}") # prints to the console the agent's positions in real time

def draw_maze(screen):
    for row in range(maze_rows):
        for col in range(maze_columns):
            color = black if maze[row][col] == 1 else white # sets the colour to black if the cell is a wall, else white for paths
            pygame.draw.rect(screen, color, (col * cell_size, row * cell_size, cell_size, cell_size)) #draws a rectangle for the position of the cell
            if color == white:
                pygame.draw.rect(screen, black, (col * cell_size, row * cell_size, cell_size, cell_size), 1) # allows to distinguish each cell by drawing a black border
    pygame.draw.rect(screen, green, (start_position[1] * cell_size, start_position[0] * cell_size, cell_size, cell_size))
    pygame.draw.rect(screen, red, (end_position[1] * cell_size, end_position[0] * cell_size, cell_size, cell_size))

def draw_agents(screen, agents_positions):
    for i, agent_pos in enumerate(agents_positions): #loops through the three agents using index i for the agents colour
        if not complete[i]:
            pygame.draw.rect(screen, agent_colours[i], (agent_pos[1] * cell_size, agent_pos[0] * cell_size, cell_size, cell_size)) #the agents still require drawing after a restart if they havent completed the game by reaching the red cell

if __name__ == "__main__": #ensures the function is called when the program is run and not imported
    run_simulation()
