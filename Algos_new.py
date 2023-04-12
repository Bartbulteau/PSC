# manipulation de données
import pandas as pd
import numpy as np

# generateur d'exemples
from Exemples2 import creer_exemple, creer_exemple_simple

# algorithmes d'optimisation
from scipy.optimize import linprog
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_flow

# gestion des fichiers excel
import xlsxwriter
import copy

"""
Classe de base servant de squelette aux algorithmes d'optimisation
     - Le constructeur gère la mise en forme des données commune aux algorithmes
     - La méthode write_to_excel permet d'écrire les résultats dans un fichier Excel
"""
class Algo:
    name = ""
    def __init__(self, tab, names):
        self.pos_long = {}
        self.pos_court = {}
        self.correlations = {}
        self.solution = {}
        self.values = np.zeros(len(names))
        self.RWA = -1
        self.initialsum = 0

        self.names = names

        for i in range(len(tab)):
            if tab[i][0] >= 0:
                self.pos_long[names[i]] = tab[i][0]
                self.values[i] = tab[i][0]
            else:
                self.pos_court[names[i]] = -tab[i][0]
                self.values[i] = -tab[i][0]
            self.correlations[names[i]] = []
            j = 1
            while  j < len(tab[i]) and tab[i][j] != -1:
                self.correlations[names[i]].append(names[tab[i][j]])
                j += 1
        self.initialsum = np.sum(self.values)/2

    def write_to_excel(self, filename):
        """
        fonction qui présente la solution dans un fichier excel sous forme d'un tableau à double entrée
        """
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()

        # definitions des styles ustilisés pour la mise en forme du tableau
        # les cases vertes
        formatvert = workbook.add_format()
        formatvert.set_fg_color('green')
        formatvert.set_bold()
        formatvert.set_font_color('white')
        # les cases grises
        formatgris = workbook.add_format()
        formatgris.set_fg_color('gray')
        
        # mise en forme initiale (nom des lignes et colonnes)
        # pour les positions longues
        worksheet.write(1, 3, "AVANT")
        worksheet.write(2, 3, "APRES")
        # pour les positions courtes
        worksheet.write(3, 1, "AVANT")
        worksheet.write(3, 2, "APRES")

        worksheet.write(3, 3, "RWA")

        # ecrire les noms des monnaies, de leur montant initial, leur montant final et leur apport au RWA
        names_long = list(self.pos_long.keys())
        names_court = list(self.pos_court.keys())
        i = 0
        for name_long in names_long:
            worksheet.write(4+i, 0, name_long, formatvert)                          # NOM
            worksheet.write(4+i, 1, self.pos_long[name_long])                       # AVANT
            worksheet.write(4+i, 2, self.values[self.names.index(name_long)])       # APRES
            worksheet.write(4+i, 3, self.values[self.names.index(name_long)]/2)     # RWA
            i += 1

        worksheet.write(4+i+1, 0, "TOTAL", formatvert)                              # TOTAUX
        worksheet.write(4+i+1, 1, np.sum(list(self.pos_long.values())))             # AVANT
        apres_long = np.sum([self.values[self.names.index(name_long)] for name_long in names_long])
        worksheet.write(4+i+1, 2, apres_long)                                       # APRES
        worksheet.write(4+i+1, 3, apres_long/2)                                     # RWA

        i = 0
        for name_court in names_court:
            worksheet.write(0, 4+i, name_court, formatvert)                         # NOM
            worksheet.write(1, 4+i, self.pos_court[name_court])                     # AVANT
            worksheet.write(2, 4+i, self.values[self.names.index(name_court)])      # APRES
            worksheet.write(3, 4+i, self.values[self.names.index(name_court)]/2)    # RWA
            i += 1

        worksheet.write(0, 4+i+1, "TOTAL", formatvert)                              # TOTAUX
        worksheet.write(1, 4+i+1, np.sum(list(self.pos_court.values())))            # AVANT
        apres_court = np.sum([self.values[self.names.index(name_court)] for name_court in names_court])
        worksheet.write(2, 4+i+1, apres_court)                                      # APRES
        worksheet.write(3, 4+i+1, apres_court/2)                                    # RWA

        # ajout des montants des compensations enregistrés dans self.solution
        for i in range(len(names_long)):
            for j in range(len(names_court)):
                if (names_long[i], names_court[j]) in self.solution.keys():
                    worksheet.write(4+i, 4+j, self.solution[(names_long[i], names_court[j])])
                else:
                    worksheet.write(4+i, 4+j, '', formatgris)

        # comment ajouter une bordure ?

        # fermer le fichier
        workbook.close()


