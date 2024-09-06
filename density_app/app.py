
""" 

"""
import tkinter as tk
from tkinter import ttk
import measurment
import analysis


def main():
    #Setup Tk()
    global window 
    window = tk.Tk()
    window.title("Alkali Density")

    #Setup the notebook (tabs)
    notebook = ttk.Notebook(window)
    frame1 = ttk.Frame(notebook)
    frame2 = ttk.Frame(notebook)
    notebook.add(frame1, text="Data Collection")
    notebook.add(frame2, text="Analysis")
    notebook.grid()

    #Create tab frames
    m = measurment.App(master=frame1)
    m.grid()
    a = analysis.App(master=frame2)
    a.grid()

    #Main loop
    window.mainloop()

if __name__ == '__main__':
    main()