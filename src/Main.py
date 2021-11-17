
import random

from pygame import mixer
import pygame

GAME_STATE_PLAY = 0
GAME_STATE_GAME_OVER = 1

MUTED = True

  
def check_bullets(explosion_sound, enemy_group, bulletDestroyThreshold, bullets):
    hits = 0

    for bullet in bullets:
        bullet.tick()
        bullet.draw()
        if bullet.get_y() < bulletDestroyThreshold:
            bullets.remove(bullet)

        collided_enemy = enemy_group.get_collided_enemy(bullet)
        if collided_enemy is not None:
            bullets.remove(bullet)
            enemy_group.kill_enemy(collided_enemy)

            hits += 1

            if not MUTED:
                explosion_sound.play()

    return hits

'''
Created on Sep 16, 2021

@author: bleem
'''


def clamp(value, minVal, maxVal):
    if value <= minVal:
        return minVal
    return min(value, maxVal)


def process_events(bulletImg, playerX_change, player, bullets):
    continue_running = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            continue_running = False
        if player is None:
            # ignore other button pushes
            continue

        # if keystroke is pressed check whether its right or left
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_LEFT:
                player.set_x_velocity(-playerX_change)
            elif event.key == pygame.K_RIGHT:
                player.set_x_velocity(playerX_change)
            elif event.key == pygame.K_SPACE:
                # create a bullet
                bulletX = player.get_center_x() - bulletImg.get_width() / 2
                bulletY = player.get_center_y() - bulletImg.get_height() / 2
                bullets.append(Bullet(bulletImg, bulletX, bulletY))

                if not MUTED:
                    bullet_sound.play()

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or pygame.K_RIGHT:
                player.set_x_velocity(0)

    return continue_running


class Entity:

    def __init__(self, img, x, y):
        self.img = img
        self.x = x
        self.y = y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def get_width(self):
        return self.img.get_width()

    def get_height(self):
        return self.img.get_height()

    def get_center_x(self):
        return self.get_x() + self.get_height() / 2

    def get_center_y(self):
        return self.get_y() + self.get_width() / 2

    def tick(self):
        pass

    def draw(self):
        screen.blit(self.img, (self.x, self.y))

    def collides_with(self, other_entity):

        y_diff = abs(self.get_center_y() - other_entity.get_center_y())
        collide_y = (self.get_height() + other_entity.get_height()) / 2

        if y_diff > collide_y:
            return False

        x_diff = abs(self.get_center_x() - other_entity.get_center_x())
        collide_x = (self.get_width() + other_entity.get_width()) / 2

        return x_diff <= collide_x


class Player(Entity):

    def __init__(self, img, x, y):
        super().__init__(img, x, y)
        self.x_velocity = 0

    def set_x_velocity(self, vel):
        self.x_velocity = vel

    def tick(self):
        self.x += self.x_velocity
        self.x = clamp(self.x, minPlayerX, maxPlayerX)


class EnemyGroup:

    def __init__(self, img, x, y, rows, cols, total_velocity):
        self.x = x
        self.y = y
        self.screen_width = pygame.display.get_surface().get_width()
        self.enemyImg = img
        self.rows = rows
        self.cols = cols
        self.total_velocity = total_velocity
        self.individual_velocity = total_velocity / (rows * cols)
        self.enemies = []
        self.moving_left = True
        for row in range(rows):
            for column in range(cols):
                enemy_x = enemy_group_x + column * (enemyImg.get_width() + enemy_px_gap)
                enemy_y = enemy_group_y + row * (enemyImg.get_height() + enemy_px_gap)
                self.enemies.append(Entity(enemyImg, enemy_x, enemy_y))

    def bounce_off_left_wall(self):
        self.moving_left = False
        self.move_down()

    def bounce_off_right_wall(self):
        self.moving_left = True
        self.move_down()

    def move_down(self):
        for enemy in self.enemies:
            enemy.set_y(enemy.get_y() + enemy_y_vel)

    def tick(self):
        # first detect bounce
        for enemy in self.enemies:
            if self.moving_left:
                if enemy.get_x() < 0:
                    self.bounce_off_left_wall()
            else:
                if enemy.get_x() + enemy.get_width() > self.screen_width:
                    self.bounce_off_right_wall()

        # then do standard movement
        for enemy in self.enemies:
            if self.moving_left:
                enemy.set_x(enemy.get_x() - self.individual_velocity)
            else:
                enemy.set_x(enemy.get_x() + self.individual_velocity)

    def get_collided_enemy(self, other):
        for enemy in self.enemies:
            if enemy.collides_with(other):
                return enemy

        return None

    def kill_enemy(self, to_kill):
        self.enemies.remove(to_kill)
        if len(self.enemies) > 0:
            self.individual_velocity = self.total_velocity / len(self.enemies)

    def draw(self):
        for enemy in self.enemies:
            enemy.draw()

    def all_enemies_dead(self):
        return len(self.enemies) == 0


