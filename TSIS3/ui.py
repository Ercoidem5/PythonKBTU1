import pygame

WHITE=(255,255,255)
GRAY=(70,70,70)
BLACK=(20,20,20)
RED=(255,0,0)

class Button:
    def __init__(self,text,x,y,w,h):
        self.text=text
        self.rect=pygame.Rect(x,y,w,h)
    def draw(self,screen,font):
        pygame.draw.rect(screen,GRAY,self.rect)
        pygame.draw.rect(screen,WHITE,self.rect,2)
        img=font.render(self.text,True,WHITE)
        screen.blit(img,img.get_rect(center=self.rect.center))
    def clicked(self,pos):
        return self.rect.collidepoint(pos)


def draw_menu(screen,font,big):
    buttons=[
        Button('Play',120,180,160,50),
        Button('Leaderboard',120,250,160,50),
        Button('Settings',120,320,160,50),
        Button('Quit',120,390,160,50)
    ]
    screen.fill(BLACK)
    screen.blit(big.render('RACER',1,WHITE),(130,90))
    for b in buttons:
        b.draw(screen,font)
    return buttons


def draw_settings(screen,font,big,sound,color,difficulty,username):
    buttons=[
        Button('Sound: ON' if sound else 'Sound: OFF',100,150,200,50),
        Button('Car Color',100,210,200,50),
        Button('Difficulty: '+difficulty,100,270,200,50),
        Button('Name: '+username,100,330,200,50),
        Button('Back',100,400,200,50)
    ]
    screen.fill(BLACK)
    screen.blit(big.render('SETTINGS',1,WHITE),(105,70))
    pygame.draw.rect(screen,color,(170,120,60,20))
    for b in buttons:
        b.draw(screen,font)
    return buttons


def draw_game_over(screen,font,big,score,distance,coins):
    buttons=[
        Button('Retry',120,340,160,50),
        Button('Main Menu',120,410,160,50)
    ]
    screen.fill(BLACK)
    screen.blit(big.render('GAME OVER',1,RED),(70,120))
    screen.blit(font.render(f'Score: {score}',1,WHITE),(130,210))
    screen.blit(font.render(f'Distance: {distance}',1,WHITE),(110,250))
    screen.blit(font.render(f'Coins: {coins}',1,WHITE),(135,290))
    for b in buttons:
        b.draw(screen,font)
    return buttons

def draw_leaderboard(screen,font,big,scores):
    back=Button('Back',120,520,160,45)
    screen.fill(BLACK)
    screen.blit(big.render('TOP 10',1,WHITE),(120,20))
    y=80
    for i,s in enumerate(scores,1):
        name=s.get('name','Unknown')
        score=s.get('score',0)
        dist=s.get('distance',0)
        txt=f"{i}. {name}  {score}  {dist}"
        screen.blit(font.render(txt,1,WHITE),(30,y))
        y+=40
    back.draw(screen,font)
    return back
