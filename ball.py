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
    acceleration = 1.01
    path_columns = ['TimeStamp','X','Y','Angle','Speed','Final_Y']

    def __init__(self, xy, angle, speed):
        super().__init__(xy, angle, speed)
        self._engine = create_engine('sqlite:///pong.db')
        self._artist = plt.Rectangle(self._get_lower_left(), LinearSquare.width, LinearSquare.height, color='g')
        self._path_trace = pd.DataFrame(columns=LinearSquare.path_columns)
        self._path_start = dt.datetime.now()
        self._bounce_sound = sa.WaveObject.from_wave_file('click_x.wav')

    def __del__(self): 
        print('Destructor called, LinearSquare Ball deleted.') 

    def _get_lower_left(self):
        return (self._xy[0] - 0.5 * LinearSquare.width, self._xy[1] - 0.5 * LinearSquare.height)

    def update_location(self, dtime):
        dx = self._speed * dtime.total_seconds() * np.cos(self._angle)
        dy = self._speed * dtime.total_seconds() * np.sin(self._angle)
        #print(dx, dy, dtime, dtime.total_seconds())
        new_x = self._xy[0] + dx
        if new_x < -court.COURT_WIDTH/2:
            self._bounce_sound.play()
            new_x = -court.COURT_WIDTH - new_x
            self._angle = np.pi - self._angle
            if self._angle < 0:
                self._angle += 2 * np.pi
            self._speed *= 1.02
        if new_x > court.COURT_WIDTH/2:
            self._bounce_sound.play()

            # Compute Final Y
            old_x = self._xy[0]
            ratio_before_bounce = (0.5*court.COURT_WIDTH - old_x)/dx
            final_y = self._xy[1] + ratio_before_bounce * dy
            self._path_trace.Final_Y = final_y
            print(self._path_trace)
            self._path_trace.to_sql('path', con=self._engine, index=False, if_exists='append')
            self._path_trace.drop(self._path_trace.index, inplace=True)

            # Update ball location
            new_x = court.COURT_WIDTH - new_x
            self._angle = np.pi - self._angle
            if self._angle < 0:
                self._angle += 2 * np.pi            
            self._speed *= 1.02
        new_y = self._xy[1] + dy
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
        new_row = {'TimeStamp':(dt.datetime.now() - self._path_start).total_seconds(),
                    'X':self._xy[0],
                    'Y':self._xy[1],
                    'Angle':self._angle,
                    'Speed':self._speed,
                    'Final_Y':0.0}
        self._path_trace.loc[self._path_trace.shape[0]] = new_row

    def get_artist(self):
        return self._artist
