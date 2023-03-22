# imports generaux
import numpy as np
# imports OpLin
from scipy.optimize import linprog
import networkx as nx
# imports Flow
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_flow
# import Excel
import xlsxwriter

# classe mere qui modelise un algorithme
class Algo:
    name = ""
    def __init__(self, tab, names):
        self.pos_long = {} # dictionnaire de type {"nom": montant} pour les positions longues
        self.pos_court = {} # dictionnaire de type {"nom": montant} pour les positions courtes
        self.correlations = {} # dictionnaire de type {"nom": [liste des noms des monnaies corrélées]}
        self.names = names

        #on récupère les données
        for i in range(len(tab)):
            if tab[i][0] > 0:
                self.pos_long[self.names[i]] = tab[i][0]
            else:
                self.pos_long[self.names[i]] = -tab[i][0]
            corr = []
            for ind in tab[i][1:]:
                if ind != -1:
                    corr.append(self.names[ind])
            self.correlations[self.names[i]] = corr

    def optimize(self):
        pass # code specifique a chaque algo

    def run(self, showResult=True):
        if showResult:
            print("RWA avant compensation :", np.sum(self.values)/2)
        self.optimize()
        if showResult:
            print("Total des compensation :", self.result.total_compensations)
            print("RWA après compensation :", np.sum(self.values)/2)

    def write_to_excel(self, name):
        pass # à coder


#Algorithme Glouton
class Greedy(Algo):
    name = "Greedy"
    def __init__(self, tab): #on initialise les variables manipulées par l'algo
        Algo.__init__(self, tab)

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

class OpLin(Algo):
    name = "OpLin"
    def __init__(self, tab):
        Algo.__init__(self, tab)
        
        # création du graphe représentant le problème
        G = nx.DiGraph()
        G.add_nodes_from(self.pos_long.keys(), bipartite=0)
        G.add_nodes_from(self.pos_court.keys(), bipartite=1)
        edges = []
        for name_long in self.pos_long.keys():
            for name_court in self.pos_court.keys():
                if name_court in self.correlations[name_long]:
                    edges.append((name_long, name_court))
        G.add_edges_from(edges)

        self.G = G

    def optimize(self):
        if self.G.number_of_edges() == 0: #rien à faire dans le cas trivial
            return None
        
        #initialisation de la matrice des contraintes
        A = np.zeros(shape=(len(self.pos_long)+len(self.pos_court), self.G.number_of_edges()))
        c = [-1 for e in self.G.edges]
        i = 0
        
        for e in self.G.edges:
            k = self.names.index(e[0])
            l = self.names.index(e[1])
            A[k][i] = 1
            A[l][i] = 1
            i += 1
        
        # algorithme de programmation linéaire qui effectue la résolution du système
        self.result = linprog(c=c, A_ub=A, b_ub=self.values)
        
        #mise à jour des positions
        i = 0
        for e in self.G.edges:
            #print(e, self.result.x[i])
            self.solution[e] = self.result.x[i]
            self.pos_long[e[0]] -= self.result.x[i]
            self.pos_court[e[1]] -= self.result.x[i]
            k = self.names.index(e[0])
            l = self.names.index(e[1])
            self.values[k] -= self.result.x[i]
            self.values[l] -= self.result.x[i]
            i += 1

class Flow(Algo):
    name = "Flow"
    def __init__(self, tab):
        Algo.__init__(self, tab)

        #ajout de la source et du puits
        self.names.append("source")
        self.names.append("puits")

        # création du graphe représentant le problème
        G = nx.DiGraph()
        G.add_nodes_from(self.pos_long.keys(), bipartite=0)
        G.add_nodes_from(self.pos_court.keys(), bipartite=1)
        edges = []
        for name_long in self.pos_long.keys():
            for name_court in self.pos_court.keys():
                if name_court in self.correlations[name_long]:
                    edges.append((name_long, name_court))

        #ajout de la source et du puits
        for name_long in self.pos_long.keys():
            edges.append(("source", name_long))

        for name_court in self.pos_court.keys():
            edges.append((name_court, "puits"))

        G.add_edges_from(edges)

        self.G = G

    def optimize(self):
        if self.G.number_of_edges() == 0: #rien à faire dans le cas trivial
            return None

        matrix = [[0 for _ in range(len(self.names))] for _ in range(len(self.names))]

        for e in self.G.edges:
            i = self.names.index(e[0])
            j = self.names.index(e[1])
            val = 0
            if(e[0] == "source"):
                val = self.pos_long[e[1]]
            elif(e[1] == "puits"):
                val = self.pos_court[e[0]]
            else:
                val = self.pos_long[e[0]]

            matrix[i][j] = val
        
        source_index = self.names.index("source")
        puits_index = self.names.index("puits")

        self.result = maximum_flow(csr_matrix(matrix), source_index, puits_index)

        arr = self.result.flow.toarray()
        for e in self.G.edges:
            if e[0] != "source" and e[1] != "puits":
                self.solution[e] = arr[self.names.index(e[0])][self.names.index(e[1])]
        
        #mise à jour des positions
        """
        i = 0
        for e in self.G.edges:
            print(e, self.result.x[i])
            self.pos_long[e[0]] -= self.result.x[i]
            self.pos_court[e[1]] -= self.result.x[i]
            k = self.names.index(e[0])
            l = self.names.index(e[1])
            self.values[k] -= self.result.x[i]
            self.values[l] -= self.result.x[i]
            i += 1
        """