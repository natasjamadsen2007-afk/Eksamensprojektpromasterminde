import pygame
import random
import sys
import time

pygame.init()

# Skærm
WIDTH, HEIGHT = 500, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dansk Wordle")

# Farver
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
GREEN = (106, 170, 100)
YELLOW = (201, 180, 88)
DARK = (120, 124, 126)
BLACK = (0, 0, 0)

# Font
font = pygame.font.SysFont(None, 60)
small_font = pygame.font.SysFont(None, 40)

# 🔹 Hent ord fra fil
def hent_ord():
    with open("ordliste.txt", "r", encoding="utf-8") as fil:
        ordliste = fil.read().splitlines()

    gyldige_ord = [
        ord.strip().lower()
        for ord in ordliste
        if len(ord.strip()) == 5 and ord.isalpha()
    ]

    return random.choice(gyldige_ord)

# 🔹 Start nyt spil
def start_spil():
    return {
        "hemmeligt_ord": hent_ord(),
        "current_guess": "",
        "guesses": [],
        "feedbacks": [],
        "start_tid": time.time()
    }

# 🔹 Tegn grid
def draw_grid(spil):
    for row in range(6):
        for col in range(5):
            x = col * 80 + 50
            y = row * 80 + 100

            rect = pygame.Rect(x, y, 70, 70)

            if row < len(spil["feedbacks"]):
                color = spil["feedbacks"][row][col]
            else:
                color = GRAY

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)

            # Bogstaver
            if row < len(spil["guesses"]) and col < len(spil["guesses"][row]):
                letter = spil["guesses"][row][col].upper()
                text = font.render(letter, True, BLACK)
                screen.blit(text, (x + 20, y + 10))
            elif row == len(spil["guesses"]) and col < len(spil["current_guess"]):
                letter = spil["current_guess"][col].upper()
                text = font.render(letter, True, BLACK)
                screen.blit(text, (x + 20, y + 10))

# 🔹 Tjek gæt
def check_guess(guess, hemmeligt_ord):
    result = []
    for i in range(5):
        if guess[i] == hemmeligt_ord[i]:
            result.append(GREEN)
        elif guess[i] in hemmeligt_ord:
            result.append(YELLOW)
        else:
            result.append(DARK)
    return result

# 🔹 Tegn startmenu
def draw_menu():
    screen.fill(WHITE)

    title = font.render("Dansk Wordle", True, BLACK)
    screen.blit(title, (120, 150))

    button = pygame.Rect(150, 300, 200, 80)
    pygame.draw.rect(screen, GREEN, button)

    text = small_font.render("Start spil", True, BLACK)
    screen.blit(text, (180, 320))

    return button

# 🔹 Tegn timer
def draw_timer(start_tid):
    tid = int(time.time() - start_tid)
    timer_text = small_font.render(f"Tid: {tid}s", True, BLACK)
    screen.blit(timer_text, (20, 20))


# 🔹 Spiltilstande
state = "menu"
spil = None

# 🔹 Game loop
running = True
while running:
    screen.fill(WHITE)

    if state == "menu":
        start_knap = draw_menu()

    elif state == "spil":
        draw_grid(spil)
        draw_timer(spil["start_tid"])

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()

        # 🔹 MENU
        if state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_knap.collidepoint(event.pos):
                    spil = start_spil()
                    state = "spil"

        # 🔹 SPIL
        elif state == "spil":
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_BACKSPACE:
                    spil["current_guess"] = spil["current_guess"][:-1]

                elif event.key == pygame.K_RETURN:
                    if len(spil["current_guess"]) == 5:
                        guess = spil["current_guess"]

                        spil["guesses"].append(guess)
                        spil["feedbacks"].append(
                            check_guess(guess, spil["hemmeligt_ord"])
                        )

                        # Vundet
                        if guess == spil["hemmeligt_ord"]:
                            print("Du vandt!")
                            state = "menu"

                        # Tabt
                        elif len(spil["guesses"]) == 6:
                            print("Du tabte! Ordet var:", spil["hemmeligt_ord"])
                            state = "menu"

                        spil["current_guess"] = ""

                else:
                    if len(spil["current_guess"]) < 5 and event.unicode.isalpha():
                        spil["current_guess"] += event.unicode.lower()

pygame.quit()