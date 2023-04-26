from Algos import Greedy, OpLin, Flow

from Exemples import creer_exemple_simple

from timeit import default_timer as timer
import matplotlib.pyplot as plt
import numpy as np

class Rate:
    def __init__(self, X, Y) -> None:
        self.X = X
        self.Y = Y

def rate_alg_aux(Algo, tabs, names):
    average = 0
    for i in range(len(tabs)):
        alg = Algo(tabs[i], names[i])
        duree = alg.optimize()
        average += duree
    average /= len(tabs)
    return average

def rate_alg(Algos, n_start, n_end, n_iter):

    ratings = []

    #creation des tableaux
    print("Creation des tableaux...")
    tabs = [[None for _ in range(n_iter)] for _ in range(n_start, n_end)]
    names = [[None for _ in range(n_iter)] for _ in range(n_start, n_end)]
    for i in range(n_start, n_end):
        for j in range(n_iter):
            tab, names_ = creer_exemple_simple(i)
            tabs[i-n_start][j] = tab
            names[i-n_start][j] = names_
    
    for Algo in Algos:
        print(f"Rating {Algo.name}...")
        Y = []
        for i in range(n_start, n_end):
            Y.append(rate_alg_aux(Algo, tabs[i-n_start], names[i-n_start]))
        ratings.append(Rate(list(range(n_start, n_end)), Y))
    return ratings

            

    

"""if __name__ == "__main__":
    n_start = 10
    n_end = 100
    n_iter = 60

    Algos = [Greedy, OpLin, Flow]
    ratings = rate_alg(Algos, n_start, n_end, n_iter)

    fig, ax = plt.subplots()
    #ax.plot(rate_Greedy.X, rate_Greedy.Y, label="Greedy")
    Y1 = np.log(ratings[0].Y)
    Y2 = np.log(ratings[1].Y)
    Y3 = np.log(ratings[2].Y)

    X1 = np.log(ratings[0].X)
    X2 = np.log(ratings[1].X)
    X3 = np.log(ratings[2].X)
    
    fit1 = np.polyfit(np.log(ratings[0].X), Y1, 1)
    fit2 = np.polyfit(np.log(ratings[1].X), Y2, 1)
    fit3 = np.polyfit(np.log(ratings[2].X), Y3, 1)
    ax.plot(ratings[0].X, Y1, label="Greedy (coeff directeur : {})".format(round(fit1[0], 4)))
    ax.plot(ratings[0].X, fit1[0]*np.log(np.array(ratings[0].X)) + fit1[1], color="red")
    ax.plot(ratings[1].X, Y2, label="OpLin (coeff directeur : {})".format(round(fit2[0], 4)))
    ax.plot(ratings[1].X, fit2[0]*np.log(np.array(ratings[1].X)) + fit2[1], color="red")
    ax.plot(ratings[2].X, Y3, label="Flow (coeff directeur : {})".format(round(fit3[0], 4)))
    ax.plot(ratings[2].X, fit3[0]*np.log(np.array(ratings[2].X)) + fit3[1], color="red")
    ax.legend()
    plt.xlabel("Nombre n de monnaies")
    plt.ylabel("Log du temps moyen de calcul (s)")
    plt.title("Temps de calcul en fonction du nombre de monnaies")
    plt.show()"""

if __name__ == "__main__":
    n_start = 100
    n_end = 300
    n_iter = 10

    Algos = [OpLin, Flow]
    ratings = rate_alg(Algos, n_start, n_end, n_iter)

    fig, ax = plt.subplots()
    #ax.plot(rate_Greedy.X, rate_Greedy.Y, label="Greedy")
    Y1 = np.log(ratings[0].Y)
    Y2 = np.log(ratings[1].Y)
    X1 = np.log(ratings[0].X)
    X2 = np.log(ratings[1].X)
    fit1 = np.polyfit(X1, Y1, 1)
    fit2 = np.polyfit(X1, Y2, 1)
    ax.plot(X1, Y1, label="OpLin (coeff directeur : {})".format(round(fit1[0], 4)))
    ax.plot(X1, fit1[0]*X1 + fit1[1], color="red")
    ax.plot(X2, Y2, label="Flow (coeff directeur : {})".format(round(fit2[0], 4)))
    ax.plot(X2, fit2[0]*X2 + fit2[1], color="red")
    ax.legend()
    plt.xlabel("Nombre n de monnaies")
    plt.ylabel("Log du temps moyen de calcul (s)")
    plt.title("Temps de calcul en fonction du nombre de monnaies")
    plt.show()

    fig, ax = plt.subplots()
    ax.plot(ratings[0].X, ratings[0].Y, label="OpLin")
    ax.plot(ratings[1].X, ratings[1].Y, label="Flow")
    ax.legend()
    plt.xlabel("Nombre n de monnaies")
    plt.ylabel("Temps moyen de calcul (s)")
    plt.title("Temps de calcul en fonction du nombre de monnaies")
    plt.show()