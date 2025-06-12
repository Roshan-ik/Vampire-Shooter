import pygame.image
from settings import *
from os.path import join
from os import walk


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprite):
        super().__init__(groups)
        original_image = pygame.image.load(join('images', 'player', 'down', '0.png')).convert_alpha()
        # Scale factor - 0.5 means 50% of original size, 0.7 means 70%, etc.
        self.scale_factor = 0.6  # Adjust this value to make player smaller/larger
        scaled_size = (int(original_image.get_width() * self.scale_factor),
                       int(original_image.get_height() * self.scale_factor))
        self.image = pygame.transform.scale(original_image, scaled_size)

        self.rect = self.image.get_rect(center=pos)
        # Adjust hitbox for scaled size
        self.hitbox = self.rect.inflate(-int(60 * self.scale_factor), -int(50 * self.scale_factor))

        self.state, self.frames_index = 'left', 0
        self.direction = pygame.Vector2()
        self.speed = 500
        self.collision_sprite = collision_sprite
        self.load_images()

        self.max_health = 100
        self.current_health = 100
    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

    def load_images(self):
        self.frames = {'down': [], 'left': [], 'right': [], 'up': []}
        for state in self.frames.keys():
            for folder_path, subfolders, file_names in walk(join('images', 'player', state)):
                for filename in sorted(file_names, key=lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, filename)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.frames[state].append(surf)

    def move(self, dt):
        self.hitbox.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def health_bar(self, surface, camera_offset=None):
        bar_width = 100
        bar_height = 10
        if camera_offset:
            screen_x = self.rect.centerx - camera_offset[0] - bar_width // 2
            screen_y = self.rect.centery - camera_offset[1] - 30
        else:
            screen_x = 20
            screen_y = 20

        screen_x = max(10, min(screen_x, surface.get_width() - bar_width - 10))
        screen_y = max(10, min(screen_y, surface.get_height() - bar_height - 10))

        health_ratio = max(0, self.current_health / self.max_health)
        current_bar = int(bar_width * health_ratio)

        pygame.draw.rect(surface, (100, 0, 0), (screen_x, screen_y, bar_width, bar_height))
        if current_bar > 0:
            pygame.draw.rect(surface, (0, 255, 0), (screen_x, screen_y, current_bar, bar_height))
        pygame.draw.rect(surface, (255, 255, 255), (screen_x, screen_y, bar_width, bar_height), 2)

    def animation(self, dt):
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        if self.direction.y != 0:
            self.state = 'down' if self.direction.y > 0 else 'up'

        self.frames_index += 5 * dt if self.direction else 0
        self.image = self.frames[self.state][int(self.frames_index) % len(self.frames[self.state])]

    def take_damage(self, amount):
        self.current_health -= amount
        if self.current_health < 0:
            self.current_health = 0

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animation(dt)

    def collision(self, direction):
        for sprite in self.collision_sprite:
            if sprite.rect.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.rect.left
                    elif self.direction.x < 0:
                        self.hitbox.left = sprite.rect.right
                else:
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.rect.top
                    elif self.direction.y < 0:
                        self.hitbox.top = sprite.rect.bottom