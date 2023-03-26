import pygame
pygame.init()
import time
import pyaudio
import struct
import numpy as np
from scipy.fftpack import fft
from threading import Thread

LOWER_FREQ = 100    # lower frequency limit of your voice sound 
HIGHER_FREQ = 2000  # higher frequency limit of you whistle sound

CHANNELS = 1                
FORMAT = pyaudio.paInt16     
RATE = 44100 * 4
CHUNK = 11025 * 2
MIDDLE_FREQ = (LOWER_FREQ + HIGHER_FREQ) / 2
VOLUME_THR = 0.6
NP_INPUT_MAX_VAR = 7000

WIDTH, HEIGHT = 700, 500
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_RADIUS = 7
WINNING_SCORE = 10
VEL_INCR = 1.05
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sound Pong")
SCORE_FONT = pygame.font.SysFont("comicsans", 50)

sound_command = False
direction = False

# pyaudio class instance
p = pyaudio.PyAudio()

# stream object to get data from microphone
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)

xf = np.linspace(0, RATE, CHUNK)
lower_prop = LOWER_FREQ / RATE
higher_prop = HIGHER_FREQ / RATE
l_idx = int(lower_prop * CHUNK)
h_idx = int(higher_prop * CHUNK)

class Paddle:
    COLOR = WHITE
    VEL = 3

    def __init__(self, x, y, width, height):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.width = width
        self.height = height

    def draw(self, win):
        pygame.draw.rect(
            win, self.COLOR, (self.x, self.y, self.width, self.height))

    def move(self, up=True):
        if up:
            self.y -= self.VEL
        else:
            self.y += self.VEL

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y

class Ball:
    MAX_VEL = 2
    COLOR = WHITE

    def __init__(self, x, y, radius):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.radius = radius
        self.x_vel = self.MAX_VEL
        self.y_vel = 0

    def draw(self, win):
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.y_vel = 0
        if self.x_vel > 0:
            self.x_vel = self.MAX_VEL
        else:
            self.x_vel = -self.MAX_VEL

def draw(win, paddles, ball, left_score, right_score):
    win.fill(BLACK)

    left_score_text = SCORE_FONT.render(f"{left_score}", 1, WHITE)
    right_score_text = SCORE_FONT.render(f"{right_score}", 1, WHITE)
    win.blit(left_score_text, (WIDTH//4 - left_score_text.get_width()//2, 20))
    win.blit(right_score_text, (WIDTH * (3/4) -
                                right_score_text.get_width()//2, 20))

    for paddle in paddles:
        paddle.draw(win)

    for i in range(10, HEIGHT, HEIGHT//20):
        if i % 2 == 1:
            continue
        pygame.draw.rect(win, WHITE, (WIDTH//2 - 5, i, 10, HEIGHT//20))

    ball.draw(win)
    pygame.display.update()


def handle_collision(ball, left_paddle, right_paddle):
    if ball.y + ball.radius >= HEIGHT:
        ball.y_vel *= -1
    elif ball.y - ball.radius <= 0:
        ball.y_vel *= -1

    if ball.x_vel < 0:
        if ball.y >= left_paddle.y and ball.y <= left_paddle.y + left_paddle.height:
            if ball.x - ball.radius <= left_paddle.x + left_paddle.width:
                ball.x_vel *= -VEL_INCR

                middle_y = left_paddle.y + left_paddle.height / 2
                difference_in_y = middle_y - ball.y
                reduction_factor = (left_paddle.height / 2) / ball.MAX_VEL
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1 * y_vel

    else:
        if ball.y >= right_paddle.y and ball.y <= right_paddle.y + right_paddle.height:
            if ball.x + ball.radius >= right_paddle.x:
                ball.x_vel *= -1.1

                middle_y = right_paddle.y + right_paddle.height / 2
                difference_in_y = middle_y - ball.y
                reduction_factor = (right_paddle.height / 2) / ball.MAX_VEL
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1 * y_vel

def handle_paddle_movement(keys, left_paddle, right_paddle, sound_command, direction):
    if sound_command and direction and (left_paddle.y - left_paddle.VEL) >= 0:
        left_paddle.move(up=True)
    if sound_command and not direction and (left_paddle.y + left_paddle.VEL + left_paddle.height <= HEIGHT):
        left_paddle.move(up=False)

    if keys[pygame.K_UP] and right_paddle.y - right_paddle.VEL >= 0:
        right_paddle.move(up=True)
    if keys[pygame.K_DOWN] and right_paddle.y + right_paddle.VEL + right_paddle.height <= HEIGHT:
        right_paddle.move(up=False)

def get_input_audio():
    global sound_command, direction

    while True:
        
        # binary data
        data = stream.read(CHUNK)  
        
        # convert data to integers, make np array, then offset it by 127
        data_int = struct.unpack(str(2 * CHUNK) + 'B', data)
        data_np = np.array(data_int, dtype='b')[::2] + 128
        relative_power = data_np.var()/NP_INPUT_MAX_VAR
        
        # compute FFT and update line
        yf = fft(data_int)
        yf_abs = np.abs(yf[0:CHUNK])  / (128 * CHUNK)
        idx_max_tf_abs = yf_abs[l_idx:h_idx].argmax() + l_idx
        max_vol_freq = xf[idx_max_tf_abs]

        if relative_power > VOLUME_THR:
            sound_command = True
            if max_vol_freq > MIDDLE_FREQ:
                direction = True
            else:
                direction = False
        else:
            sound_command = False

def main():
    global sound_command, direction

    run = True
    clock = pygame.time.Clock()


    left_paddle = Paddle(10, HEIGHT//2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)

    left_score = 0
    right_score = 0

    thread = Thread(target=get_input_audio)
    thread.start()
    time.sleep(5)

    while run:

        clock.tick(FPS)
        draw(WIN, [left_paddle, right_paddle], ball, left_score, right_score)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        
        handle_paddle_movement(keys, left_paddle, right_paddle, sound_command, direction)

        ball.move()
        handle_collision(ball, left_paddle, right_paddle)

        if ball.x < 0:
            right_score += 1
            ball.reset()
        elif ball.x > WIDTH:
            left_score += 1
            ball.reset()

        won = False
        if left_score >= WINNING_SCORE:
            won = True
            win_text = "Left Player Won!"
        elif right_score >= WINNING_SCORE:
            won = True
            win_text = "Right Player Won!"

        if won:
            text = SCORE_FONT.render(win_text, 1, WHITE)
            WIN.blit(text, (WIDTH//2 - text.get_width() //
                            2, HEIGHT//2 - text.get_height()//2))
            pygame.display.update()
            pygame.time.delay(5000)
            ball.reset()
            left_paddle.reset()
            right_paddle.reset()
            left_score = 0
            right_score = 0

    pygame.quit()

if __name__ == '__main__':
    main()
