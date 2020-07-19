import datetime as dt
import tkinter
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler # Implement the default Matplotlib key bindings.
from matplotlib.figure import Figure
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import simpleaudio as sa
import time
import traceback
import court
import paddle
import ball
import predictor

score_sound = sa.WaveObject.from_wave_file('phasers3.wav')
root = tkinter.Tk()
root.wm_title("Pong Machine Learning")

fig, ax1 = plt.subplots()
ax1.axes.xaxis.set_visible(False)
ax1.axes.yaxis.set_visible(False)
ax1.axvline(linewidth=1, color='r', dashes=(3,2))  #net

left_score = 0
right_score = 0
left_score_box = ax1.text(-0.5,0.7,'0',fontsize=30)
right_score_box = ax1.text(0.5,0.7,'0',fontsize=30)
left_paddle = paddle.BasicPaddle((-0.52 * court.COURT_WIDTH, 0.0), 'Human')
right_paddle = paddle.BasicPaddle((0.52 * court.COURT_WIDTH, 0.0), 'ML')
initial_angle = 0.25 * np.pi * (2.0 * np.random.rand() + 3.0)
ball = ball.LinearSquare((0.0,0.0), initial_angle, 1.0, left_paddle, right_paddle, training=False)

myPredictor = predictor.Predictor()
paddle_commands = []

def init():
    print(f'Initializing the animation at {dt.datetime.now()}, from call stack.')
    #traceback.print_stack()
    ax1.add_patch(ball.get_artist())
    ax1.add_patch(left_paddle.get_artist())
    ax1.add_patch(right_paddle.get_artist())

    ax1.set_xlim(-1.5 * court.COURT_WIDTH/2, 1.5 * court.COURT_WIDTH/2)
    ax1.set_ylim(-1.0 * court.COURT_HEIGHT/2, 1.0 * court.COURT_HEIGHT/2)
    return ball.get_artist(), left_paddle.get_artist(), right_paddle.get_artist(), left_score_box, right_score_box

def update(frame):
    global paddle_commands
    global left_score
    global right_score

    # ball
    (x, y) = ball.update_location(dt.timedelta(milliseconds = 100))
    reset_ball = False
    if x < -0.5 * court.COURT_WIDTH:
        right_score += 1
        right_score_box.set_text(str(right_score))
        print(f'right_score_box.text is {right_score_box.get_text()}')
        score_sound.play()
        #raise StopIteration
        reset_ball = True
    if x > 0.5 * court.COURT_WIDTH:
        left_score += 1
        left_score_box.set_text(str(left_score))
        print(f'left_score_box.text is {left_score_box.get_text()}')
        score_sound.play()
        #raise StopIteration
        reset_ball = True

    if reset_ball:
        initial_angle = 0.25 * np.pi * (2.0 * np.random.rand() + 3.0)
        ball.reset((0.0, 0.0), initial_angle, 1.0)
        #time.sleep(1)

    predicted_y = myPredictor.predict_y(x, y)
    #print(f'The predicted Y is {predicted_y}')

    # left_paddle
    #print(f'The paddle command list is {paddle_commands}')
    dy = 0.0
    for letter in paddle_commands:
        if letter == 'u':
            dy += 0.1
        elif letter == 'd':
            dy -= 0.1
    paddle_commands = []
    left_paddle.update_location(dy)

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

    return ball.get_artist(), left_paddle.get_artist(), right_paddle.get_artist(), left_score_box, right_score_box

lbl_instructions = tkinter.Label(root, text="Control the Left Paddle with the 'u' (up) and 'd' (down) keys.")
lbl_instructions.pack()

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
#canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

def on_key_press(event):
    #print("you pressed {}".format(event.key))
    if event.key in ['u','d']:
        paddle_commands.append(event.key)
    #key_press_handler(event, canvas, toolbar)

canvas.mpl_connect("key_press_event", on_key_press)

def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

button = tkinter.Button(master=root, text="Quit", command=_quit)
button.pack(side=tkinter.BOTTOM)

ani = FuncAnimation(fig, update, interval=200,
                    init_func=init, blit=True)

# ani = FuncAnimation(fig, update, frames=np.arange(0,60), interval=200,
#                     init_func=init, blit=True)

#root.resizable(False, False) 
tkinter.mainloop()

