# $LAN=PYTHON$
# Algorithm project by m083140005 曾煜鈞(Yu-Chun, Tseng)
# Github: https://github.com/yctseng1227/voronoi_project
# Copyright © 2019 yctseng. All rights reserved

import tkinter as tk
import tkinter.messagebox
import pickle
import numpy as np
import random

from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from canvas import *

imgW = 800
imgH = 600

class RootWidget:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("M083140005")
        self.window.geometry("800x650")

        self.canvas = VCanvas(width=800, height=600, bg="white")
        self.canvas.pack()
        # self.label = tk.Label(self.window, font=("Times", 20), fg="red")
        # self.label.pack(side="right")

        ttk.Button(text="import", command=self.open_PL_file).pack(side=tk.LEFT)
        ttk.Button(text="load", command=self.open_file).pack(side=tk.LEFT)
        ttk.Button(text="random", command=self.canvas.random_points).pack(side=tk.LEFT)
        ttk.Button(text="save", command=self.save_file).pack(side=tk.LEFT)
        ttk.Button(text="next case", command=self.canvas.next_points).pack(side=tk.LEFT)
        ttk.Button(text="step by step", command=self.canvas.next_voronoi).pack(side=tk.LEFT)
        ttk.Button(text="run VD", command=self.canvas.voronoi_sample).pack(side=tk.LEFT)
        ttk.Button(text="clear", command=self.canvas.clean_canvas).pack(side=tk.LEFT)
        ttk.Button(text="convex hull", command=self.canvas.voronoi_step).pack(side=tk.RIGHT)
        

    def open_file(self):
        openfilename = fd.askopenfilename(initialdir="./", title="Select file",filetypes=(("text files", "*.txt"), ("all files", "*.*")))
        print(openfilename)

        all_points = []
        reader = open(openfilename, encoding = 'utf8')
        for line in reader:
            if len(line) > 1 and line[0] != "#" and len(line.split()) == 1:
                n = int(line.split()[0])
                if n == 0:
                    break
                points = []
                for _ in range(n):
                    tmp = next(reader)
                    subpoint = tuple(map(int, tmp.split()))
                    points.append(subpoint)
                all_points.append(points)
        self.canvas.set_subset_points(all_points)
        self.canvas.next_points()

    def open_PL_file(self):
        openfilename = fd.askopenfilename(initialdir="./", title="Select file", filetypes=(("text files", "*.txt"), ("all files", "*.*")))
        print(openfilename)

        reader = open(openfilename, encoding = 'utf8')
        for line in reader:
            if(line[0] == 'P'):
                p, x, y = line.split()
                self.canvas.draw_point((float(x), float(y)))
            else:
                p, x1, y1, x2, y2 = line.split()
                self.canvas.draw_edge((float(x1), float(y1)), (float(x2), float(y2)))

    def save_file(self):
        f = fd.asksaveasfile(mode='w', defaultextension=".txt")
        if f is None:
            return
        self.canvas.visible_points = sorted(self.canvas.visible_points , key=lambda k: [k[0], k[1]])
        string = '\n'.join([f'P {x} {y}' for (x, y) in self.canvas.visible_points])
        f.writelines(string+'\n')

        self.canvas.visible_lines = sorted(self.canvas.visible_lines , key=lambda k: [k[0], k[1], k[2], k[3]])
        string = '\n'.join([f'E {x1} {y1} {x2} {y2}' for (x1, y1, x2, y2) in self.canvas.visible_lines])
        f.writelines(string+'\n')
        f.close()



if __name__ == "__main__":
    main = RootWidget()
    tkinter.mainloop()  # run GUI
