import tkinter
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler # Implement the default Matplotlib key bindings.
from matplotlib.figure import Figure
import game

pong = game.Game(diagnostics=False)
figure = pong.get_figure()

### GUI Callbacks ###
def toggle_color_scheme():
    print(f'In toggle_color_scheme.')
    pass

def on_key_press(event):
    #print("you pressed {}".format(event.key))
    if event.key in ['u','d']:
        pong.add_paddle_command(event.key)
    elif event.key in ['c']:
        toggle_color_scheme()
    #key_press_handler(event, canvas, toolbar)

def start_game():
    pong.start()
    canvas.draw()

def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

### GUI Layout ###
root = tkinter.Tk()
root.configure(bg='white')
root.wm_title("Pong Machine Learning")

lbl_instructions = tkinter.Label(root, text="Control the Left Paddle with the 'u' (up) and 'd' (down) keys.")
lbl_instructions.pack()

btn_start = tkinter.Button(master=root, text="Start Game", command=start_game)
btn_start.pack()

show_machine_learning = tkinter.BooleanVar() 
show_machine_learning.set(False)
chk_show_ml = tkinter.Checkbutton(root, var=show_machine_learning, text="Show Machine Learning")
chk_show_ml.pack()

canvas = FigureCanvasTkAgg(figure, master=root)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
canvas.mpl_connect("key_press_event", on_key_press)

btn_quit = tkinter.Button(master=root, text="Quit", command=_quit)
btn_quit.pack(side=tkinter.BOTTOM)

#root.resizable(False, False) 
tkinter.mainloop()
