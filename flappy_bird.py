import pygame
import random
import os


class Bird:
    IMGS = [pygame.transform.scale2x(pygame.image.load(
        os.path.join("assets", "bird" + str(i) + ".png"))) for i in range(1, 4)]
    GRAVITY = 1.5
    ANIM_DURATION = 5
    ROT_VEL = 20
    MAX_ROT = 25
    
    def __init__(self, pos):
        self.x = pos[0]
        self.y = pos[1]
        self.tilt = 0
        self.tick = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        #(0,0) is the top left corner
        self.vel = -10
        # this is the time count
        self.tick = 0
        self.height = self.y

    def move(self):
        #time elapses...
        self.tick += 1
        displacement = max(15, self.vel*self.tick + self.GRAVITY*self.tick**2)
        self.y += displacement
        if displacement < 0 or self.y < self.height + 50:
            self.tilt = max(self.MAX_ROT, self.tilt)
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, surface):
        self.img_count = 0 if self.img_count + 1 >= self.ANIM_DURATION * 3 else self.img_count + 1
        # don't flap the wing if titled almost 90 deg...
        self.img = self.IMGS[1] if self.tilt <= -80 else self.IMGS[self.img_count//self.ANIM_DURATION]

        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        surface.blit(rotated_img, new_rect.topleft)

    # needed for collision detection
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    PIPE_IMG = pygame.transform.scale2x(pygame.image.load(
        os.path.join("assets", "pipe.png")))
    GAP = 200
    VEL = 5
    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(self.PIPE_IMG.convert_alpha(), False, True)
        self.PIPE_BOTTOM = self.PIPE_IMG.convert_alpha()
        self.passed = False #game logic
        self.set_height()
        self.width = self.PIPE_TOP.get_width()
    
    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
            self.x -= self.VEL

    def draw(self, surface):
        """
        draw both the top and bottom of the pipe
        :param surface: pygame surface
        :return: None
        """
        # draw top
        surface.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        surface.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        """
        returns if a pixel of bird is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        bottom_overlap = bird_mask.overlap(bottom_mask, bottom_offset)
        top_overlap = bird_mask.overlap(top_mask, top_offset)

        return True if bottom_overlap or top_overlap else False


class Base:
    """
    Represnts the moving floor
    """
    BASE_IMG = pygame.transform.scale2x(pygame.image.load(
        os.path.join("assets", "base.png")))
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    

    def __init__(self, y):
        """
        Initialize the object
        :param y: int
        :return: None
        """
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH #two base floor wrap around the game field horizontally
        self.img = IMG = self.BASE_IMG.convert_alpha()

    def move(self):
        """
        move floor so it looks like its scrolling
        :return: None
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, surface):
        """
        Draw the floor. Two images move along horizontally and wrap around
        :param surface: the pygame surface
        :return: None
        """
        surface.blit(self.img, (self.x1, self.y))
        surface.blit(self.img, (self.x2, self.y))

class App:
    WIDTH, HEIGHT = 600, 800
    def __init__(self):
        self._running = True
        self.size = self.WIDTH, self.HEIGHT
        self.remove_pipes = []
        self.score = 0
    
    def on_init(self):
        pygame.init()
        pygame.display.set_caption("Flappy Bird")
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.BG_IMG = pygame.transform.scale(pygame.image.load(
            os.path.join("assets", "bg.png")).convert_alpha(), self.size)
        self.bird = Bird((200,200))
        self.base = Base(self.WIDTH)
        #self.pipes = [Pipe(self.width+i*self.width*1.2/self.num_of_pipes) for i in range(0,self.num_of_pipes+1)]
        self.pipes = [Pipe(self.WIDTH)]
        self._clock = pygame.time.Clock()
        self._running = True

    def draw(self):
        self._display_surf.blit(self.BG_IMG, (0,0))
        self.base.draw(self._display_surf)
        self.bird.draw(self._display_surf)
        for pipe in self.pipes:
            pipe.draw(self._display_surf)
    
        pygame.display.update()

    def on_event(self, event):
        self._clock.tick(60)
        if event.type == pygame.QUIT:
            self._running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.pause()
             
    def on_loop(self):
        self.base.move()
        add_pipe = False
        for pipe in self.pipes:
            #TODO: check collision
            pipe.move()
            if pipe.collide(self.bird):
                pass
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                #put the pipe on remove list
                self.remove_pipes.append(pipe)
                
            if not pipe.passed and pipe.x < self.bird.x:
                pipe.passed = True
                add_pipe = True
                self.score += 10

        if add_pipe:
            self.pipes.append(Pipe(self.WIDTH))
        #remove the pipe in remove list
        if self.remove_pipes and self.pipes:
            for p in self.remove_pipes:
                self.pipes.remove(p)
            self.remove_pipes.clear()

        self.draw()
        
    def on_render(self):
        pass

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while ( self._running ):
            #controls the game frame rate 30 frames per second:
            self._clock.tick(30)
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()

