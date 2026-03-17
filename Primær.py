import pygame
import random
import sys

pygame.init()

# Skærm
WIDTH, HEIGHT = 500, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mastermind Word Game")

# Farver
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
GREEN = (106, 170, 100)
YELLOW = (201, 180, 88)
DARK = (120, 124, 126)
BLACK = (0, 0, 0)

# Font
font = pygame.font.SysFont(None, 60)

# 🔹 Hent ord fra fil
def hent_ord():
    with open("ordliste.txt", "r", encoding="utf-8") as fil:
        ordliste = fil.read().splitlines()

    gyldige_ord = [
        ord.strip().lower()
        for ord in ordliste
        if len(ord.strip()) == 5 and ord.isalpha()
    ]

    if not gyldige_ord:
        raise ValueError("Ingen gyldige 5-bogstavsord fundet!")

    return random.choice(gyldige_ord)

hemmeligt_ord = hent_ord()

# Spil variabler
current_guess = ""
guesses = []
feedbacks = []
max_guesses = 6

# 🔹 Tegn grid
def draw_grid():
    screen.fill(WHITE)
    for row in range(6):
        for col in range(5):
            x = col * 80 + 50
            y = row * 80 + 50

            rect = pygame.Rect(x, y, 70, 70)

            if row < len(feedbacks):
                color = feedbacks[row][col]
            else:
                color = GRAY

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)

            # Bogstaver
            if row < len(guesses) and col < len(guesses[row]):
                letter = guesses[row][col].upper()
                text = font.render(letter, True, BLACK)
                screen.blit(text, (x + 20, y + 10))
            elif row == len(guesses) and col < len(current_guess):
                letter = current_guess[col].upper()
                text = font.render(letter, True, BLACK)
                screen.blit(text, (x + 20, y + 10))

# 🔹 Tjek gæt
def check_guess(guess):
    result = []
    for i in range(5):
        if guess[i] == hemmeligt_ord[i]:
            result.append(GREEN)
        elif guess[i] in hemmeligt_ord:
            result.append(YELLOW)
        else:
            result.append(DARK)
    return result

# 🔹 Game loop
running = True
while running:
    draw_grid()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                current_guess = current_guess[:-1]

            elif event.key == pygame.K_RETURN:
                if len(current_guess) == 5:
                    guesses.append(current_guess)
                    feedbacks.append(check_guess(current_guess))

                    if current_guess == hemmeligt_ord:
                        print("Du vandt!")
                        running = False

                    if len(guesses) == max_guesses:
                        print("Du tabte! Ordet var:", hemmeligt_ord)
                        running = False

                    current_guess = ""

            else:
                if len(current_guess) < 5 and event.unicode.isalpha():
                    current_guess += event.unicode.lower()

pygame.quit()