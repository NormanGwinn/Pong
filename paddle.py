from abc import ABC, abstractmethod
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import court
 
class AbstractPaddle(ABC):
 
    def __init__(self, xy):
        self._xy = xy         # (x, y) pair for center of paddle; type:  tuple(float, float)
        super().__init__()
    
    # dtime := time elapsed; type:  dt.timedelta
    # returns:  xy; type:  tuple(float, float)
    @abstractmethod
    def update_location(self, dtime):
        pass

    @abstractmethod
    def get_artist(self):
        pass

class BasicPaddle(AbstractPaddle):
    width = 0.04 * court.COURT_WIDTH
    height = 0.2 * court.COURT_HEIGHT

    def __init__(self, xy):
        super().__init__(xy)
        self._artist = plt.Rectangle(self._get_lower_left(), BasicPaddle.width, BasicPaddle.height, color='b')

    def _get_lower_left(self):
        return (self._xy[0] - 0.5 * BasicPaddle.width, self._xy[1] - 0.5 * BasicPaddle.height)

    def update_location(self, dtime):
        dy = dtime.total_seconds() * (0.5 - np.random.rand())
        self._xy = (self._xy[0], self._xy[1] + dy)
        #print(f'New XY:  {self._xy}')
        self._artist.set_xy(self._get_lower_left())

    def get_artist(self):
        return self._artist
