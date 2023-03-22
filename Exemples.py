import numpy as np
import random as rd
import string

def exemple_libre(n):
    """Genere un tableau de correlation de n monnaies a double entrees. A la case [i,j], 
    on trouve si les monnaies i et j sont correlees ou non en fontion de la valeur du booleen"""
    
    tab = np.zeros((n,n))
    
    for i in range(n):
        tab[i,i]=True

        for j in range(i):
            tab[i,j]=tab[j,i]   #La matrice est naturellement symétrique.

        for j in range(i+1,n):
            p = rd.random()

            if p<0.54:     #Probabilité de correlation entre deux monnaies calculee a partir d'un exemple reel.
                tab[i,j]=True
            else :
                tab[i,j]=False

    return np.logical_or(tab,tab)


def generation_pos(tab):
    """Genere aleatoirement les positions des monnaies correlees entre elles"""
    test = True
    n = len(tab)
    arret = 0

    while arret < 1000:
        ind_1 = rd.randint(0,n-1)   #On choisit aleatoirement l'indice de la premiere monnaie

        if len(tab[ind_1])>2:       #On verifie que la monnaie admet des correlations
            ind_2 = tab[ind_1][rd.randint(1,len(tab[ind_1])-1)]  #Si oui, on choisit aleatoirement la deuxieme monnaie
            val = rd.randint(1,10000)
            tab[ind_1][0] += val
            tab[ind_2][0] -= val
            arret += 1              #On n'incremente _arret que si la condition if a ete verifiee

def nomination(n):
    return [str(i) for i in range(n)]


def creer_tab(n):
    """Cree un tableau d'exemple tel que la premiere colonne represente la position de la monnaie i,
    la suite de la ligne i est utillisee pour indiquer les monnaies correlees a i.
    On remplit par des -1 la fin des lignes pour obtenir un tableau."""

    corr = exemple_libre(n)
    tab=[]
    for i in range(n):
        tab.append([0])   #Crée les lignes du tableau

    for i in range(n):
        for j in range(i-1):
            if corr[i][j]:
                tab[i].append(j) 
                tab[j].append(i) 
    
    max_len = 0
    
    for i in range(n):
        if len(tab[i])>max_len:
            max_len = len(tab[i])
    generation_pos(tab)

    for i in range(n):
        while(len(tab[i])<max_len):
            tab[i].append(int(-1))

    return np.array(tab), nomination(n)

print(creer_tab(8))
