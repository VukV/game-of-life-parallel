from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from IPython.display import HTML
import numpy as np
import threading
import random

n = 10  # dimenzija matrice
cell_counter = 0  # brojac celija
cord_i = [-1, -1, -1, 0, 1, 1, 1, 0]
cord_j = [-1, 0, 1, 1, 1, 0, -1, -1]

condition = threading.Condition()


class Cell():
    def __init__(self, alive, pos_i, pos_j):
        self.alive = alive  # vrednost zivota celije
        self.semaphore = threading.Semaphore(0)
        self.neighbour = 0  # brojac procitanih komsija
        self.pos_i = pos_i
        self.pos_j = pos_j
        self.mutex = threading.Lock()


matrix = [[Cell(random.choice([True, False]), j, i) for i in range(n)] for j in range(n)]
state_matrix = []  # niz stanja matrica


def life_game(cell, steps=20):
    global cell_counter
    global matrix
    global state_matrix

    for i in range(steps):
        neighbour_values = []  # vrednosti okolnih celija

        for j in range(8):
            tmp_i = (cell.pos_i + cord_i[j] + n) % n  # ciklus matrica
            tmp_j = (cell.pos_j + cord_j[j] + n) % n

            matrix[tmp_i][tmp_j].mutex.acquire()  # mutex, ulazak u kriticnu sekciju

            neighbour_values.append(matrix[tmp_i][tmp_j].alive)  # pamcenje vrednosti niza suseda
            matrix[tmp_i][tmp_j].neighbour += 1  # izmena brojaca suseda

            if (matrix[tmp_i][tmp_j].neighbour == 8):  # ukoliko je brojac suseda dosao do 8 (svi su ga procitali)
                matrix[tmp_i][tmp_j].neighbour = 0  # resetuje se brojac
                matrix[tmp_i][tmp_j].semaphore.release()  # i propusta se semafor suseda

            matrix[tmp_i][tmp_j].mutex.release()  # izlazak iz kriticne sekcije

        living = len([elem for elem in neighbour_values if elem == True])  # brojac zivih suseda

        cell.semaphore.acquire()  # blokira se semafor i menja se vrednost celije
        if (living < 2):
            cell.alive = False
        elif (living > 3):
            cell.alive = False
        elif ((cell.alive == True) and (living == 2 or living == 3)):
            cell.alive = True
        elif ((cell.alive == False) and living == 3):  # (living == 2 or living == 3)?
            cell.alive = True

        condition.acquire()  # nakon promene vrednosti blokira se condition
        cell_counter += 1  # brojac se povecava za promenjenu celiju

        if (cell_counter < n * n):
            condition.wait()  # ukoliko sve celije nisu procitane, sledeca iteracija mora da ceka
        else:
            # u suprotnom se trenutna iteracija dodaje u niz matrica
            state_matrix.append([[matrix[i][j].alive for i in range(n)] for j in range(n)])
            cell_counter = 0  # resetuje se brojac celija
            condition.notifyAll()  # i condition obavestava sve da mogu da nastave dalje

        condition.release()


ta = []
for i in range(n):
    for j in range(n):
        ta.append(threading.Thread(target=life_game, args=(matrix[i][j],)))

state_matrix.append([[matrix[i][j].alive for i in range(n)] for j in range(n)])
for i in ta:
    i.start()

for i in ta:
    i.join()


def animate(steps):
    def init():
        im.set_data(steps[0])
        return [im]

    def animate(i):
        im.set_data(steps[i])
        return [im]

    im = plt.matshow(steps[0], interpolation='None', animated=True);

    anim = FuncAnimation(im.get_figure(), animate, init_func=init, frames=len(steps), interval=500,
                         blit=True, repeat=False);
    return anim


anim = animate(state_matrix);
HTML(anim.to_html5_video())