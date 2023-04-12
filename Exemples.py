import numpy as np

"""
Script permettant de créer des exemples de tableaux de données de taille arbitraire
pour les tests des algorithmes d'optimisation.
"""

"""
Création d'exemples dans le cas général
"""
def creer_exemple(n):
    # création du tableau de noms (nous utilisons des noms fictifs dans ce genre de format : "0", "1", "2", ...)
    names = []
    for i in range(n):
        names.append(str(i))

    # création du tableau de valeurs (format d'une ligne : [valeur, indice1, indice2, ...] où indice1, indice2, ... sont les indices des noms des positions corrélées à la position i) 
    tab = np.zeros((n, n))

    # creation d'une matrice de correlation
    corr_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i):
            if np.random.rand() < 0.54:
                corr_matrix[i, j] = 1
                corr_matrix[j, i] = 1
    
    # remplissage des correlations dans le tableau
    for i in range(n):
        corr_line = []
        for j in range(n):
            if corr_matrix[i, j] == 1:
                corr_line.append(j)
        corr_line = np.array(corr_line)
        tab[i, 1:] = np.concatenate((corr_line, np.full(n-1-len(corr_line), -1)))
    
    # incrémentation des valeurs des positions
    # on choisit aléatoirement un couple de valeurs corrélées auquel on ajoute/retranche une valeur aléatoire
    for _ in range(1000):                   # Le choix de 1000 est arbitraire et peut être modifié suivant l'ordre de grandeur des valeurs des positions souhaitées
        val = np.random.randint(1, 10000)   # idem pour la borne supérieure de l'intervalle des valeurs
        i = np.random.randint(0, n)
        j = np.random.randint(0, n)
        if corr_matrix[i, j] == 1:
            tab[i, 0] += val
            tab[j, 0] -= val

    tab = tab.astype(int)
    return tab, names

"""
Création d'exemples assurant une solution optimale nulle
"""
def creer_exemple_simple(n):
    # création du tableau de noms (nous utilisons des noms fictifs dans ce genre de format : "0", "1", "2", ...)
    names = []
    for i in range(n):
        names.append(str(i))

    # création du tableau de valeurs (format d'une ligne : [valeur, indice1, indice2, ...] où indice1, indice2, ... sont les indices des noms des positions corrélées à la position i) 
    tab = np.zeros((n, n))

    # creation d'une matrice de correlation
    corr_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i):
            if np.random.rand() < 0.54:
                corr_matrix[i, j] = 1
                corr_matrix[j, i] = 1
    
    # remplissage des correlations dans le tableau
    for i in range(n):
        corr_line = []
        for j in range(n):
            if corr_matrix[i, j] == 1:
                corr_line.append(j)
        corr_line = np.array(corr_line)
        tab[i, 1:] = np.concatenate((corr_line, np.full(n-1-len(corr_line), -1)))

    # choix du nombre de positions longues
    nb_long = np.random.randint(1, n-1)
    pos_long = np.random.choice(n, nb_long, replace=False)              # on choisit aléatoirement les positions longues (replace=False permet d'éviter les doublons)
    pos_court = np.array([i for i in range(n) if i not in pos_long])    # les autres sont des positions courtes
        
    # incrémentation des valeurs des positions
    # on choisit aléatoirement un couple de valeurs corrélées auquel on ajoute/retranche une valeur aléatoire suivant le type de position
    for _ in range(1000):                   # Le choix de 1000 est arbitraire et peut être modifié suivant l'ordre de grandeur des valeurs des positions souhaitées
        val = np.random.randint(1, 10000)   # idem pour la borne supérieure de l'intervalle des valeurs
        i = np.random.choice(pos_long)
        j = np.random.choice(pos_court)
        if corr_matrix[i, j] == 1:
            tab[i, 0] += val
            tab[j, 0] -= val

    tab = tab.astype(int)
    return tab, names