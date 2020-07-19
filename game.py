# Python Libraries
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import numpy as np
import simpleaudio as sa
import time

# Local Files
import court
import paddle
import ball
import predictor

class Game():
    score_sound = sa.WaveObject.from_wave_file('phasers3.wav')

    def __init__(self, fig):
        self.figure = fig
        self.ax1 = fig.add_subplot(111)
        self.ax1.set_facecolor('k')
        self.ax1.axes.xaxis.set_visible(False)
        self.ax1.axes.yaxis.set_visible(False)
        self.ax1.axvline(linewidth=1, color='w', dashes=(3,2))  #net
        self.left_score = 0
        self.right_score = 0
        self.left_score_box = None
        self.right_score_box = None
        self.left_paddle = paddle.BasicPaddle((-0.52 * court.COURT_WIDTH, 0.0), 'Human')
        self.right_paddle = paddle.BasicPaddle((0.52 * court.COURT_WIDTH, 0.0), 'ML')
        initial_angle = 0.25 * np.pi * (2.0 * np.random.rand() + 3.0)
        self.ball = ball.LinearSquare((0.0,0.0), initial_angle, 1.0, 
                                      self.left_paddle, self.right_paddle, training=False)
        self.predictor = predictor.Predictor()
        self.paddle_commands = []
        self.animation = None

    def get_figure(self):
        return self.figure

    def get_predictor(self):
        return self.predictor

    def init(self):
        print(f'Initializing the animation at {dt.datetime.now()}, from call stack.')
        self.left_score_box = self.ax1.text(-0.5,0.7,'0',fontsize=30,color='w')
        self.right_score_box = self.ax1.text(0.5,0.7,'0',fontsize=30,color='w')
        self.ax1.add_patch(self.ball.get_artist())
        self.ax1.add_patch(self.left_paddle.get_artist())
        self.ax1.add_patch(self.right_paddle.get_artist())

        self.ax1.set_xlim(-1.5 * court.COURT_WIDTH/2, 1.5 * court.COURT_WIDTH/2)
        self.ax1.set_ylim(-1.0 * court.COURT_HEIGHT/2, 1.0 * court.COURT_HEIGHT/2)
        return self.ball.get_artist(), self.left_paddle.get_artist(), \
               self.right_paddle.get_artist(), self.left_score_box, self.right_score_box

    def update(self, frame):
        global paddle_commands
        global left_score
        global right_score

        # ball
        (x, y) = self.ball.update_location(dt.timedelta(milliseconds = 100))
        reset_ball = False
        if x < -0.5 * court.COURT_WIDTH:
            self.right_score += 1
            self.right_score_box.set_text(str(self.right_score))
            #print(f'right_score_box.text is {right_score_box.get_text()}')
            #Game.score_sound.play()
            #raise StopIteration
            reset_ball = True
        if x > 0.5 * court.COURT_WIDTH:
            self.left_score += 1
            self.left_score_box.set_text(str(self.left_score))
            #print(f'left_score_box.text is {left_score_box.get_text()}')
            #Game.score_sound.play()
            #raise StopIteration
            reset_ball = True

        if reset_ball:
            initial_angle = 0.25 * np.pi * (2.0 * np.random.rand() + 3.0)
            self.ball.reset((0.0, 0.0), initial_angle, 1.0)
            #time.sleep(1)

        predicted_y = self.predictor.predict_y(x, y)
        #print(f'The predicted Y is {predicted_y}')

        # left_paddle
        #print(f'The paddle command list is {paddle_commands}')
        dy = 0.0
        for letter in self.paddle_commands:
            if letter == 'u':
                dy += 0.1
            elif letter == 'd':
                dy -= 0.1
        self.paddle_commands = []
        self.left_paddle.update_location(dy)

        # right_paddle
        (x, y) = self.right_paddle.get_center()
        epsilon = 0.06
        dy = 0.0
        if abs(predicted_y - y) > epsilon:
            if predicted_y > y:
                dy = 0.1
            else:
                dy = -0.1
        self.right_paddle.update_location(dy)

        return self.ball.get_artist(), self.left_paddle.get_artist(), \
               self.right_paddle.get_artist(), self.left_score_box, self.right_score_box

    def add_paddle_command(self, cmd):
        self.paddle_commands.append(cmd)

    def start(self):
        #print('Start Game')
        if self.animation is not None:
            self.animation.event_source.stop()
        self.animation = FuncAnimation(self.figure, self.update, interval=200,
                            init_func=self.init, blit=True)
