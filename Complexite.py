from Algos import Greedy, OpLin, Flow

from Exemples import creer_tab

from timeit import default_timer as timer
import matplotlib.pyplot as plt

class Rate:
    def __init__(self, X, Y) -> None:
        self.X = X
        self.Y = Y

def rate_alg_aux(Algo, tabs):
    average = 0
    for tab in tabs:
        alg = Algo(tab)
        t0 = timer()
        alg.run(showResult=False)
        t1 = timer()
        average += (t1-t0)
    average /= len(tabs)
    return average

def rate_alg(Algos, n_start, n_end, n_iter):

    ratings = []

    #creation des tableaux
    print("Creation des tableaux...")
    tabs = [[None for _ in range(n_iter)] for _ in range(n_start, n_end)]
    for i in range(n_start, n_end):
        for j in range(n_iter):
            tab = creer_tab(i)
            tabs[i-n_start][j] = tab
    
    for Algo in Algos:
        print(f"Rating {Algo.name}...")
        Y = []
        for i in range(n_start, n_end):
            Y.append(rate_alg_aux(Algo, tabs[i-n_start]))
        ratings.append(Rate(list(range(n_start, n_end)), Y))
    return ratings

            

    

if __name__ == "__main__":
    n_start = 10
    n_end = 50
    n_iter = 10

    Algos = [Greedy, OpLin, Flow]
    ratings = rate_alg(Algos, n_start, n_end, n_iter)

    fig, ax = plt.subplots()
    #ax.plot(rate_Greedy.X, rate_Greedy.Y, label="Greedy")
    ax.plot(ratings[0].X, ratings[0].Y, label="Greedy")
    ax.plot(ratings[1].X, ratings[1].Y, label="OpLin")
    ax.plot(ratings[2].X, ratings[2].Y, label="Flow")
    ax.legend()
    plt.xlabel("Nombre n de monnaies")
    plt.ylabel("Temps moyen de calcul (s)")
    plt.show()

