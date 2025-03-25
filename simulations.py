import pygame
from pygame.locals import *
from math import sqrt
from copy import deepcopy
from collections import deque

# Définition des objets
class Point:
    def __init__(self, x:float, y:float):
        self.x = x
        self.y = y
        self.color = (0,0,0)

    def update(self, fenetre):
        pygame.draw.circle(fenetre, self.color, (self.x, self.y), 7)


class Vecteur:
    def __init__(self, x:float, y:float):
        self.x = x
        self.y = y
        self.norme = sqrt(x**2 + y**2)
        
    def __add__(self, autre):
        return Vecteur(self.x + autre.x, self.y + autre.y)
    
    def __rmul__(self, scalaire:float):
        return Vecteur(scalaire * self.x, scalaire * self.y)

class PM(Point):
    def __init__(self, x, y, v0):
        super().__init__(x, y)
        self.color = (200,100,0)
        self.vitesse = Vecteur(*v0)
        self.acceleration = Vecteur(0,0)
        self.forces = []
        self.m = 100

    def update(self, fenetre):
        self.x += dt * self.vitesse.x
        self.y += dt * self.vitesse.y
        self.acceleration = Vecteur(0,0)
        for force in self.forces:
            self.acceleration += (1/self.m)*force
        # self.acceleration += -0.00001*self.vitesse # frottements
        self.vitesse += dt*self.acceleration
        if self.x < -LARGEUR or self.x > 2*LARGEUR or self.y < -HAUTEUR or self.y > 2 * HAUTEUR:
            del self
        pygame.draw.circle(fenetre, self.color, (self.x, self.y), 10)
        self.n = 50
        pygame.draw.line(fenetre, (200,10,10), (self.x, self.y), (self.x + self.n*self.vitesse.x, self.y + self.n*self.vitesse.y), 3)
        pygame.draw.line(fenetre, (10,200,10), (self.x, self.y), (self.x + 5*self.n*self.acceleration.x, self.y + 5*self.acceleration.y), 3)

class Ressort:
    def __init__(self, k:float, l0:float, accroche:Point, point:PM):
        self.k = k 
        self.l0 = l0
        self.accroche = accroche
        self.point = point
        self.l = vectorize(point, accroche).norme

    def force(self):
        v = vectorize(self.accroche, self.point)
        return -self.k*(self.l-self.l0)*(1/v.norme)*v
    
    def update_l(self):
        self.l = vectorize(self.point, self.accroche).norme

    def update(self, fenetre):
        pygame.draw.line(fenetre, (200,200,200), (self.accroche.x, self.accroche.y), (self.point.x, self.point.y))

def vectorize(pointA:Point, pointB:Point):
    return Vecteur(pointB.x-pointA.x, pointB.y-pointA.y)

# Paramétrage
pygame.init()
LARGEUR = 640
HAUTEUR = 480
fenetre = pygame.display.set_mode((LARGEUR,HAUTEUR), RESIZABLE)

CENTRE = Point(LARGEUR/2, HAUTEUR/2)
HAUT = Point(LARGEUR/2, 10)
BAS = Point(LARGEUR/2, HAUTEUR - 10)
DROITE = Point(LARGEUR - 10, HAUTEUR/2)
GAUCHE = Point(10, HAUTEUR/2)

# SETUP 1
"""
M = PM(LARGEUR/2+100,HAUTEUR/2+100,(0,-0.01))
R1 = Ressort(0.0006,vectorize(CENTRE,M).norme + 20,CENTRE,M)
"""

# SETUP 2
M_init = PM(LARGEUR/2+30,HAUTEUR/2+80,(0,0))
M = deepcopy(M_init)
K = 0.00004
R1 = Ressort(K,vectorize(HAUT,CENTRE).norme - 100,HAUT,M)
R2 = Ressort(K,vectorize(BAS,CENTRE).norme - 100,BAS,M)
R3 = Ressort(K,vectorize(DROITE,CENTRE).norme - 100,DROITE,M)
R4 = Ressort(K,vectorize(GAUCHE,CENTRE).norme - 100,GAUCHE,M)


points = [HAUT, BAS, DROITE, GAUCHE]
ressorts = [R1, R2, R3, R4]
trajectoire = deque([], maxlen=5000)

clock = pygame.time.Clock()
dt = pygame.time.get_ticks()

def update_all():
    for i, p in enumerate(trajectoire):
        pygame.draw.circle(fenetre, (int((255-10)*(len(trajectoire)-i)/len(trajectoire)+10),int((255-30)*(len(trajectoire)-i)/len(trajectoire)+30),int((255-130)*(len(trajectoire)-i)/len(trajectoire)+130)), p, 1)
    for ressort in ressorts:
        ressort.update_l()
        ressort.update(fenetre)
    M.forces = []
    for ressort in ressorts:
        M.forces.append(ressort.force())
    M.update(fenetre)
    trajectoire.append((M.x,M.y))
    for point in points:
        point.update(fenetre)


# Boucle principale
while True:
    fenetre.fill((255,255,255))
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.display.quit()
            pygame.quit()
            exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.display.quit()
                pygame.quit() 
                exit()
            elif event.key == K_r:
                pass
    update_all()
    pygame.display.flip()
    dt = clock.tick(120)

