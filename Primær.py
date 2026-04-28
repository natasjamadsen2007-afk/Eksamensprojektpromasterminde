import pygame
import random
import sys
import time

pygame.init()

WIDTH, HEIGHT = 500, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dansk Wordle")

WHITE = (255,255,255)
GRAY = (200,200,200)
GREEN = (106,170,100)
YELLOW = (201,180,88)
DARK = (120,124,126)
BLACK = (0,0,0)

font = pygame.font.SysFont(None,50)
small_font = pygame.font.SysFont(None,28)

keyboard_rows = [
    "qwertyuiopå",
    "asdfghjklæø",
    "↵zxcvbnm⌫"
]

key_rects = {}

stats = [0,0,0,0,0,0,0]  # 1-6 guesses + losses


def hent_ord():
    with open("ordliste.txt","r",encoding="utf-8") as fil:
        ordliste = fil.read().splitlines()

    gyldige = [
        o.strip().lower()
        for o in ordliste
        if len(o.strip()) == 5 and o.isalpha()
    ]

    return random.choice(gyldige)


def start_spil():
    return {
        "hemmeligt_ord": hent_ord(),
        "current_guess":"",
        "guesses":[],
        "feedbacks":[],
        "start_tid":time.time(),
        "slut_tid":None
    }


def opdater_bogstaver(spil):
    status={}
    for guess,feedback in zip(spil["guesses"],spil["feedbacks"]):
        for letter,color in zip(guess,feedback):
            if letter not in status:
                status[letter]=color
            else:
                if status[letter]!=GREEN:
                    status[letter]=color
    return status


def draw_grid(spil):

    cell=60
    gap=10

    start_x=(WIDTH-(5*cell+4*gap))//2
    start_y=60

    for row in range(6):
        for col in range(5):

            x=start_x+col*(cell+gap)
            y=start_y+row*(cell+gap)

            rect=pygame.Rect(x,y,cell,cell)

            if row<len(spil["feedbacks"]):
                color=spil["feedbacks"][row][col]
            else:
                color=GRAY

            pygame.draw.rect(screen,color,rect)
            pygame.draw.rect(screen,BLACK,rect,2)

            letter=None

            if row<len(spil["guesses"]) and col<len(spil["guesses"][row]):
                letter=spil["guesses"][row][col]

            elif row==len(spil["guesses"]) and col<len(spil["current_guess"]):
                letter=spil["current_guess"][col]

            if letter:
                text=font.render(letter.upper(),True,BLACK)
                text_rect=text.get_rect(center=rect.center)
                screen.blit(text,text_rect)


def draw_keyboard(spil):

    global key_rects
    key_rects={}

    status=opdater_bogstaver(spil)

    start_y=500
    key_w=35
    key_h=45
    gap=5

    for row_i,row in enumerate(keyboard_rows):

        row_width=len(row)*(key_w+gap)
        start_x=(WIDTH-row_width)//2

        for i,letter in enumerate(row):

            x=start_x+i*(key_w+gap)
            y=start_y+row_i*(key_h+gap)

            rect=pygame.Rect(x,y,key_w,key_h)
            key_rects[letter]=rect

            color=GRAY

            if letter in status:
                color=status[letter]

            pygame.draw.rect(screen,color,rect,border_radius=6)
            pygame.draw.rect(screen,BLACK,rect,2,border_radius=6)

            text=small_font.render(letter.upper(),True,BLACK)
            text_rect=text.get_rect(center=rect.center)
            screen.blit(text,text_rect)


def check_guess(guess,hemmeligt):

    result=[]
    for i in range(5):

        if guess[i]==hemmeligt[i]:
            result.append(GREEN)

        elif guess[i] in hemmeligt:
            result.append(YELLOW)

        else:
            result.append(DARK)

    return result


def draw_timer(start_tid):
    tid=int(time.time()-start_tid)
    text=small_font.render(f"Tid: {tid}s",True,BLACK)
    screen.blit(text,(20,20))


