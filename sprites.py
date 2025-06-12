import pygame.sprite
from settings import width, height
from settings import *
from math import atan2,degrees
class Sprites(pygame.sprite.Sprite):
    def __init__(self,pos,surf,groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.ground= True

class CollisionSprites(pygame.sprite.Sprite):
    def __init__(self,pos,surf,group,collision_sprites= None):
        if collision_sprites:
            super().__init__(group,collision_sprites)
        else :
            super().__init__(group)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)


class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        self.player = player
        self.distance = 140
        self.player_direction = pygame.Vector2(1, 0)

        # Scale factor for gun - adjust this to make gun smaller/larger
        self.scale_factor = 0.5  # Makes gun 50% of original size

        super().__init__(groups)

        # Load original gun image
        original_gun_surf = pygame.image.load(join('images', 'gun', 'gun.png')).convert_alpha()

        # Scale the gun image
        scaled_size = (int(original_gun_surf.get_width() * self.scale_factor),
                       int(original_gun_surf.get_height() * self.scale_factor))
        self.gun_surf = pygame.transform.scale(original_gun_surf, scaled_size)

        self.image = self.gun_surf
        self.rect = self.image.get_rect(center=self.player.rect.center + self.player_direction * self.distance)

    def rotation_gun(self):
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90

        if self.player_direction.x > 0:
            # Use the scaled gun surface for rotation
            self.image = pygame.transform.rotozoom(self.gun_surf, angle, 1)
        else:
            # Use the scaled gun surface for rotation
            self.image = pygame.transform.rotozoom(self.gun_surf, abs(angle), 1)
            self.image = pygame.transform.flip(self.image, False, True)

    def get_direction(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(width / 2, height / 2)
        self.player_direction = (mouse_pos - player_pos).normalize()

    def update(self, _):
        self.rotation_gun()
        self.get_direction()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance


class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, group):
        super().__init__(group)

        # Scale factor for bullet - adjust this to make bullets smaller/larger
        bullet_scale_factor = 0.4  # Makes bullets 40% of original size

        # Load original bullet image
        original_bullet = pygame.image.load(join('images', 'gun', 'bullet.png'))

        # Scale the bullet image
        scaled_size = (int(original_bullet.get_width() * bullet_scale_factor),
                       int(original_bullet.get_height() * bullet_scale_factor))
        self.image = pygame.transform.scale(original_bullet, scaled_size)

        self.rect = self.image.get_rect(center=pos)
        self.direction = direction
        self.speed = 1000
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()  # Added missing kill() method

            self.kill()
class Enemy(pygame.sprite.Sprite):
    def __init__(self,pos,frames,group,player,collision_sprite):
        super().__init__(group)
        self.player = player
        self.frames,self.frame_index= frames,0
        self.image= self.frames[self.frame_index]
        self.animation_speed = 6
        self.rect = self.image.get_rect(center = pos)
        self.hitbox = self.rect.inflate(-20,-40)
        self.collision_sprites = collision_sprite
        self.direction = pygame.Vector2()
        self.speed= 100
        self.death_time = 0
        self.death_duration = 400
    def collision(self, direction):
        for sprite in self.collision_sprites:
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

    def move(self,dt):
        player_pos =pygame.Vector2(self.player.rect.center)
        enemy_pos=pygame.Vector2(self.rect.center)
        direction_vector = player_pos - enemy_pos
        if direction_vector.length() != 0:
            self.direction = direction_vector.normalize()
            self.hitbox.x += self.direction.x * self.speed * dt
            self.collision('horizontal')
            self.hitbox.y += self.direction.y * self.speed * dt
            self.collision('vertical')
            self.rect.center = self.hitbox.center
        else:
            self.direction = pygame.Vector2(0, 0)  # No movement if player is at same position

    def animate(self,dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
    def destroy(self):
        self.death_time = pygame.time.get_ticks()
        surf = pygame.mask.from_surface(self.frames[0]).to_surface()
        self.image= surf
        surf.set_colorkey('black')
    def death_timer(self):
        if pygame.time.get_ticks() - self.death_time >=self.death_duration:
            self.kill()
    def update(self,dt):
        if self.death_time == 0:
            self.animate(dt)
            self.move(dt)
        else:
            self.death_timer()





