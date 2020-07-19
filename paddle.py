from abc import ABC, abstractmethod
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import court
 
class AbstractPaddle(ABC):
 
    def __init__(self, xy, name):
        self._xy = xy         # (x, y) pair for center of paddle; type:  tuple(float, float)
        self._name = name
        super().__init__()
    
    # dy := requested change in y location; type:  float
    # returns:  xy; type:  tuple(float, float)
    @abstractmethod
    def update_location(self, dy):
        pass

    # return xy
    @abstractmethod
    def get_center(self):
        pass

    # return (y_bottom, y_top)
    @abstractmethod
    def get_span(self):
        pass

    @abstractmethod
    def get_artist(self):
        pass

class BasicPaddle(AbstractPaddle):
    width = 0.04 * court.COURT_WIDTH
    height = 0.15 * court.COURT_HEIGHT
    max_y = 0.5 * (court.COURT_HEIGHT - height)
    min_y = -max_y

    def __init__(self, xy, name):
        super().__init__(xy, name)
        self._artist = plt.Rectangle(self._get_lower_left(), BasicPaddle.width, BasicPaddle.height, color='b')

    def _get_lower_left(self):
        return (self._xy[0] - 0.5 * BasicPaddle.width, self._xy[1] - 0.5 * BasicPaddle.height)

    def get_center(self):
        return (self._xy[0], self._xy[1])        

    def get_span(self):
        y_bottom = self._xy[1] - 0.5 * BasicPaddle.height
        y_top = self._xy[1] + 0.5 * BasicPaddle.height
        #print(f'In get_span, y is {self._xy[1]}')
        return (y_bottom, y_top)

    def update_location(self, dy):
        #print(f'Paddle {self._name} center is {self._xy}')
        new_y = self._xy[1] + dy
        # Limit the range of the paddle, to keep it on the court
        if new_y > BasicPaddle.max_y:
            new_y = BasicPaddle.max_y
        elif new_y < BasicPaddle.min_y:
            new_y = BasicPaddle.min_y
        self._xy = (self._xy[0], new_y)
        #print(f'New XY:  {self._xy}')
        self._artist.set_xy(self._get_lower_left())
        return (self._xy[0], self._xy[1])

    def get_artist(self):
        return self._artist
