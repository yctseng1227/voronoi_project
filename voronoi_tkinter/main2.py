# Algorithm project by m083140005
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

        ttk.Button(text="IMPORT", command=self.open_PL_file).pack(side=tk.LEFT)
        ttk.Button(text="LOAD", command=self.open_file).pack(side=tk.LEFT)
        ttk.Button(text="SAVE", command=self.save_file).pack(side=tk.LEFT)
        ttk.Button(text="NEXT", command=self.canvas.next_points).pack(side=tk.LEFT)
        ttk.Button(text="STEP", command=self.canvas.voronoi_sample, state=DISABLED).pack(side=tk.LEFT)
        ttk.Button(text="RUN", command=self.canvas.voronoi_diagram).pack(side=tk.LEFT)
        ttk.Button(text="CLEAR", command=self.canvas.clean_canvas).pack(side=tk.LEFT)

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
