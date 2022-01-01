import pygame
import os
import random
import sys
import neat
import math
import time
import pickle

pygame.init()

# Defining global variables first
game_speed, x_pos_bg, y_pos_bg, points, obstacles, dinosaurs, ge, nets, pop, gens, high= 0,0,0,0, [], [], [], [] , 0 ,0,0

# Creating screen height and width to display the game
HEIGHT = 540
WIDTH = 960
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Jump!")

# Loading the images
DINO = pygame.transform.scale(pygame.image.load(os.path.join("assets", "Dino.png")), (180,225)) 

BG = pygame.image.load(os.path.join("assets", "track.png")) 

CACTUS = [pygame.transform.scale(pygame.image.load(os.path.join("assets", "cact1.png")),(100,140)),
pygame.transform.scale(pygame.image.load(os.path.join("assets", "cact2.png")),(100,100)),
pygame.transform.scale(pygame.image.load(os.path.join("assets", "cact3.png")),(100,80)),
pygame.transform.scale(pygame.image.load(os.path.join("assets", "cact4.png")),(100,100)),
pygame.transform.scale(pygame.image.load(os.path.join("assets", "cact5.png")),(100,118)),
pygame.transform.scale(pygame.image.load(os.path.join("assets", "cact6.png")),(100,104))]

# Loading the font
FONT = pygame.font.Font('freesansbold.ttf', 20)

class Dinosaur:
    # Constants for where it goes ont he screen
    X_POS = 50
    Y_POS = 200
    JUMP_VEL = 8.5

    def __init__(self, img = DINO):
        self.image = DINO
        self.mask = pygame.mask.from_surface(DINO)
        self.dino_jump = False
        self.jump_vel = self.JUMP_VEL
        self.y = self.Y_POS
        self.x = self.X_POS

    def update(self):
        if self.dino_jump:
            self.jump()

    def jump(self):
        if self.dino_jump:
            # Remember that subtraction means that it is going up
            self.y = self.y - (self.jump_vel*4)
            # Decreasing the jump velocity, we arrive at 0.85 by 8.5/10 = 0.85
            self.jump_vel = self.jump_vel - 0.85
        # If the dino is at the ground again
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL
            self.y = self.Y_POS

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.X_POS, self.y))

    def getX(self):
        return self.x
    
    def getY(self):
        return self.y

    def getOriginal(self):
        return self.Y_POS

class Obstacle:
    def __init__(self, image, cacti_num):
        self.image = image
        self.type = cacti_num
        self.mask = pygame.mask.from_surface(self.image[self.type])
        self.x = WIDTH+random.randint(0, 500)
        self.y = 300

    def update(self):
        # Moves the x position of the cactus to match the game speed
        self.x = self.x - game_speed
        if self.x < 0:
            # Deletes from obstacles array
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], (self.x, self.y))

    def getX(self):
        return self.x
    
    def getY(self):
        return self.y

def remove(index):
    dinosaurs.pop(index)
    ge.pop(index)
    nets.pop(index)

def replay_genome(config_path, genome_path = "winner.pkl"):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    # Unpickle the winner
    with open(genome_path, "rb") as f:
        genome = pickle.load(f)

    

def distance(pos_a, pos_b):
    dx = pos_a[0]- pos_b[0]
    dy = pos_a[1] - pos_b[1]

    return math.sqrt(dx**2+dy**2)

def eval_genomes(genomes, config):
    global gens, high

    # Incrementing generation count
    gens += 1
    time.sleep(1)

    # Global variables
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles, dinosaurs, ge, nets

    # Loading the clock
    clock = pygame.time.Clock()

    # Array that will hold all the dinosaur and cacti objects
    obstacles = []
    dinosaurs = []
    # Dictionary to store genomes
    ge = []

    # Dictionary to store neural network objects
    nets = []

    x_pos_bg = 0
    y_pos_bg = 210
    game_speed = 20
    points = 0

    # Loops through all dinos
    for genome_id, genome in genomes:

        # Creating new dino
        dinosaurs.append(Dinosaur())

        # Gives a genome
        ge.append(genome)

        # Makes neural network and adds to array
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)

        genome.fitness = 0

    def score():
        global points, game_speed
        points += 1

        # Every time points reach a multiple of 100
        if points % 100 == 0:
            game_speed += 3

        # Displays number of points
        text = FONT.render(f'Points:  {str(points)}', True, (0,0,0))
        SCREEN.blit(text, (750, 20))

    def stats():
        global dinosaurs, game_speed, ge
        text_1 = FONT.render(f'Dinosaurs Alive: {str(len(dinosaurs))}', True, (0,0,0))
        text_2 = FONT.render(f'Generation: {gens}', True, (0,0,0))
        text_3 = FONT.render(f'Game Speed: {str(game_speed)}', True, (0,0,0))
        text_4 = FONT.render(f'High Score: {str(high)}', True, (0,0,0))

        SCREEN.blit(text_1, (750,50))
        SCREEN.blit(text_2, (750,80))
        SCREEN.blit(text_3, (750,110))
        SCREEN.blit(text_4, (750,140))

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.fill((255, 255, 255))

        #Prints Score and moves background
        score()
        background()
        stats()

        for dinosaur in dinosaurs:
            dinosaur.update()
            dinosaur.draw(SCREEN)

        if len(dinosaurs) == 0:
            break

        # Randomly creates cacti
        if len(obstacles) == 0:
            rand_int = random.randint(0,5)
            obstacles.append(Obstacle(CACTUS, rand_int))
            
        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            for i, dinosaur in enumerate(dinosaurs):
                offset_x = int(obstacle.getX() - dinosaur.getX())
                offset_y = int(obstacle.getY() - dinosaur.getY())

                # Collision!
                if dinosaur.mask.overlap(obstacle.mask, (offset_x, offset_y)):
                    # Lowers fitness because they crashed
                    ge[i].fitness -= 2
                    remove(i)

        # Leave in here to test
        #user_input = pygame.key.get_pressed()

        for i, dinosaur in enumerate(dinosaurs):

            # Passing in the y position of dinosaur
            # and the distance to the next cacti
            output = nets[i].activate((dinosaur.getY(), distance((dinosaur.getX(), dinosaur.getY()), (obstacle.getX(), dinosaur.getY())), game_speed))

            # If the network decided jump and dino is not jumping
            if output[0] > 0.5 and (dinosaur.getY() == dinosaur.getOriginal()):
                dinosaur.dino_jump = True

            # Leave in here for testing
            #if user_input[pygame.K_SPACE]:
                #dinosaur.dino_jump = True
            
        # This means 30 frames per second
        clock.tick(30)

        if points > high:
            high = points
        pygame.display.update()

def run(config_path):
    # Configuring the neat algorithm (defaults)
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    # Creating the population
    pop = neat.Population(config)

    # Running up to 50 times
    winner = pop.run(eval_genomes, 1000)

    # Saving the model
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)
        f.close()

    print('saved model!')


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')

    # Toggle on and off depending on train or not
    run(config_path)