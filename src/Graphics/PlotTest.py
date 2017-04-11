from Graphics.Plot import Plot
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys
import time
from Utility import Vector2D
import tkinter as tk

class Viewer(object):
    def __init__(self, parent, width=100, height=100):
        self.canvas = tk.Canvas(parent, width=width, height=height)
        self.width = width
        self.height = height

        # the following "shift" variables are used to center the drawing
        self.shift_x = 0.5*self.width
        self.shift_y = 0.5*self.height
        self.scale = 0.01

        self.canvas.pack()

    def draw_pixel(self, x, y):
        '''Simulates drawing a given pixel in black by drawing a black line
           of length equal to one pixel.'''
        self.canvas.create_line(x, y, x+1, y, fill="black")


root = tk.Tk()
app = Viewer(root)
x = np.arange(1,10,0.0001)
y = 1/x
canvas = Vector2D(100,100)
p = Plot(canvas)
# for i in y:
# 	p.appendYValue(i)
# for j in range(0,4):
for i in range(0,2000):
	p.appendYValue(i*2)
print("done with in range")
# for i in range(0,30):
# 	p.appendYValue(30-i)

for i in range(0,p.canvas.shape[0]):
	for j in range(0,p.canvas.shape[1]):
		if p.canvas[i,j] == 1:
			app.draw_pixel(i,j)
root.mainloop()