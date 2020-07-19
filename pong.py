import tkinter
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler # Implement the default Matplotlib key bindings.
from matplotlib.figure import Figure

import court
import game

pong = None
fig = Figure(figsize=(6,5), dpi=100)
ml_fig = Figure(figsize=(5,8), dpi=100)

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
    global pong
    the_court = court.Court(color_scheme.get())
    pong = game.Game(fig, the_court, training_btn_value.get())
    pong.start()
    canvas.draw()
    btn_ml['state'] = tkinter.NORMAL

def show_ml():
    global pong
    ml_window = tkinter.Toplevel(root)
    ml_window.resizable(False, False)
    ml_window.title("The View from the Machine")
    tkinter.Label(ml_window, bg="white", fg="black", 
        text="The black box is the court.").pack(fill=tkinter.X)
    tkinter.Label(ml_window, bg="white", fg="black", 
        text="The black circles show the ball path.").pack(fill=tkinter.X)
    tkinter.Label(ml_window, bg="white", fg="blue", 
        text="The blue arrows show the linear projected path and the projected Y.").pack(fill=tkinter.X)
    tkinter.Label(ml_window, bg="white", fg="blue", 
        text="The vertical blue lines show the projection boundaries for each direction.").pack(fill=tkinter.X)
    tkinter.Label(ml_window, bg="white", fg="green", 
        text="The green lines and formulas show the folding, to get the predicted Y.").pack(fill=tkinter.X)
    tkinter.Label(ml_window, bg="white", fg="green", 
        text="The green arrow shows the predicted Y intercept for the right paddle.").pack(fill=tkinter.X)

    ml_canvas = FigureCanvasTkAgg(ml_fig, master=ml_window)  # A tk.DrawingArea.
    ml_canvas.draw()
    #ml_canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
    ml_canvas.get_tk_widget().pack(fill=tkinter.BOTH, expand=1)

    pong.get_predictor().start(ml_fig)

def ml_quit():
    pass

def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

### GUI Layout ###
root = tkinter.Tk()
root.configure(bg='white')
root.wm_title("Pong Machine Learning")
root.resizable(False, False) 

lbl_instructions = tkinter.Label(root, bg="white",
                                 text="Control the Left Paddle with the 'u' (up) and 'd' (down) keys.")
lbl_instructions.pack(fill=tkinter.X, pady=10)

training_btn_value = tkinter.BooleanVar(False)
#training_btn_value.set(False)
tkinter.Checkbutton(root, text="Training Mode", var=training_btn_value).pack(pady=10)

color_scheme = tkinter.IntVar()
color_scheme.set(1972)
tkinter.Label(root, bg="white", text="Select a Color Scheme").pack()
tkinter.Radiobutton(root, bg="white", text="1972", 
                    variable=color_scheme, value=1972).pack()
tkinter.Radiobutton(root, bg="white", text="2020", 
                    variable=color_scheme, value=2020).pack()

tkinter.Button(master=root, text="Start Game", command=start_game).pack(pady=10)

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
canvas.mpl_connect("key_press_event", on_key_press)

btn_ml = tkinter.Button(master=root, text="Show Machine Learning", 
               command=show_ml, state=tkinter.DISABLED)
btn_ml.pack(pady=10)

tkinter.Button(master=root, text="Quit", command=_quit).pack(pady=10)

tkinter.mainloop()
