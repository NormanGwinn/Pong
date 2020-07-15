from abc import ABC, abstractmethod
import datetime as dt
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
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

    def __init__(self, xy, angle, speed):
        super().__init__(xy, angle, speed)
        self._engine = create_engine('sqlite:///pong.db')
        self._artist = plt.Rectangle(self._get_lower_left(), LinearSquare.width, LinearSquare.height, color='g')

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
            new_x = -court.COURT_WIDTH - new_x
            self._angle = (np.pi - self._angle) % (2 * np.pi)
            self._speed *= 1.02
        if new_x > court.COURT_WIDTH/2:
            new_x = court.COURT_WIDTH - new_x
            self._angle = (np.pi - self._angle) % (2 * np.pi)
            self._speed *= 1.02
        new_y = self._xy[1] + dy
        if new_y > court.COURT_HEIGHT/2:
            new_y = court.COURT_HEIGHT - new_y
            self._angle = -self._angle
        if new_y < -court.COURT_HEIGHT/2:
            new_y = -court.COURT_HEIGHT - new_y
            self._angle = -self._angle
        self._xy = (new_x, new_y)
        #print(f'New XY:  {self._xy}')
        self._artist.set_xy(self._get_lower_left())
        with self._engine.connect() as conn:
            conn.execute("insert into path values(?,?,?,?,?)", 
            #(1.1,self._xy[0],self._xy[1],self._angle,self._speed))
            (dt.datetime.now().timestamp(),self._xy[0],self._xy[1],self._angle,self._speed))

    def get_artist(self):
        return self._artist
