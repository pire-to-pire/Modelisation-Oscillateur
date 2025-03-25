from math import sqrt
import numpy as np
import matplotlib.pyplot as plt

k = 0.05
l_0 = 5
l = 10
L = 10

n = 64

def E_p(x,y):
    return k*(l_0*(
        sqrt(x**2+(y-L/2)**2)+
        sqrt(x**2+(y+L/2)**2)+
        sqrt((x-l/2)**2+y**2)+
        sqrt((x+l/2)**2+y**2))
        -2*(x**2)
        -2*(y**2)
        -l_0*(l+L))


X = np.linspace(-l/2., l/2, n) 
Y = np.linspace(-L/2, L/2, n) 

# Champ d'énergie potentielle
Z = np.array([[E_p(x,y) for x in X] for y in Y])
fig, ax = plt.subplots()
pc = ax.pcolormesh(X, Y, Z)
plt.colorbar(pc)
plt.pcolormesh(X, Y, Z) 
plt.show()

# Champ de forces 
F = np.gradient(Z)
gradx,grady=np.gradient(Z)
gradxnorm=gradx/np.sqrt(gradx**2+grady**2)
gradynorm=grady/np.sqrt(gradx**2+grady**2)
gradmag=np.sqrt(gradx**2+grady**2)
step=5

plt.pcolor(X, Y, gradmag,cmap='rainbow')
plt.colorbar()

plt.quiver(X[::step], Y[::step],gradxnorm[::step,::step] , gradynorm[::step,::step],units='xy')
plt.show()