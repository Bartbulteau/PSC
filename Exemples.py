import numpy as np
import random as rd
import string

def exemple_libre(n):
    tab = np.zeros((n,n))
    for i in range(n):
        tab[i,i]=True
        for j in range(i):
            tab[i,j]=tab[j,i]
        for j in range(i+1,n):
            p = rd.random()
            if p<0.54:
                tab[i,j]=True
            else :
                tab[i,j]=False

    return np.logical_or(tab,tab)



def nomination(n):
    return [str(i) for i in range(n)]

def generation_pos(tab):

    test = True
    n = len(tab)
    arret = 0
    while arret < 1000:
        ind_1 = rd.randint(0,n-1)
        if len(tab[ind_1])>2:
            ind_2 = tab[ind_1][rd.randint(2,len(tab[ind_1])-1)]
            val = rd.randint(1,100000)
            tab[ind_1][1] += val
            tab[ind_2][1] -= val
            arret += 1



def creer_tab(n):
    """Cree un tableau d'exemple au format initial, avec les positions set a 0
    et en remplissant la fin des lignes par des str vides"""
    corr = exemple_libre(n)
    index = nomination(n)
    tab=[]
    for i in range(len(index)):
        tab.append([index[i],0])

    for i in range(n):
        for j in range(i-1):
            if corr[i][j]:
                tab[i].append(j) #tab[i].append(index[j])
                tab[j].append(i) #tab[j].append(index[i])
    max_len=0
    for i in range(n):
        if len(tab[i])>max_len:
            max_len = len(tab[i])
    generation_pos(tab)

    for i in range(n):
        while(len(tab[i])<max_len):
            tab[i].append("")

    #exemple = completerListeArray(tab)
    return np.array(tab)

#print(cree_tab(50))

