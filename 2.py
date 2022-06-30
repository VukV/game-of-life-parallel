from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from IPython.display import HTML
import numpy as np
import threading
import random
from queue import Queue, Empty

n = 10  # dimenzija matrice
cord_i = [-1, -1, -1, 0, 1, 1, 1, 0]
cord_j = [-1, 0, 1, 1, 1, 0, -1, -1]

finish = Queue(n * n)  # finish red za belezenje vrednosti trenutne iteracije
counter = Queue(1)  # red za brojac celija trenutne iteracije


class Cell():
    def __init__(self, alive, pos_i, pos_j):
        self.alive = alive  # vrednost zivota celije
        self.queue = Queue(8)  # red kroz koji se salju vrednosti (alive)
        self.pos_i = pos_i
        self.pos_j = pos_j


matrix = [[Cell(random.choice([True, False]), j, i) for i in range(n)] for j in range(n)]
state_matrix = []  # niz stanja matrica


def life_game(cell, steps=20):
    global matrix
    global state_matrix

    for i in range(steps):
        neighbour_values = []  # vrednosti okolnih celija

        for j in range(8):
            tmp_i = (cell.pos_i + cord_i[j] + n) % n  # ciklus matrica
            tmp_j = (cell.pos_j + cord_j[j] + n) % n

            matrix[tmp_i][tmp_j].queue.put(cell.alive)  # salje svoju vrednost susedima u red

        for j in range(8):  # konstantno se cita iz reda
            neighbour_values.append(cell.queue.get())

        living = len([elem for elem in neighbour_values if elem == True])  # brojac zivih suseda

        if (living < 2):
            cell.alive = False
        elif (living > 3):
            cell.alive = False
        elif ((cell.alive == True) and (living == 2 or living == 3)):
            cell.alive = True
        elif ((cell.alive == False) and living == 3):  # (living == 2 or living == 3)?
            cell.alive = True

        cnt = counter.get()  # uzme se counter
        cnt += 1  # poveca se za trenutnu celiju
        if (cnt < n * n):
            finish.put(cell)  # ukoliko to nije poslednja celija, ona se dodaje u red stanja
            counter.put(cnt)  # i counter se dodaje nazad u red
            finish.join()  # zove se join da se trenutna celija zablokira
        else:
            state_matrix.append([[matrix[i][j].alive for i in range(n)] for j in
                                 range(n)])  # upisuje se stanje trenutne iteracije, pa ce se odblokirati sve celije
            while True:
                try:
                    finish.get(timeout=0.1)  # ukoliko je na red dosla poslednja celija, ona ce izbaciti sve iz reda
                    finish.task_done()  # i pozvace task done kako bi se ostale odblokirale
                except Empty:
                    counter.put(0)
                    break


counter.put(0)
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