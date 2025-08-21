import pygame
import neat
import time
import os
import random

pygame.font.init()

# Ukuran jendela baru
WIN_WIDTH = 400
WIN_HEIGHT = 600
FLOOR = 530 # Posisi y untuk lantai
STAT_FONT = pygame.font.SysFont("comicsans", 40)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = True

# --- Memuat Aset Gambar ---
# Saya akan membungkus ini dalam try-except untuk menangani jika file tidak ada
try:
    BIRD_IMGS = [
        pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "bird" + str(x) + ".png")))
        for x in range(1, 4)
    ]
    PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "pipe.png")).convert_alpha())
    BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "base.png")).convert_alpha())
    BG_IMG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bg.png")).convert_alpha(), (WIN_WIDTH, WIN_HEIGHT))
    ASSETS_LOADED = True
except (pygame.error, FileNotFoundError) as e:
    ASSETS_LOADED = False
    print("Gagal memuat aset gambar! Pastikan file gambar ada di folder 'assets'.")
    print("Daftar file yang dibutuhkan: bird1.png, bird2.png, bird3.png, pipe.png, base.png, bg.png")
    print(f"Error: {e}")
# -------------------------

GEN = 0
MAX_FITNESS = 0
BEST_SCORE = 0

# --- Kelas yang Dirombak Menggunakan pygame.sprite.Sprite ---

class Bird(pygame.sprite.Sprite):
    IMGS = BIRD_IMGS if ASSETS_LOADED else []
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.image = self.IMGS[0] if ASSETS_LOADED else pygame.Surface((30,30))
        if not ASSETS_LOADED: self.image.fill((255,255,0))
        self.rect = self.image.get_rect(topleft=(x, y))

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        displacement = self.vel * (self.tick_count) + 0.5 * (3) * (self.tick_count) ** 2
        if displacement >= 16:
            displacement = (displacement / abs(displacement)) * 16
        if displacement < 0:
            displacement -= 2
        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

        self.rect.y = self.y

    def draw(self, win):
        self.img_count += 1
        if self.img_count <= self.ANIMATION_TIME:
            self.image = self.IMGS[0] if ASSETS_LOADED else self.image
        elif self.img_count <= self.ANIMATION_TIME * 2:
            self.image = self.IMGS[1] if ASSETS_LOADED else self.image
        elif self.img_count <= self.ANIMATION_TIME * 3:
            self.image = self.IMGS[2] if ASSETS_LOADED else self.image
        elif self.img_count <= self.ANIMATION_TIME * 4:
            self.image = self.IMGS[1] if ASSETS_LOADED else self.image
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.image = self.IMGS[0] if ASSETS_LOADED else self.image
            self.img_count = 0

        if self.tilt <= -80:
            self.image = self.IMGS[1] if ASSETS_LOADED else self.image
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.image, self.tilt)
        new_rect = rotated_image.get_rect(center=self.image.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe(pygame.sprite.Sprite):
    GAP = 200
    VEL = 5

    def __init__(self, x):
        super().__init__()
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) if ASSETS_LOADED else pygame.Surface((50,300))
        self.PIPE_BOTTOM = PIPE_IMG if ASSETS_LOADED else pygame.Surface((50,300))
        if not ASSETS_LOADED:
            self.PIPE_TOP.fill((0,255,0))
            self.PIPE_BOTTOM.fill((0,255,0))

        self.passed = False
        self.set_height()

        self.rect_top = self.PIPE_TOP.get_rect(topleft=(self.x, self.top))
        self.rect_bottom = self.PIPE_BOTTOM.get_rect(topleft=(self.x, self.bottom))

    def set_height(self):
        self.height = random.randrange(50, 350)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL
        self.rect_top.x = self.x
        self.rect_bottom.x = self.x

    def draw(self, win):
        win.blit(self.PIPE_TOP, self.rect_top.topleft)
        win.blit(self.PIPE_BOTTOM, self.rect_bottom.topleft)

    def collide(self, bird, win):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if b_point or t_point:
            return True
        return False


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width() if ASSETS_LOADED else WIN_WIDTH
    IMG = BASE_IMG if ASSETS_LOADED else None

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
        if ASSETS_LOADED:
            win.blit(self.IMG, (self.x1, self.y))
            win.blit(self.IMG, (self.x2, self.y))
        else:
            pygame.draw.rect(win, (200,150,100), (0, FLOOR, WIN_WIDTH, WIN_HEIGHT - FLOOR))

def draw_window(win, birds, pipes, base, score, gen, fitness, species_count):
    if ASSETS_LOADED:
        win.blit(BG_IMG, (0, 0))
    else:
        win.fill((100, 149, 237))  # Fallback to blue if no assets

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        bird.draw(win)

    # Statistik
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (10, 10))

    gen_label = STAT_FONT.render("Gen: " + str(gen),1,(255,255,255))
    win.blit(gen_label, (10, 50))

    alive_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(alive_label, (10, 90))

    fitness_label = STAT_FONT.render(f"Max Fitness: {fitness:.2f}", 1, (255, 255, 255))
    win.blit(fitness_label, (10, 130))

    species_label = STAT_FONT.render(f"Species: {species_count}", 1, (255, 255, 255))
    win.blit(species_label, (10, 170))

    best_score_label = STAT_FONT.render(f"Best Score: {BEST_SCORE}", 1, (255, 255, 255))
    win.blit(best_score_label, (WIN_WIDTH - best_score_label.get_width() - 10, 10))

    pygame.display.update()


def eval_genomes(genomes, config, population): # Terima objek populasi
    global GEN, MAX_FITNESS, BEST_SCORE
    GEN += 1

    nets = []
    birds = []
    ge = []

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
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1

        for x, bird in enumerate(birds):
            ge[x].fitness += 0.1
            bird.move()
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                bird.jump()

        base.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            for bird in birds:
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            if score > BEST_SCORE:
                BEST_SCORE = score
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.image.get_height() - 10 >= FLOOR or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        current_max_fitness = 0
        for g in ge:
            if g.fitness > current_max_fitness:
                current_max_fitness = g.fitness
        MAX_FITNESS = current_max_fitness

        # Dapatkan jumlah spesies dari objek populasi
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

    # Gunakan lambda untuk meneruskan objek populasi 'p' ke eval_genomes
    winner = p.run(lambda genomes, config: eval_genomes(genomes, config, p), 50)
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    if not ASSETS_LOADED:
        print("\nExiting due to missing assets.")
    else:
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config-feedforward.txt')
        run(config_path)
