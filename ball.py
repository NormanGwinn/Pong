from abc import ABC, abstractmethod
import datetime as dt
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import pandas as pd
import simpleaudio as sa
import numpy as np
import court

class AbstractBall(ABC):
 
    def __init__(self, xy, angle, speed):
        self._xy = xy         # (x, y) pair for center of ball; type:  tuple(float, float)
        self._angle = angle   # angle, in radians, indicating the direction of the ball; type:  float
        self._speed = speed   # speed, in units/second; type:  float
        super().__init__()
    
    @abstractmethod
    def reset(self, xy, angle, speed):
        pass

    # dtime := time elapsed; type:  dt.timedelta
    # returns:  xy; type:  tuple(float, float)
    @abstractmethod
    def update_location(self, dtime):
        pass

    @abstractmethod
    def get_artist(self):
        pass

class LinearSquare(AbstractBall):
    width = 0.04 * court.COURT_HEIGHT
    height = width
    acceleration = 1.05
    path_columns = ['TimeStamp','X','Y','Angle','Speed','Final_Y']

    def __init__(self, xy, angle, speed, left_paddle, right_paddle, training = True):
        super().__init__(xy, angle, speed)
        self._engine = create_engine('sqlite:///pong.db')
        self._artist = plt.Rectangle(self._get_lower_left(), LinearSquare.width, LinearSquare.height, color='w')
        self._path_trace = pd.DataFrame(columns=LinearSquare.path_columns)
        self._path_start = dt.datetime.now()
        self._bounce_sound = sa.WaveObject.from_wave_file('click_x.wav')

        self._left_paddle = left_paddle
        self._right_paddle = right_paddle
        self._training = training

    def __del__(self):
        pass
        #print('Destructor called, LinearSquare Ball deleted.') 

    def reset(self, xy, angle, speed):
        self._xy = xy         # (x, y) pair for center of ball; type:  tuple(float, float)
        self._angle = angle   # angle, in radians, indicating the direction of the ball; type:  float
        self._speed = speed   # speed, in units/second; type:  float

    def _get_lower_left(self):
        return (self._xy[0] - 0.5 * LinearSquare.width, self._xy[1] - 0.5 * LinearSquare.height)

    def update_location(self, dtime):
        dx = self._speed * dtime.total_seconds() * np.cos(self._angle)
        dy = self._speed * dtime.total_seconds() * np.sin(self._angle)
        #print(dx, dy, dtime, dtime.total_seconds())
        new_x = self._xy[0] + dx
        new_y = self._xy[1] + dy
        #print(f'Ball:  {new_x}, {new_y}')
        if new_x < -court.COURT_WIDTH/2:
            bounce = True
            if self._training == False:
                # Compute Final Y
                old_x = self._xy[0]
                ratio_before_bounce = (-0.5*court.COURT_WIDTH - old_x)/dx
                final_y = self._xy[1] + ratio_before_bounce * dy
                #print(f'Final Y {final_y}, ratio {ratio_before_bounce}, old y {self._xy[1]}')
                # Compare Final Y to paddle
                (paddle_bottom, paddle_top) = self._left_paddle.get_span()
                if final_y <= paddle_bottom or final_y >= paddle_top:
                    bounce = False
                #print(f'Left Paddle Span:  ({paddle_bottom}, {paddle_top}), ball:  {final_y}, bounce:  {bounce}')

            if bounce:
                self._bounce_sound.play()
                new_x = -court.COURT_WIDTH - new_x
                self._angle = np.pi - self._angle
                if self._angle < 0:
                    self._angle += 2 * np.pi
                self._speed *= LinearSquare.acceleration
        if new_x > court.COURT_WIDTH/2:
            bounce = True
            if self._training == False:
                # Compute Final Y
                old_x = self._xy[0]
                ratio_before_bounce = (0.5*court.COURT_WIDTH - old_x)/dx
                final_y = self._xy[1] + ratio_before_bounce * dy
                # Compare Final Y to paddle
                (paddle_bottom, paddle_top) = self._right_paddle.get_span()
                if final_y <= paddle_bottom or final_y >= paddle_top:
                    bounce = False
                #print(f'Right Paddle Span:  ({paddle_bottom}, {paddle_top}), ball:  {final_y}, bounce:  {bounce}')

            if bounce:
                self._bounce_sound.play()
                new_x = court.COURT_WIDTH - new_x
                self._angle = np.pi - self._angle
                if self._angle < 0:
                    self._angle += 2 * np.pi            
                self._speed *= LinearSquare.acceleration
        if new_y > court.COURT_HEIGHT/2:
            self._bounce_sound.play()
            new_y = court.COURT_HEIGHT - new_y
            self._angle = -self._angle
        if new_y < -court.COURT_HEIGHT/2:
            self._bounce_sound.play()
            new_y = -court.COURT_HEIGHT - new_y
            self._angle = -self._angle
        self._xy = (new_x, new_y)
        #print(f'New XY:  {self._xy}')
        self._artist.set_xy(self._get_lower_left())
        # new_row = {'TimeStamp':(dt.datetime.now() - self._path_start).total_seconds(),
        #             'X':self._xy[0],
        #             'Y':self._xy[1],
        #             'Angle':self._angle,
        #             'Speed':self._speed,
        #             'Final_Y':0.0}
        # self._path_trace.loc[self._path_trace.shape[0]] = new_row
        return (new_x, new_y)

    def get_artist(self):
        return self._artist
