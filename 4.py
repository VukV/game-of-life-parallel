from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from IPython.display import HTML
import multiprocessing
import random
import copy

n = 10  # dimenzija matrice
cord_i = [-1, -1, -1, 0, 1, 1, 1, 0]
cord_j = [-1, 0, 1, 1, 1, 0, -1, -1]
steps = 20
N = 5


class Cell():
    def __init__(self, alive, pos_i, pos_j):
        self.alive = alive  # vrednost zivota celije
        self.pos_i = pos_i
        self.pos_j = pos_j

    def __repr__(self):
        return str(self.alive) + " " + str(self.pos_i) + " " + str(self.pos_j)


matrix = [[Cell(random.choice([True, False]), j, i) for i in range(n)] for j in range(n)]  # inicijalno stanje matrice
state_matrix = []  # niz stanja matrica

tmp_mat_arr = []
for i in range(n):
    for j in range(n):
        tmp_mat_arr.append(matrix[i][j].alive)

shared_arr = multiprocessing.Array('b', tmp_mat_arr)  # deljeni niz koji ce celije koristiti da citaju komsije


def life_game(cell):
    neighbour_values = []  # vrednosti okolnih celija

    for j in range(8):
        tmp_i = (cell.pos_i + cord_i[j] + n) % n  # ciklus matrica
        tmp_j = (cell.pos_j + cord_j[j] + n) % n

        neighbour_values.append(shared_arr[tmp_i * n + tmp_j])  # citanje vrednosti komsija iz deljenog niza

    living = len([elem for elem in neighbour_values if elem == True])  # brojac zivih suseda

    if (living < 2):
        cell.alive = False
    elif (living > 3):
        cell.alive = False
    elif ((cell.alive == True) and (living == 2 or living == 3)):
        cell.alive = True
    elif ((cell.alive == False) and living == 3):
        cell.alive = True

    return cell


pool = multiprocessing.Pool(N)

mat_tmp = [[True for i in range(n)] for j in range(n)]  # ptivremena matrica za belezenje trenutne iteracije
state_matrix.append([[matrix[i][j].alive for i in range(n)] for j in range(n)])  # niz matrica za animaciju

cell_arr = []  # niz celija koji se map-u prosledjuje za narednu iteraciju
for i in range(n):
    for j in range(n):
        cell_arr.append(matrix[i][j])

for i in range(steps):

    cell_result = pool.map(life_game, cell_arr, chunksize=N)  # dobije se result

    for cell in cell_result:  # obradjuje se svaka celija iz result-a
        shared_arr[cell.pos_i * n + cell.pos_j] = cell.alive
        # menja se deljeni niz na nova stanja, kako bi u narednoj iteraciji svaka celija opet citala komsije

        cell_arr[cell.pos_i * n + cell.pos_j] = cell
        # ista promena se radi i sa nizom koji se prosledjuje pool-u, kako bi pool radio sa narednom iteracijom

        mat_tmp[cell.pos_i][cell.pos_j] = cell.alive  # pravi se matrica trenutne iteracije

    state_matrix.append(copy.deepcopy(mat_tmp))  # ta matrica se na kraju prosledi nizu matrica (za animaciju)

pool.close()
pool.join()


def animate(steps):
    def init():
        im.set_data(steps[0])
        return [im]

    def animate(i):
        im.set_data(steps[i])
        return [im]

    im = plt.matshow(steps[0], interpolation='None', animated=True);

    anim = FuncAnimation(im.get_figure(), animate, init_func=init,
                         frames=len(steps), interval=500, blit=True, repeat=False);
    return anim


anim = animate(state_matrix);
HTML(anim.to_html5_video())