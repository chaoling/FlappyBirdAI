import pygame
import random
import os

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(
    os.path.join("assets", "bird" + str(i) + ".png"))) for i in range(1, 4)]
class Bird:
    IMGS = BIRD_IMGS
    
    def __init__(self, pos):
        self.x = pos[0]
        self.y = pos[1]
        self.tilt = 0
        self.tick = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
        self.gravity = 1.5
        self.anim_duration = 5
        self.rot_vel = 20
        self.max_rot = 25

    def jump(self):
        #(0,0) is the top left corner
        self.vel = -10
        # this is the time count
        self.tick = 0
        self.height = self.y

    def move(self):
        #time elapses...
        self.tick += 1
        displacement = max(15, self.vel*self.tick + self.gravity*self.tick**2)
        self.y += displacement
        if displacement < 0 or self.y < self.height + 50:
            self.tilt = max(self.max_rot, self.tilt)
        else:
            if self.tilt > -90:
                self.tilt -= self.rot_vel

    def draw(self, surface):
        self.img_count = 0 if self.img_count + 1 >= self.anim_duration * 3 else self.img_count + 1
        # don't flap the wing if titled almost 90 deg...
        self.img = self.IMGS[1] if self.tilt <= -80 else self.IMGS[self.img_count//self.anim_duration]

        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        surface.blit(rotated_img, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_suface(self.img)
        
class App:
    def __init__(self,title):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 600, 800
        self.title = title
    
    def draw(self):
        self._display_surf.blit(self.bg_img, (0,0))
        #self.bird.move()
        self.bird.draw(self._display_surf)
        pygame.display.update()

    def on_init(self):
        pygame.init()
        pygame.display.set_caption(self.title)
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.pipe_img = pygame.transform.scale2x(pygame.image.load(
            os.path.join("assets", "pipe.png")).convert_alpha())
        self.bg_img = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bg.png")).convert_alpha(), (self.width, self.height))
        self.base_img = pygame.transform.scale2x(pygame.image.load(
                os.path.join("assets", "base.png")).convert_alpha())
        self.bird = Bird((200,200))
        self._clock = pygame.time.Clock()
        self._running = True

    def on_event(self, event):
        self._clock.tick(60)
        if event.type == pygame.QUIT:
            self._running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.pause()
             

    def on_loop(self):
        self.draw()
        
    def on_render(self):
        pass

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while ( self._running ):
            self._clock.tick(30)
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

if __name__ == "__main__" :
    theApp = App("Flappy Bird")
    theApp.on_execute()