"""
Algorithme implémentant l'optimisation par programmation linéaire
"""
class OpLin(Algo):
    def __init__(self, tab, names):
        super().__init__(tab, names)
        self.name = "OpLin"
    
    def optimize(self):
        # détermination des bonnes dimensions pour les contraintes
        nb_contraintes = len(self.names)
        nb_variables = 0
        edges = []
        for name_long in self.pos_long.keys():
            for name_court in self.pos_court.keys():
                if name_court in self.correlations[name_long]:
                    edges.append((name_long, name_court))
                    nb_variables += 1
        
        # construction de la matrice intervenant les inégalités de contrainte Ax <= b avec b = valeurs de départ
        A = np.zeros((nb_contraintes, nb_variables))
        i = 0
        for e in edges:
            A[self.names.index(e[0])][i] = 1
            A[self.names.index(e[1])][i] = 1
            i += 1
        # contsruction du vecteur intervenant dans la fonction objectif (c)
        c = np.full(nb_variables, -1)

        # résolution du problème
        self.result = linprog(c=c, A_ub=A, b_ub=self.values)

        # mise à jour des positions
        i = 0
        for e in edges:
            self.solution[e] = self.result.x[i]
            self.values[self.names.index(e[0])] -= self.result.x[i]
            self.values[self.names.index(e[1])] -= self.result.x[i]
            i += 1

        # calcul du RWA
        self.RWA = np.sum(self.values)/2

"""
Algrithme implémentant l'optimisation par flot maximal
"""
class Flow(Algo):
    def __init__(self, tab, names):
        super().__init__(tab, names)
        self.name = "Flow"
    
    def optimize(self):
        # ajout de la source et du puits
        self.names.append("source")
        self.names.append("puits")

        # construction des arrêtes du graphe
        edges = []
        for name_long in self.pos_long.keys():
            for name_court in self.pos_court.keys():
                if name_court in self.correlations[name_long]:
                    edges.append((name_long, name_court))
        for name_long in self.pos_long.keys():
            edges.append(("source", name_long))
        
        for name_court in self.pos_court.keys():
            edges.append((name_court, "puits"))

        # construction de la matrice d'adjacence
        matrix = np.zeros((len(self.names), len(self.names)))
        for e in edges:
            i = self.names.index(e[0])
            j = self.names.index(e[1])
            val = 0
            if e[0] == "source":
                val = self.pos_long[e[1]]
            elif e[1] == "puits":
                val = self.pos_court[e[0]]
            else:
                val = self.pos_long[e[0]]
            
            matrix[i][j] = abs(val)

        # résolution du problème
    
        source_index = len(self.names) - 2
        puits_index = len(self.names) - 1

        self.result = maximum_flow(csr_matrix(matrix.astype(int)), source_index, puits_index)
        flow_array = self.result.flow.toarray()

        for name_long in self.pos_long.keys():
            for name_court in self.pos_court.keys():
                if name_court in self.correlations[name_long]:
                    i = self.names.index(name_long)
                    j = self.names.index(name_court)
                    self.solution[(name_long, name_court)] = flow_array[i][j]
                    self.values[self.names.index(name_long)] -= flow_array[i][j]
                    self.values[self.names.index(name_court)] -= flow_array[i][j]

        #print(self.solution)

class Greedy(Algo):
    def __init__(self, tab, names):
        super().__init__(tab, names)
        self.name = "Greedy"
    
    # realise la compensation et supprime les monnaies de valeur nulle
    def compAndUpdate(self, monnaies):
        val = self.pos_long[monnaies[0]] - self.pos_court[monnaies[1]]
        if val > 0:
            self.pos_long[monnaies[0]] = val
            del self.pos_court[monnaies[1]]
            del self.correlations[monnaies[1]]
        elif val < 0:
            self.pos_court[monnaies[1]] = -val
            del self.pos_long[monnaies[0]]
            del self.correlations[monnaies[0]]
        else:
            del self.pos_long[monnaies[0]]
            del self.correlations[monnaies[0]]
            del self.pos_court[monnaies[1]]
            del self.correlations[monnaies[1]]
        return val
    
    # verifie s'il reste des monnaies compensables (de montants non nuls et correlees a des monnaies de montant non nul)
    def shouldContinue(self):
        for c in self.pos_court:
            if len(set(self.correlations[c]) and set(self.correlations.keys()) and set(self.pos_long.keys())) != 0:
                return True
        for l in self.pos_long:
            if len(set(self.correlations[l]) and set(self.correlations.keys()) and set(self.pos_court.keys())) != 0:
                return True
        return False

    def f(self, couple):
        return -(len(self.correlations[couple[0]]) + len(self.correlations[couple[1]]))

    # coeur de l'algo : trouve le couple qui maximise la règle de décision f, effectue la compensation et recommence jusqu'a ce qu'il ne reste plus de  couples valides
    def optimize(self):
        while(self.shouldContinue()):
            best=()
            for c in self.pos_court:
                for l in self.pos_long:
                    if l in self.correlations[c]:
                        best = (l, c)
                        break
            for c in self.pos_court:
                for l in self.pos_long:
                    if c in self.correlations[l]:
                        if self.f((l, c)) > self.f(best):
                            best = (l, c)
            if best == ():
                break
            else :
                val = self.compAndUpdate(best)
                self.solution[best] = val

        i = 0
        for couple in self.solution.keys():
            i += self.solution[couple]
        print(i)



def main():
    tab, names = creer_exemple_simple(30)
    algo = Flow(tab, names)
    algo.optimize()
    algo.write_to_excel("flow.xlsx")
    algo2 = OpLin(tab, names)
    algo2.optimize()
    algo2.write_to_excel("oplin.xlsx")
    #print(algo.solution)


if __name__ == "__main__":
    main()