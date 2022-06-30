from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from IPython.display import HTML
import numpy as np
import multiprocessing
import random
from queue import Empty

n = 10  # dimenzija matrice
cord_i = [-1, -1, -1, 0, 1, 1, 1, 0]
cord_j = [-1, 0, 1, 1, 1, 0, -1, -1]
steps = 20

servis_queue = multiprocessing.Queue(n * n)  # finish red za belezenje vrednosti trenutne iteracije
matrix_queue = multiprocessing.Queue(steps)  # red za stanja celija
cells_queue = [[multiprocessing.Queue(8) for i in range(n)] for j in range(n)]
iter_queue = multiprocessing.JoinableQueue(n * n)


class Cell():
    def __init__(self, alive, pos_i, pos_j):
        self.alive = alive  # vrednost zivota celije
        self.pos_i = pos_i
        self.pos_j = pos_j


matrix = [[Cell(random.choice([True, False]), j, i) for i in range(n)] for j in range(n)]
state_matrix = []  # niz stanja matrica


def life_game(cell, servis_queue, cells_queue):
    for i in range(steps):
        neighbour_values = []  # vrednosti okolnih celija

        for j in range(8):
            tmp_i = (cell.pos_i + cord_i[j] + n) % n  # ciklus matrica
            tmp_j = (cell.pos_j + cord_j[j] + n) % n

            cells_queue[tmp_i][tmp_j].put(cell.alive)  # salje svoju vrednost susedima u red

        for j in range(8):  # konstantno se cita iz reda
            neighbour_values.append(cells_queue[cell.pos_i][cell.pos_j].get())

        living = len([elem for elem in neighbour_values if elem == True])  # brojac zivih suseda

        if (living < 2):
            cell.alive = False
        elif (living > 3):
            cell.alive = False
        elif ((cell.alive == True) and (living == 2 or living == 3)):
            cell.alive = True
        elif ((cell.alive == False) and living == 3):
            cell.alive = True

        servis_queue.put(cell)
        iter_queue.put(True)
        iter_queue.join()


def servis(servis_queue, matrix_queue):
    mat_tmp = [[True for i in range(n)] for j in range(n)]

    for iter in range(steps):
        for i in range(n * n):
            item = servis_queue.get()
            mat_tmp[item.pos_i][item.pos_j] = item.alive

        matrix_queue.put(mat_tmp)
        for j in range(n * n):
            iter_queue.get()
            iter_queue.task_done()


pa = []
for i in range(n):
    for j in range(n):
        pa.append(multiprocessing.Process(target=life_game, kwargs={'cell': matrix[i][j], 'servis_queue': servis_queue,
                                                                    'cells_queue': cells_queue}))

state_matrix.append([[matrix[i][j].alive for i in range(n)] for j in range(n)])

sp = multiprocessing.Process(target=servis, kwargs={'servis_queue': servis_queue, 'matrix_queue': matrix_queue})

for i in pa:
    i.start()
sp.start()

for i in pa:
    i.join()
sp.join()


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


while True:
    try:
        m = matrix_queue.get(timeout=0.1)  # ukoliko je na red dosla poslednja celija, ona ce izbaciti sve iz reda
        state_matrix.append(m)
    except Empty:
        break

anim = animate(state_matrix);
HTML(anim.to_html5_video())