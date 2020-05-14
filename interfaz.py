#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  interfaz.jpeg
#  
#  Copyright 2020 Unknown <raiz@pc-piola>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GooCanvas', '2.0')
from gi.repository import Gtk, GooCanvas
from conexion import Conexion
from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.figure import Figure
from matplotlib import animation

class Sliders(Gtk.Frame):
    def __init__(self, watch_slider):
        super(Sliders, self).__init__(
            label = "Control")
        
        #self.set_size_request(200, 150) #No es necesaria
        
        grid = Gtk.Grid(
                    margin = 4)	
        scales = {}
        for x, (ref, vmin, vmax, step, label, hasbtn) in enumerate((
                    ("p", 0, 5, 0.01, "P", False),
                    ("i", 0, 5, 0.01, "I", False),
                    ("d", 0, 5, 0.01, "D", False),
                    ("v", 0, 255, 1, "Vel", True))):
            scales[ref] = Gtk.Scale.new_with_range(
                            Gtk.Orientation.VERTICAL,
                            vmin,#Min
                            vmax,#Max
                            step)#Paso				
            scales[ref].set_vexpand(True)
            scales[ref].set_inverted(True)
            grid.attach(scales[ref], x, 0, 1, 1)
            grid.attach(Gtk.Label(label = label), x, 1, 1, 1)
            
            if hasbtn:
                btn = Gtk.ToggleButton(label = "No")
                grid.attach(btn, x, 2, 1, 1)    
        watch_slider(scales["v"])
        
        self.add(grid)

class Plot(Gtk.Frame):
    def __init__(self, canvas):
        super(Plot, self).__init__(
            label = "Graph")
        
        scroller = Gtk.ScrolledWindow(
                    hexpand = True)
        scroller.add(canvas)
        
        self.add(scroller)

class MainWindow(Gtk.Window):
	def __init__(self, watch_slider, canvas):
	    super(MainWindow, self).__init__()
	    self.connect("destroy", lambda x: Gtk.main_quit())
	    self.set_size_request(400, 300)
	    
	    grid = Gtk.Grid()
	    self.plot = Plot(canvas)
	    sliders = Sliders(watch_slider)
	    grid.attach(sliders, 0, 0, 1, 1)
	    grid.attach(self.plot, 1, 0, 1, 1)
	    
	    #Meterlo adentro de la ventana
	    self.add(grid)
	    
	    self.show_all()
		
	def run(self):
	    Gtk.main()

class Graphics():	

    def __init__(self, conexion):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.axis = self.fig.add_subplot()
        self.canvas = FigureCanvas(self.fig)
        self.conexion = conexion
        #   Variable that stores the time duration of intervals for animation in miliseconds
        self.time_interval = 50
        #   Variable that stores how many seconds we are showing in animation
        self.time_show = 10

    def create_animation(self):
        self.anim = animation.FuncAnimation(self.fig, self.animate, init_func = self.init,
            interval = self.time_interval)

    def init(self):
        self.velDynamic = []
        self.torqueDynamic = []
        self.time = []
        #   Only show delta time of self.time_show seconds
        for t in range(0, self.time_show * 1000 // self.time_interval):
            self.time.append(t * self.time_interval / 1000)
            self.velDynamic.append(0)   #   Initiate with 0s
            self.torqueDynamic.append(0)    #   Initiate with 0s

    def animate(self, i):
        #   Clear animation axis
        self.axis.clear()
        #   Rewrite axis
        self.axis.set_title("Motor dinámico: Velocidad vs Tiempo")
        self.axis.set_xlabel("Tiempo (delta_t en segundos)")
        self.axis.set_ylabel("Velocidad (0-255)")
        self.axis.set_ylim([-1, 260])    #   Set Y limits between 0 and 255
        #   Get data
        vel, torque = self.conexion.get_scale()
        #   Only keep self.time_show seconds window of data
        #   Overwrite last value
        self.velDynamic.pop(0)
        self.torqueDynamic.pop(0)
        self.velDynamic.append(vel)
        self.torqueDynamic.append(torque)
        self.axis.plot(self.time, self.velDynamic, 'r')
        self.axis.plot(self.time, self.torqueDynamic, 'y')
        #   Set legends here because before plotting doesn't work
        self.axis.legend(['Speed', 'Torque'])

def main(args):
    conexion = Conexion()
    graphics = Graphics(conexion)
    graphics.create_animation()
    canvas = graphics.canvas
    canvas.set_size_request(800, 600)
    mainwdw = MainWindow(conexion.watch_slider, canvas)
    mainwdw.run()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
