
import time

import sys
if sys.version_info < (3,):
    import Tkinter as tk
else:
    import tkinter as tk

def mandel(c):
    '''determines if a point is in the Mandelbrot set based on deciding if,
       after 20 iterations, the absolute value of the resulting number is
       greater or equal to 2.'''
    z = 0
    for iter in range(0, 100):
        z = z**2 + c
        if abs(z) >= 2:
            return False
    return abs(z) < 2

class Viewer(object):
    def __init__(self, parent, width=500, height=500):
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

    def draw_fractal(self):
        '''draws a fractal picture'''
        begin = time.time()
        print("Inside draw_fractal.")
        for x in range(0, self.width):
            real = (x - self.shift_x)*self.scale
            for y in range(0, self.height):
                imag = (y - self.shift_y)*self.scale
                c = complex(real, imag)
                if mandel(c):
                    self.draw_pixel(x, (self.height - y))
        print("Time taken for calculating and drawing = %s" %
                                                (time.time() - begin))

if __name__ == "__main__":
    print("Starting...")
    root = tk.Tk()
    app = Viewer(root)
    root.mainloop()
