import pygame
import random
import os
import time
import neat

# Inisialisasi font untuk statistik
pygame.font.init()

# Konstanta untuk ukuran jendela
WIN_WIDTH = 550
WIN_HEIGHT = 800

# Konstanta untuk warna (menggantikan gambar)
COLOR_BIRD = (255, 200, 0)   # Kuning
COLOR_PIPE = (0, 200, 0)     # Hijau
COLOR_BASE = (200, 150, 100) # Coklat
COLOR_BG = (100, 149, 237)   # Biru Langit
COLOR_TEXT = (255, 255, 255) # Putih

# Font untuk statistik
STAT_FONT = pygame.font.SysFont("comicsans", 40)

class Bird:
    """
    Kelas untuk objek Burung
    """
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.jump_height = self.y  # Posisi y saat melompat, BUKAN tinggi gambar
        self.img_count = 0
        # Dimensi gambar burung
        self.width = 30
        self.height = 30

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.jump_height = self.y  # Catat posisi saat melompat

    def move(self):
        self.tick_count += 1
        # Fisika dasar untuk lompatan (gerak parabola)
        displacement = self.vel * self.tick_count + 1.5 * self.tick_count**2
        if displacement >= 16:
            displacement = 16
        if displacement < 0:
            displacement -= 2
        self.y = self.y + displacement

        # Mengatur kemiringan burung
        if displacement < 0 or self.y < self.jump_height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        # Menggambar placeholder burung (persegi)
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(win, COLOR_BIRD, rect)

    def get_mask(self):
        # Membuat mask untuk deteksi tabrakan
        mask_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(mask_surface, (255, 255, 255, 255), (0, 0, self.width, self.height))
        return pygame.mask.from_surface(mask_surface)


class Pipe:
    """
    Kelas untuk objek Pipa
    """
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP_SURFACE = pygame.Surface((50, 800))
        self.PIPE_BOTTOM_SURFACE = pygame.Surface((50, 800))

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP_SURFACE.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        # Menggambar pipa atas
        top_rect = pygame.Rect(self.x, self.top, 50, self.PIPE_TOP_SURFACE.get_height())
        pygame.draw.rect(win, COLOR_PIPE, top_rect)
        # Menggambar pipa bawah
        bottom_rect = pygame.Rect(self.x, self.bottom, 50, self.PIPE_BOTTOM_SURFACE.get_height())
        pygame.draw.rect(win, COLOR_PIPE, bottom_rect)

    def collide(self, bird):
        bird_mask = bird.get_mask()

        # Mask untuk pipa atas dan bawah
        top_mask_surface = pygame.Surface((50, self.PIPE_TOP_SURFACE.get_height()), pygame.SRCALPHA)
        top_mask_surface.fill((255, 255, 255))
        top_mask = pygame.mask.from_surface(top_mask_surface)

        bottom_mask_surface = pygame.Surface((50, self.PIPE_BOTTOM_SURFACE.get_height()), pygame.SRCALPHA)
        bottom_mask_surface.fill((255, 255, 255))
        bottom_mask = pygame.mask.from_surface(bottom_mask_surface)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True
        return False

class Base:
    """
    Kelas untuk objek Dasar (lantai)
    """
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
        pygame.draw.rect(win, COLOR_BASE, (self.x1, self.y, self.WIDTH, WIN_HEIGHT - self.y))
        pygame.draw.rect(win, COLOR_BASE, (self.x2, self.y, self.WIDTH, WIN_HEIGHT - self.y))


def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    """
    Menggambar semua elemen ke jendela permainan
    """
    win.fill(COLOR_BG)

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        bird.draw(win)

    # Teks Statistik
    score_label = STAT_FONT.render("Score: " + str(score), 1, COLOR_TEXT)
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    gen_label = STAT_FONT.render("Gen: " + str(gen), 1, COLOR_TEXT)
    win.blit(gen_label, (10, 10))

    alive_label = STAT_FONT.render("Alive: " + str(len(birds)), 1, COLOR_TEXT)
    win.blit(alive_label, (10, 50))

    pygame.display.update()

# Variabel global untuk melacak generasi
GEN = 0

def eval_genomes(genomes, config):
    """
    Fungsi ini akan menjalankan simulasi untuk setiap populasi (generasi)
    dan menghitung skor fitness untuk setiap burung.
    """
    global GEN
    GEN += 1

    nets = []
    ge = []
    birds = []

    for _, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        genome.fitness = 0
        ge.append(genome)

    base = Base(730)
    pipes = [Pipe(700)]
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
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP_SURFACE.get_width():
                pipe_ind = 1

        for x, bird in enumerate(birds):
            ge[x].fitness += 0.1
            bird.move()

            # Memberi input ke jaringan saraf dan mendapatkan output
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  # Jika output > 0.5, burung akan melompat
                bird.jump()

        rem = []
        add_pipe = False
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP_SURFACE.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.height >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win, birds, pipes, base, score, GEN, pipe_ind)


def run(config_path):
    """
    Memuat konfigurasi NEAT, membuat populasi, dan menjalankan algoritma.
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    p = neat.Population(config)

    # Menambahkan reporter untuk menampilkan progress di konsol
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Menjalankan algoritma untuk maksimal 50 generasi
    winner = p.run(eval_genomes, 50)

    # Menampilkan statistik pemenang
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == "__main__":
    # Menentukan path ke file konfigurasi dan menjalankan fungsi run
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
