from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import random
import pandas as pd
import numpy as np
import matplotlib.animation as animation
import itertools
 


def createAnimatedGraph(data, x_header, y_header):
    #filename = 'Data\\kseExperiment\\2024-06-27-10_36_36.368552_processed.csv'
    #data = pd.read_csv(filename)

    def data_gen():
        for cnt in itertools.count():
            t = float(data[x_header][cnt]) #cnt / 10
            #y = np.sin(2*np.pi*t) * np.exp(-t/10.) 
            y = float(data[y_header][cnt])
            yield t, y
    
    def init():
        ax.set_ylim(1.3524100e7, 1.3526000e7)
        ax.set_xlim(0, 10)
        del xdata[:]
        del ydata[:]
        line.set_data(xdata, ydata)
        return line,

    fig, ax = plt.subplots()
    line, = ax.plot([], [], lw=2)
    ax.grid()
    xdata, ydata = [], []

    def run(data):
        # update the data
        t, y = data
        xdata.append(t)
        ydata.append(y)
        xmin, xmax = ax.get_xlim()

        if t >= xmax:
            ax.set_xlim(xmin, 2*xmax)
            ax.figure.canvas.draw()
        line.set_data(xdata, ydata)

        return line,

    # Only save last 100 frames, but run forever
    ani = animation.FuncAnimation(fig, run, data_gen, interval=100, init_func=init)
    plt.show()