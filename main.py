import pygame
import random
import math
import pygame_textinput
import sys
import names
import numpy as np
import time


FPS = 250
WORLD_WIDTH = 10000
WORLD_HEIGHT = 10000


WHITE = (255, 255, 255)
GREEN = (0, 255, 0)


def random_name():
    return names.get_first_name()


def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def get_player_name(screen, font):
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_active  # Set the initial color to color_active
    active = True  # Set the initial state of the input box to active
    text = ''
    done = False

    prompt_text = "Player Name:"
    prompt_surface = font.render(prompt_text, True, (255, 255, 255))  # Weiß
    prompt_rect = prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((30, 30, 30))
        screen.blit(prompt_surface, prompt_rect)
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()
        clock.tick(30)

    return text




def collide_rect_ratio(rect1, rect2, ratio=1.0):
    intersection = rect1.clip(rect2)
    if intersection.width == 0 or intersection.height == 0:
        return False

    intersection_area = intersection.width * intersection.height
    rect1_area = rect1.width * rect1.height
    rect2_area = rect2.width * rect2.height

    return intersection_area / rect1_area >= ratio or intersection_area / rect2_area >= ratio


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, size, name):
        super().__init__()
        self.name = name
        self.size = size
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GREEN, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 3
        self.points = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        self.rect.clamp_ip(pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT))

    def grow(self, growth):
        self.points += growth
        self.size += growth
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GREEN, (self.size // 2, self.size // 2), self.size // 2)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center



    def respawn(self):
        self.rect.center = (random.randint(100, WORLD_WIDTH - 100), random.randint(100, WORLD_HEIGHT - 100))
        self.points = 0
        self.size = 20
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GREEN, (self.size // 2, self.size // 2), self.size // 2)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        self.speed = 3

def update_scoreboard(player, ai_players, font, screen, game_time):
    all_players = [player] + [ai_player for ai_player in ai_players]
    sorted_players = sorted(all_players, key=lambda p: p.points, reverse=True)

    # Limit the number of displayed players to the top 5
    sorted_players = sorted_players[:5]

    BLACK = (0, 0, 0)
    screen_width = screen.get_width()

    # Render and display game time
    game_time_text = font.render(f"Playtime: {game_time:.0f} s", True, BLACK)
    game_time_rect = game_time_text.get_rect(topleft=(10, 10))
    screen.blit(game_time_text, game_time_rect)

    # Render and display player points
    player_points_text = font.render(f"Points: {player.points}", True, BLACK)
    player_points_rect = player_points_text.get_rect(topleft=(10, game_time_rect.bottom + 10))
    screen.blit(player_points_text, player_points_rect)

    for i, sorted_player in enumerate(sorted_players, 1):
        player_name = sorted_player.name if hasattr(sorted_player, "name") else "Player"
        points_text = font.render(f"{i}. {player_name}: {sorted_player.points}", True, BLACK)
        points_rect = points_text.get_rect(topleft=(10, player_points_rect.bottom + 40 * i))
        points_rect.right = screen_width - 10
        screen.blit(points_text, points_rect)




###################################################################################################################
#AI PLAYERS Class

class AIPlayer(Player):
    def __init__(self, x, y, size, name, color=None):
        super().__init__(x, y, size, name)
        if color is None:
            self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Generate random color
        else:
            self.color = color
        self.speed = 3
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (size // 2, size // 2), size // 2)


    def update(self):
        target = self.get_target(food_group, ai_players, player)
        if target:
            direction = pygame.Vector2(target.rect.center) - pygame.Vector2(self.rect.center)
            direction.normalize_ip()
            self.rect.x += int(direction.x * self.speed)
            self.rect.y += int(direction.y * self.speed)
        self.rect.clamp_ip(pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT))

    def get_target(self, food_group, ai_players, player):
        detection_range = 500
        targets = []
        escape_targets = []

        for food in food_group:
            distance = math.dist(self.rect.center, food.rect.center)
            if distance < detection_range:
                targets.append((food, distance))

        for other_player in ai_players.sprites() + [player]:
            if other_player == self:
                continue

            distance = math.dist(self.rect.center, other_player.rect.center)
            if distance < detection_range:
                priority_points = other_player.points if other_player.points > 0 else 0.1
                if self.points > other_player.points * 1.2:
                    targets.append((other_player, distance / priority_points))
                elif other_player.points > self.points * 1.2:  
                    escape_targets.append((other_player, distance))

        if not targets and not escape_targets:
            return None

        if escape_targets:
            closest_escape_target = min(escape_targets, key=lambda x: x[1])[0]
            escape_direction = pygame.Vector2(self.rect.center) - pygame.Vector2(closest_escape_target.rect.center)
            escape_direction.normalize_ip()
            escape_point = self.rect.center + escape_direction * detection_range
            return type("EscapeTarget", (pygame.sprite.Sprite,), {"rect": pygame.Rect(escape_point[0], escape_point[1], 0, 0)})()

        return min(targets, key=lambda x: x[1])[0]



    def grow(self, growth):
        self.points += growth
        self.size += growth
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.size // 2, self.size // 2), self.size // 2)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center




    def respawn(self):
        self.rect.center = (random.randint(100, WORLD_WIDTH - 100), random.randint(100, WORLD_HEIGHT - 100))
        self.points = 0
        self.size = 20
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.size // 2, self.size // 2), self.size // 2)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        self.speed = 3

############################################################################################################################################
#Food Class

class Food(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.image = pygame.Surface((size, size))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

def create_food(num_food, width, height):
    food_group = pygame.sprite.Group()
    for _ in range(num_food):
        x = random.randint(10, width - 10)
        y = random.randint(10, height - 10)
        food = Food(x, y, 5)
        food_group.add(food)
    return food_group

num_food = 2500
food_group = create_food(num_food, WORLD_WIDTH, WORLD_HEIGHT)

############################################################################################################################################


pygame.init()
info_object = pygame.display.Info()
WIDTH = info_object.current_w
HEIGHT = info_object.current_h

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)


pygame.mixer.music.load('background.mp3')
pygame.mixer.music.play(-1)

font = pygame.font.Font(None, 36)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Agario")
clock = pygame.time.Clock()
start_time = time.time()
zoom_level = 1.0

player_name = get_player_name(screen, font)
player = Player(WIDTH//2, HEIGHT//2, 20, player_name)
all_sprites = pygame.sprite.Group()




ai_players = pygame.sprite.Group()
for i in range(25):
    ai_player = AIPlayer(random.randint(100, WORLD_WIDTH - 100), random.randint(100, WORLD_HEIGHT - 100), 20, random_name())
    ai_players.add(ai_player)


all_sprites.add(ai_players)

food_group = create_food(num_food, WORLD_WIDTH, WORLD_HEIGHT)  
all_sprites.add(food_group)
camera = pygame.Vector2(0, 0)


running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.update()


    for ai_player in ai_players:
        ai_player.update()
        ai_eaten_food = pygame.sprite.spritecollide(ai_player, food_group, True)
        if ai_eaten_food:
            ai_player.grow(len(ai_eaten_food))
            new_food_group = create_food(len(ai_eaten_food), WORLD_WIDTH, WORLD_HEIGHT)
            all_sprites.add(new_food_group)
            food_group.add(new_food_group)

        collision = collide_rect_ratio(player.rect, ai_player.rect, ratio=1.0)
        if collision:
            if player.points > ai_player.points:
                player.grow(ai_player.points)
                ai_player.respawn()
            elif ai_player.points > player.points:
                ai_player.grow(player.points)
                player.respawn()

    eaten_food = pygame.sprite.spritecollide(player, food_group, True)
    if eaten_food:
        player.grow(len(eaten_food))
        new_food_group = create_food(len(eaten_food), WORLD_WIDTH, WORLD_HEIGHT)
        all_sprites.add(new_food_group)
        food_group.add(new_food_group)

    camera_x = min(max(-player.rect.x + WIDTH // 2, -WORLD_WIDTH + WIDTH), 0)
    camera_y = min(max(-player.rect.y + HEIGHT // 2, -WORLD_HEIGHT + HEIGHT), 0)
    camera = pygame.Vector2(camera_x, camera_y)


    for ai_player1 in ai_players:
        for ai_player2 in ai_players:
            if ai_player1 != ai_player2:
                collision = collide_rect_ratio(ai_player1.rect, ai_player2.rect, ratio=1.0)
                if collision:
                    if ai_player1.points > ai_player2.points:
                        ai_player1.grow(ai_player2.points)
                        ai_player2.respawn()
                    elif ai_player2.points > ai_player1.points:
                        ai_player2.grow(ai_player1.points)
                        ai_player1.respawn()



    screen.fill((255, 255, 255))
    for food in food_group:
        screen.blit(pygame.transform.scale(food.image, (int(food.rect.width * zoom_level), int(food.rect.height * zoom_level))), (int(food.rect.topleft[0] * zoom_level), int(food.rect.topleft[1] * zoom_level)) + camera)

    screen.blit(pygame.transform.scale(player.image, (int(player.rect.width * zoom_level), int(player.rect.height * zoom_level))), (int(player.rect.topleft[0] * zoom_level), int(player.rect.topleft[1] * zoom_level)) + camera)

    for ai_player in ai_players:
        screen.blit(pygame.transform.scale(ai_player.image, (int(ai_player.rect.width * zoom_level), int(ai_player.rect.height * zoom_level))), (int(ai_player.rect.topleft[0] * zoom_level), int(ai_player.rect.topleft[1] * zoom_level)) + camera)

    for ai_player in ai_players:
        screen.blit(ai_player.image, ai_player.rect.topleft + camera)
        ai_points_text = font.render(str(ai_player.points), True, WHITE)
        ai_points_rect = ai_points_text.get_rect(center=ai_player.rect.center)
        screen.blit(ai_points_text, ai_points_rect.topleft + camera)

    game_time = time.time() - start_time
    font = pygame.font.Font(None, 36)
    points_text = font.render(str(player.points), True, WHITE)
    points_rect = points_text.get_rect(center=player.rect.center)
    screen.blit(points_text, points_rect.topleft + camera)

    update_scoreboard(player, ai_players, font, screen, game_time)

    pygame.display.flip()


pygame.quit()