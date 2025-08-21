import pygame
import neat
import time
import os
import random
import math

pygame.font.init()

# Konstanta
WIN_WIDTH = 400
WIN_HEIGHT = 600
FLOOR = 530
STAT_FONT = pygame.font.SysFont("comicsans", 40)

# Warna Prosedural
SKY_BLUE_TOP = (135, 206, 250)
SKY_BLUE_BOTTOM = (176, 224, 230)
BIRD_YELLOW = (255, 223, 0)
BIRD_ORANGE = (255, 165, 0)
BIRD_WHITE = (255, 255, 255)
BIRD_BLACK = (0, 0, 0)
PIPE_GREEN = (46, 139, 87)
PIPE_GREEN_DARK = (34, 107, 67)
BASE_BROWN = (139, 69, 19)
BASE_GREEN = (60, 179, 113)

GEN = 0
MAX_FITNESS = 0
BEST_SCORE = 0

class Bird:
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.width = 34  # Perkiraan ukuran untuk surface
        self.height = 24 # Perkiraan ukuran untuk surface
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        displacement = self.vel * self.tick_count + 1.5 * self.tick_count**2
        if displacement >= 16:
            displacement = 16
        if displacement < 0:
            displacement -= 2
        self.y += displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        # Menggambar burung ke surface internal
        self.surface.fill((0,0,0,0)) # Latar transparan

        # Badan
        pygame.draw.circle(self.surface, BIRD_YELLOW, (self.width // 2, self.height // 2), 12)
        # Mata
        pygame.draw.circle(self.surface, BIRD_WHITE, (22, 10), 4)
        pygame.draw.circle(self.surface, BIRD_BLACK, (22, 10), 2)
        # Paruh
        pygame.draw.polygon(self.surface, BIRD_ORANGE, [(26, 12), (32, 14), (26, 16)])

        # Animasi Sayap
        flap_cycle = self.img_count % (self.ANIMATION_TIME * 2)
        if flap_cycle < self.ANIMATION_TIME: # Sayap ke atas
            wing_points = [(14, 12), (8, 6), (20, 6)]
        else: # Sayap ke bawah
            wing_points = [(14, 12), (8, 18), (20, 18)]
        pygame.draw.polygon(self.surface, BIRD_YELLOW, wing_points)
        pygame.draw.line(self.surface, BIRD_BLACK, (14,12), (8,6) if flap_cycle < self.ANIMATION_TIME else (8,18), 1)

        # Rotasi
        rotated_surface = pygame.transform.rotate(self.surface, self.tilt)
        new_rect = rotated_surface.get_rect(center=self.surface.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_surface, new_rect.topleft)

    def get_mask(self):
        # Mask harus dibuat ulang setiap frame karena rotasi
        temp_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
        self.draw(temp_surface) # Gambar burung ke surface sementara di posisinya
        return pygame.mask.from_surface(temp_surface)


class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.width = 60 # Lebar pipa
        self.cap_height = 25 # Tinggi cincin
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(80, 320)
        self.top = self.height
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        # Pipa Atas
        pygame.draw.rect(win, PIPE_GREEN, (self.x, 0, self.width, self.top))
        pygame.draw.rect(win, PIPE_GREEN_DARK, (self.x - 5, self.top - self.cap_height, self.width + 10, self.cap_height))
        # Pipa Bawah
        pygame.draw.rect(win, PIPE_GREEN, (self.x, self.bottom, self.width, WIN_HEIGHT - self.bottom))
        pygame.draw.rect(win, PIPE_GREEN_DARK, (self.x - 5, self.bottom, self.width + 10, self.cap_height))

    def collide(self, bird):
        # Deteksi tabrakan sederhana berbasis persegi panjang (cukup untuk ini)
        bird_rect = pygame.Rect(bird.x, bird.y, bird.width, bird.height)
        top_pipe_rect = pygame.Rect(self.x, 0, self.width, self.top)
        bottom_pipe_rect = pygame.Rect(self.x, self.bottom, self.width, WIN_HEIGHT - self.bottom)

        if bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect):
            return True
        return False


class Base:
    VEL = 5
    WIDTH = WIN_WIDTH

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        pygame.draw.rect(win, BASE_BROWN, (self.x1, self.y, self.WIDTH, WIN_HEIGHT - self.y))
        pygame.draw.rect(win, BASE_BROWN, (self.x2, self.y, self.WIDTH, WIN_HEIGHT - self.y))
        # Tekstur rumput
        for i in range(0, WIN_WIDTH, 20):
            pygame.draw.line(win, BASE_GREEN, (self.x1 + i, self.y), (self.x1 + i + 5, self.y + 10), 3)
            pygame.draw.line(win, BASE_GREEN, (self.x2 + i, self.y), (self.x2 + i + 5, self.y + 10), 3)


def draw_window(win, birds, pipes, base, score, gen, fitness, species_count):
    # Latar gradien
    for y in range(WIN_HEIGHT):
        color_r = SKY_BLUE_TOP[0] + (SKY_BLUE_BOTTOM[0] - SKY_BLUE_TOP[0]) * y / WIN_HEIGHT
        color_g = SKY_BLUE_TOP[1] + (SKY_BLUE_BOTTOM[1] - SKY_BLUE_TOP[1]) * y / WIN_HEIGHT
        color_b = SKY_BLUE_TOP[2] + (SKY_BLUE_BOTTOM[2] - SKY_BLUE_TOP[2]) * y / WIN_HEIGHT
        pygame.draw.line(win, (color_r, color_g, color_b), (0, y), (WIN_WIDTH, y))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        bird.draw(win)

    # Statistik (dengan latar belakang semi-transparan)
    stat_bg = pygame.Surface((WIN_WIDTH, 210), pygame.SRCALPHA)
    stat_bg.fill((0,0,0, 100))
    win.blit(stat_bg, (0,0))

    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (10, 10))
    gen_label = STAT_FONT.render("Gen: " + str(gen),1,(255,255,255))
    win.blit(gen_label, (10, 50))
    alive_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(alive_label, (10, 90))
    fitness_label = STAT_FONT.render(f"Max Fitness: {fitness:.1f}", 1, (255, 255, 255))
    win.blit(fitness_label, (10, 130))
    species_label = STAT_FONT.render(f"Species: {species_count}", 1, (255, 255, 255))
    win.blit(species_label, (10, 170))
    best_score_label = STAT_FONT.render(f"Best Score: {BEST_SCORE}", 1, (255, 255, 255))
    win.blit(best_score_label, (WIN_WIDTH - best_score_label.get_width() - 10, 10))

    pygame.display.update()


def eval_genomes(genomes, config, population):
    global GEN, MAX_FITNESS, BEST_SCORE
    GEN += 1

    nets, ge, birds = [], [], []

    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(130, 250))
        ge.append(genome)

    base = Base(FLOOR)
    pipes = [Pipe(WIN_WIDTH)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    run = True
    while run and len(birds) > 0:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].width:
                pipe_ind = 1

        for x, bird in enumerate(birds):
            ge[x].fitness += 0.1
            bird.move()
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                bird.jump()

        base.move()

        rem, add_pipe = [], False
        for pipe in pipes:
            pipe.move()
            for bird in birds:
                if pipe.collide(bird):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.width < 0:
                rem.append(pipe)
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            if score > BEST_SCORE: BEST_SCORE = score
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.height >= FLOOR or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        current_max_fitness = 0
        if ge:
            current_max_fitness = max(g.fitness for g in ge)
        MAX_FITNESS = current_max_fitness

        species_count = len(population.species.species)
        draw_window(win, birds, pipes, base, score, GEN, MAX_FITNESS, species_count)


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(lambda genomes, config: eval_genomes(genomes, config, p), 50)
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
