import pygame
from pygame.locals import *
from math import sqrt
from copy import deepcopy
from collections import deque

masse = 100
LARGEUR = 980
HAUTEUR = 600
K = 0.00003
magie = 0.01
v = (0.1, -0.1)


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
        self.normec = x**2 + y**2
        
    def __add__(self, autre):
        return Vecteur(self.x + autre.x, self.y + autre.y)
    
    def __rmul__(self, scalaire:float):
        return Vecteur(scalaire * self.x, scalaire * self.y)

def vectorize(pointA:Point, pointB:Point):
    return Vecteur(pointB.x-pointA.x, pointB.y-pointA.y)
    
pygame.init()
fenetre = pygame.display.set_mode((LARGEUR,HAUTEUR), RESIZABLE)

CENTRE = Point(LARGEUR/2, HAUTEUR/2)
HAUT = Point(LARGEUR/2, 10)
BAS = Point(LARGEUR/2, HAUTEUR - 10)
DROITE = Point(LARGEUR - 10, HAUTEUR/2)
GAUCHE = Point(10, HAUTEUR/2)

x0, y0 = LARGEUR/2+60,HAUTEUR/2+80

l_0 = vectorize(GAUCHE,CENTRE).norme - 100

def E_p(a,b):
    k=K
    L=HAUTEUR
    l=LARGEUR
    x = a-l/2
    y=b-L/2
    return -k*(l_0*(
        sqrt(x**2+(y-L/2)**2)+
        sqrt(x**2+(y+L/2)**2)+
        sqrt((x-l/2)**2+y**2)+
        sqrt((x+l/2)**2+y**2))
        -2*(x**2)
        -2*(y**2)
        -l_0*(l+L))


E_m = E_p(x0,y0) + 1/2*masse*(v[0]**2+v[1]**2)

def vit(x,y):
    return sqrt(2/masse * max(E_m-E_p(x,y), 0))

# Définition des objets


class PM(Point):
    def __init__(self, x, y, v0):
        super().__init__(x, y)
        self.color = (200,100,0)
        self.vitesse = Vecteur(*v0)
        self.acceleration = Vecteur(0,0)
        self.forces = []
        self.m = 100

    def update(self, fenetre):
        if (E_p(self.x+dt*self.vitesse.x,self.y+dt*self.vitesse.y)>E_m):
            self.vitesse.x=0
            self.vitesse.y=0
        self.x += dt * self.vitesse.x
        self.y += dt * self.vitesse.y
        self.acceleration = Vecteur(0,0)
        for force in self.forces:
            self.acceleration += (1/self.m)*force
        # self.acceleration += -0.00001*self.vitesse # frottements
        self.vitesse += dt*self.acceleration
        Vth = vit(self.x, self.y)
        norme = self.vitesse.normec
        self.vitesse.x *= sqrt(Vth**2/norme)
        self.vitesse.y *= sqrt(Vth**2/norme)
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


# Paramétrage

M_init = PM(x0,y0,v)
# M_init = PM(LARGEUR/2,HAUTEUR/2,(0.02,0.01))
M = deepcopy(M_init)
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

