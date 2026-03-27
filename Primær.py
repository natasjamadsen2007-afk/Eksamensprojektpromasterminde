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
RED = (200,80,80)

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
        "start_tid":time.time()
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


def draw_end_screen(vandt):

    screen.fill(WHITE)

    if vandt:
        title="Du vandt!"
    else:
        title="Du tabte!"

    text=font.render(title,True,BLACK)
    screen.blit(text,(170,50))

    pygame.draw.line(screen,BLACK,(50,120),(450,120),2)

    max_val=max(stats) if max(stats)>0 else 1

    for i,val in enumerate(stats):

        bar_w=40
        spacing=20

        x=50+i*(bar_w+spacing)
        bar_h=(val/max_val)*150

        y=300-bar_h

        pygame.draw.rect(screen,GRAY,(x,y,bar_w,bar_h))
        pygame.draw.rect(screen,BLACK,(x,y,bar_w,bar_h),2)

        label = str(i+1) if i<6 else "T"

        l=small_font.render(label,True,BLACK)
        screen.blit(l,(x+10,310))

        num=small_font.render(str(val),True,BLACK)
        screen.blit(num,(x+10,y-20))

    button=pygame.Rect(170,380,160,60)

    pygame.draw.rect(screen,GREEN,button)

    t=small_font.render("Spil igen",True,BLACK)
    screen.blit(t,(200,400))

    return button


state="menu"
spil=None
vandt=False

running=True

while running:

    screen.fill(WHITE)

    if state=="menu":

        title=font.render("Dansk Wordle",True,BLACK)
        screen.blit(title,(150,200))

        start_knap=pygame.Rect(170,320,160,70)

        pygame.draw.rect(screen,GREEN,start_knap)

        t=small_font.render("Start spil",True,BLACK)
        screen.blit(t,(205,345))

    elif state=="spil":

        draw_grid(spil)
        draw_timer(spil["start_tid"])
        draw_keyboard(spil)

    elif state=="slut":

        play_button=draw_end_screen(vandt)

    pygame.display.flip()

    for event in pygame.event.get():

        if event.type==pygame.QUIT:
            pygame.quit()
            sys.exit()

        if state=="menu":

            if event.type==pygame.MOUSEBUTTONDOWN:
                if start_knap.collidepoint(event.pos):
                    spil=start_spil()
                    state="spil"

        elif state=="spil":

            if event.type==pygame.KEYDOWN:

                if event.key==pygame.K_BACKSPACE:
                    spil["current_guess"]=spil["current_guess"][:-1]

                elif event.key==pygame.K_RETURN:

                    if len(spil["current_guess"])==5:

                        guess=spil["current_guess"]

                        spil["guesses"].append(guess)
                        spil["feedbacks"].append(check_guess(guess,spil["hemmeligt_ord"]))

                        if guess==spil["hemmeligt_ord"]:

                            stats[len(spil["guesses"])-1]+=1
                            vandt=True
                            state="slut"

                        elif len(spil["guesses"])==6:

                            stats[6]+=1
                            vandt=False
                            state="slut"

                        spil["current_guess"]=""

                else:

                    if (
                        len(spil["current_guess"])<5
                        and event.unicode.lower() in "abcdefghijklmnopqrstuvwxyzæøå"
                    ):
                        spil["current_guess"]+=event.unicode.lower()

            if event.type==pygame.MOUSEBUTTONDOWN:

                pos=event.pos

                for letter,rect in key_rects.items():

                    if rect.collidepoint(pos):

                        if letter=="⌫":
                            spil["current_guess"]=spil["current_guess"][:-1]

                        elif letter=="↵":

                            if len(spil["current_guess"])==5:

                                guess=spil["current_guess"]

                                spil["guesses"].append(guess)

                                spil["feedbacks"].append(
                                    check_guess(guess,spil["hemmeligt_ord"])
                                )

                                if guess==spil["hemmeligt_ord"]:

                                    stats[len(spil["guesses"])-1]+=1
                                    vandt=True
                                    state="slut"

                                elif len(spil["guesses"])==6:

                                    stats[6]+=1
                                    vandt=False
                                    state="slut"

                                spil["current_guess"]=""

                        else:

                            if len(spil["current_guess"])<5:
                                spil["current_guess"]+=letter

        elif state=="slut":

            if event.type==pygame.MOUSEBUTTONDOWN:

                if play_button.collidepoint(event.pos):
                    spil=start_spil()
                    state="spil"