def draw_end_screen(vandt, spil):
    # Fylder hele skærmen med hvid baggrund
    screen.fill(WHITE)

    # Viser titel afhængigt af om spilleren vandt eller tabte
    title = "Du vandt!" if vandt else "Du tabte!"
    text = font.render(title, True, BLACK)
    screen.blit(text, (160, 40))

    # Viser det hemmelige ord
    ord_text = small_font.render(f"Ordet var: {spil['hemmeligt_ord'].upper()}", True, BLACK)
    screen.blit(ord_text, (170, 100))

    # Viser antal gæt hvis man vandt, ellers fast tekst
    if vandt:
        score = len(spil["guesses"])
        score_text = small_font.render(f"Du brugte {score} gæt", True, BLACK)
    else:
        score_text = small_font.render("Du brugte alle 6 gæt", True, BLACK)

    screen.blit(score_text, (170, 130))

    # Beregner hvor lang tid spillet tog
    tid = int(spil["slut_tid"] - spil["start_tid"])
    tid_text = small_font.render(f"Tid: {tid} sek", True, BLACK)
    screen.blit(tid_text, (170, 160))

    # Finder højeste værdi i statistik (for at skalere søjlediagram)
    max_val = max(stats) if max(stats) > 0 else 1

    # Indstillinger for søjlediagram
    bar_width = 40
    spacing = 20
    start_x = 40
    base_y = 420

    # Labels til x-aksen
    labels = ["1", "2", "3", "4", "5", "6", "Tabt"]

    # Tegner søjlediagram
    for i, val in enumerate(stats):

        # Skalerer højden på søjlen
        bar_height = int((val / max_val) * 200)

        # Beregner position
        x = start_x + i * (bar_width + spacing)
        y = base_y - bar_height

        # Tegner selve søjlen
        pygame.draw.rect(screen, GRAY, (x, y, bar_width, bar_height))
        pygame.draw.rect(screen, BLACK, (x, y, bar_width, bar_height), 2)

        # Tegner label under søjlen
        l = small_font.render(labels[i], True, BLACK)
        l_rect = l.get_rect(center=(x + bar_width // 2, base_y + 20))
        screen.blit(l, l_rect)

        # Viser tal over søjlen
        num = small_font.render(str(val), True, BLACK)
        num_rect = num.get_rect(center=(x + bar_width // 2, y - 15))
        screen.blit(num, num_rect)

    # Opretter "Spil igen" knap
    button = pygame.Rect(170, 520, 160, 60)
    pygame.draw.rect(screen, GREEN, button)

    # Tekst på knappen
    t = small_font.render("Spil igen", True, BLACK)
    t_rect = t.get_rect(center=button.center)
    screen.blit(t, t_rect)

    # Returnerer knappen så vi kan registrere klik
    return button


# Starttilstand
state = "menu"
spil = None
vandt = False

running = True

# Hoved game loop
while running:

    # Ryd skærmen hver frame
    screen.fill(WHITE)

    if state == "menu":
        # Tegner menu
        title = font.render("Dansk Wordle", True, BLACK)
        screen.blit(title, (150, 200))

        # Start knap
        start_knap = pygame.Rect(170, 320, 160, 70)
        pygame.draw.rect(screen, GREEN, start_knap)

        t = small_font.render("Start spil", True, BLACK)
        screen.blit(t, (205, 345))

    elif state == "spil":
        # Tegner selve spillet
        draw_grid(spil)
        draw_timer(spil["start_tid"])
        draw_keyboard(spil)

    elif state == "slut":
        # Tegner slutskærm
        play_button = draw_end_screen(vandt, spil)

    pygame.display.flip()

    # Event loop (input fra bruger)
    for event in pygame.event.get():

        # Luk spillet
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if state == "menu":
            # Klik på start
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_knap.collidepoint(event.pos):
                    spil = start_spil()
                    state = "spil"

        elif state == "spil":

            # Tastatur input
            if event.type == pygame.KEYDOWN:

                # Slet sidste bogstav
                if event.key == pygame.K_BACKSPACE:
                    spil["current_guess"] = spil["current_guess"][:-1]

                # Enter trykkes
                elif event.key == pygame.K_RETURN:

                    if len(spil["current_guess"]) == 5:

                        guess = spil["current_guess"]

                        # Gem gæt og feedback
                        spil["guesses"].append(guess)
                        spil["feedbacks"].append(check_guess(guess, spil["hemmeligt_ord"]))

                        # Hvis korrekt gæt
                        if guess == spil["hemmeligt_ord"]:
                            stats[len(spil["guesses"]) - 1] += 1
                            vandt = True
                            spil["slut_tid"] = time.time()
                            state = "slut"

                        # Hvis brugt alle forsøg
                        elif len(spil["guesses"]) == 6:
                            stats[6] += 1
                            vandt = False
                            spil["slut_tid"] = time.time()
                            state = "slut"

                        # Nulstil input
                        spil["current_guess"] = ""

                else:
                    # Tilføj bogstav hvis gyldigt
                    if (
                        len(spil["current_guess"]) < 5
                        and event.unicode.lower() in "abcdefghijklmnopqrstuvwxyzæøå"
                    ):
                        spil["current_guess"] += event.unicode.lower()

            # Mus input (klik på virtuelt keyboard)
            if event.type == pygame.MOUSEBUTTONDOWN:

                pos = event.pos

                for letter, rect in key_rects.items():

                    if rect.collidepoint(pos):

                        if letter == "⌫":
                            spil["current_guess"] = spil["current_guess"][:-1]

                        elif letter == "↵":

                            if len(spil["current_guess"]) == 5:

                                guess = spil["current_guess"]

                                spil["guesses"].append(guess)
                                spil["feedbacks"].append(
                                    check_guess(guess, spil["hemmeligt_ord"])
                                )

                                if guess == spil["hemmeligt_ord"]:
                                    stats[len(spil["guesses"]) - 1] += 1
                                    vandt = True
                                    spil["slut_tid"] = time.time()
                                    state = "slut"

                                elif len(spil["guesses"]) == 6:
                                    stats[6] += 1
                                    vandt = False
                                    spil["slut_tid"] = time.time()
                                    state = "slut"

                                spil["current_guess"] = ""

                        else:
                            # Tilføj bogstav fra mus klik
                            if len(spil["current_guess"]) < 5:
                                spil["current_guess"] += letter

        elif state == "slut":
            # Klik på "spil igen"
            if event.type == pygame.MOUSEBUTTONDOWN:

                if play_button.collidepoint(event.pos):
                    spil = start_spil()
                    state = "spil"