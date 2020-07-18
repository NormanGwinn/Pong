import datetime as dt
import tkinter

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import court
import paddle
import ball
import predictor

root = tkinter.Tk()
root.wm_title("Pong Machine Learning")

fig, ax1 = plt.subplots()
ax1.axvline(linewidth=1, color='r', dashes=(3,2))  #net
left_paddle = paddle.BasicPaddle((-0.5 * court.COURT_WIDTH, 0.0))
right_paddle = paddle.BasicPaddle((0.5 * court.COURT_WIDTH, 0.0))
initial_angle = 0.25 * np.pi * (2.0 * np.random.rand() + 3.0)
ball = ball.LinearSquare((0.0,0.0), initial_angle, 1.0)
myPredictor = predictor.Predictor()

def init():
    print(f'Initializing the animation at {dt.datetime.now()}.')
    ax1.add_patch(ball.get_artist())
    ax1.add_patch(left_paddle.get_artist())
    ax1.add_patch(right_paddle.get_artist())
    ax1.set_xlim(-1.5 * court.COURT_WIDTH/2, 1.5 * court.COURT_WIDTH/2)
    ax1.set_ylim(-1.25 * court.COURT_HEIGHT/2, 1.25 * court.COURT_HEIGHT/2)
    return ball.get_artist(), left_paddle.get_artist(), right_paddle.get_artist()

def update(frame):
    # ball
    (x, y) = ball.update_location(dt.timedelta(milliseconds = 100))
    predicted_y = myPredictor.predict_y(x, y)
    print(f'The predicted Y is {predicted_y}')

    # right_paddle
    (x, y) = right_paddle.get_center()
    epsilon = 0.06
    dy = 0.0
    if abs(predicted_y - y) > epsilon:
        if predicted_y > y:
            dy = 0.1
        else:
            dy = -0.1
    right_paddle.update_location(dy)

    # left_paddle
    left_paddle.update_location(0.1*(0.5 - np.random.rand()))

    return ball.get_artist(), left_paddle.get_artist(), right_paddle.get_artist()

#plt.show()

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

def on_key_press(event):
    print("you pressed {}".format(event.key))
    key_press_handler(event, canvas, toolbar)

canvas.mpl_connect("key_press_event", on_key_press)

def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

button = tkinter.Button(master=root, text="Quit", command=_quit)
button.pack(side=tkinter.BOTTOM)

ani = FuncAnimation(fig, update, frames=np.arange(0,60), interval=200,
                    init_func=init, blit=True)

tkinter.mainloop()