class Bullet(Entity):

    def tick(self):
        self.y -= bulletVelY


if __name__ == '__main__':
    
    import gym
    
    env = gym.make('SpaceInvaders-v0')
    
    while(True):
        env.reset()
        for _ in range(1000):
            env.step(env.action_space.sample())
            env.render('human')
    
    env.close()  # https://github.com/openai/gym/issues/893
    
    game_state = GAME_STATE_PLAY

    pygame.init()

    if not MUTED:
        mixer.music.load("backgroundmusic.mp3")
        mixer.music.play(-1)

    bullet_sound = mixer.Sound("laser_shot.mp3")
    explosion_sound = mixer.Sound("explosion.wav")

    screenWidth = 800
    screenHeight = 600

    # create the screen
    screen = pygame.display.set_mode((screenWidth, screenHeight))

    enemy_rows = 3
    enemy_cols = 4
    enemy_px_gap = 10

    # background
    background = pygame.image.load("Background.png")

    # title and icon
    pygame.display.set_caption("Space Invaders")
    icon = pygame.image.load("ufo32x32.png")
    pygame.display.set_icon(icon)

    # enemy
    enemyImg = pygame.image.load("alien.png")
    max_enemy_group_x = screenWidth - enemyImg.get_width() * enemy_cols + enemy_px_gap * (enemy_cols - 1)
    enemy_group_x = random.randint(0, max_enemy_group_x)
    enemy_group_y = random.randint(50, 150)
    enemy_x_total_velocity = .1 * enemy_rows * enemy_cols
    enemy_y_vel = enemyImg.get_height() / 2
    enemy_group = EnemyGroup(enemyImg, enemy_group_x, enemy_group_y, enemy_rows, enemy_cols, enemy_x_total_velocity)

    # bullet
    bulletImg = pygame.image.load("bullet.png")
    bulletVelY = .4
    bulletDestroyThreshold = -100

    # player
    playerImg = pygame.image.load("space-invaders.png")
    playerX = (screenWidth - playerImg.get_width()) / 2
    playerY = 480
    playerX_change = .6
    minPlayerX = 0
    maxPlayerX = screenWidth - playerImg.get_width()
    player = Player(playerImg, playerX, playerY)

    # score
    score = 0
    font = pygame.font.Font("freesansbold.ttf", 32)
    score_x = 10
    score_y = 10

    # game loop
    running = True
    left_held = False
    right_held = False
    bullets = []

    while running:

        screen.blit(background, (0, 0))

        if game_state == GAME_STATE_PLAY:
            running = process_events(bulletImg, playerX_change, player, bullets)
            score += check_bullets(explosion_sound, enemy_group, bulletDestroyThreshold, bullets)

            score_display = font.render("Score: " + str(score), True, (255, 255, 255))
            screen.blit(score_display, (score_x, score_y))

            player.tick()
            player.draw()

            enemy_group.tick()
            enemy_group.draw()

            if enemy_group.get_collided_enemy(player) is not None:
                game_state = GAME_STATE_GAME_OVER

        elif game_state == GAME_STATE_GAME_OVER:
            game_over_text = pygame.font.Font("freesansbold.ttf", 64).render("GAME OVER", True, (255, 255, 255))
            screen.blit(game_over_text, (200, 250))
            running = process_events(None, None, None, None)

        pygame.display.update()

