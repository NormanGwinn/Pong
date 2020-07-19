import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import numpy as np
import pandas as pd
from sklearn import linear_model

import court

class Predictor():
    epsilon = 0.0001

    def __init__(self):
        self.projected_y = 0.0
        self.predicted_y = 0.0
        self.ball_path = pd.DataFrame(columns=['X','Y'])
        self.animation = None
        self.figure = None
        self.ax = None
        self.final_y_arrow = None
        self.projected_y_arrow = None
        self.projected_path_arrow = None
        self.path_markers = None

    def fold_y(self, y):
        folded_y = y
        if y > 3:
            folded_y = y - 4.0
        elif y > 1:
            folded_y = 2.0 - y
        elif y < -1:
            folded_y = -2.0 - y
        elif y < -3:
            folded_y = y + 4.0
        return folded_y

    def predict_y(self, x, y):
        self.ball_path.loc[self.ball_path.shape[0]] = {'X':x, 'Y':y}

        if len(self.ball_path) > 2:
            # Get the x,y coordinates for the three most recent points
            x1 = self.ball_path.iloc[-3,0]
            x2 = self.ball_path.iloc[-2,0]
            x3 = self.ball_path.iloc[-1,0]
            y1 = self.ball_path.iloc[-3,1]
            y2 = self.ball_path.iloc[-2,1]
            y3 = self.ball_path.iloc[-1,1]

            # Regress the path with two points, points 1 and 2 of the recent 3 points
            train_x = np.array([[x1],[x2]])
            train_y = np.array([[y1],[y2]])
            regr = linear_model.LinearRegression()
            regr.fit(train_x, train_y)
            #print(f'Fit Results:  Y = {regr.intercept_[0]} + {regr.coef_[0]} x')
            
            # Use the most recent point, point 3, to test the regression
            predicted_y3 = regr.predict(np.array([[x3]]))[0][0]

            # If the last three points are colinear, then a wall or paddle
            # has not interrupted the path, and the regression model is
            # valid for predicting the Y-intercept for the right paddle.
            if abs(predicted_y3 - y3) < Predictor.epsilon:
                # Set the projected_x, based on the ball direction
                if x3 < x2:
                    projected_x = -1.5 * court.COURT_WIDTH
                else:
                    projected_x = 0.5 * court.COURT_WIDTH
                self.projected_y = regr.predict(np.array([[projected_x]]))[0][0]
                self.predicted_y = self.fold_y(self.projected_y)
                #print(f'Precited a y intercept of {self.predicted_y}')
            else:
                pass
                #print('But third point was not colinear.')

            # Reset the ball_path after a bounce against the right side
            if x2 > 0 and x2 > x1 and x2 > x3:
                self.ball_path.drop(self.ball_path.index, inplace=True)
            # Reset the ball_path after a score
            if abs(x3) > 0.5 * court.COURT_WIDTH:
                self.ball_path.drop(self.ball_path.index, inplace=True)

        return self.predicted_y

    def get_projected_arrow_geometry(self):
        x = 0
        y = 0
        dx = -3 * court.COURT_WIDTH/2
        dy = 0
        if self.ball_path.shape[0] > 1:
            ball_x_prev = self.ball_path.iloc[-2,0]
            ball_x = self.ball_path.iloc[-1,0]
            ball_y = self.ball_path.iloc[-1,1]
            x = ball_x
            y = ball_y
            if ball_x_prev > ball_x:
                dx = -3 * court.COURT_WIDTH/2 - ball_x
            else:
                dx = court.COURT_WIDTH/2 - ball_x
            dy = self.projected_y - ball_y
        return (x, y, dx, dy)

    def init(self):
        # Grid
        self.ax.set_xlim(-3.5 * court.COURT_WIDTH/2, 1.5 * court.COURT_WIDTH/2)
        self.ax.set_ylim(-5 * court.COURT_HEIGHT/2, 5 * court.COURT_HEIGHT/2)
        self.ax.grid(True)
        self.ax.xaxis.set_ticks(np.arange(-3,2,1))
        self.ax.yaxis.set_ticks(np.arange(-5,6,1))

        # Algorithm Markers
        self.ax.axvline(linewidth=1, color='r', dashes=(3,2))  #net
        self.ax.axvline(x = -3, linewidth=1, color='b')
        self.ax.axvline(x = 1, linewidth=1, color='b')
        self.ax.axhline(linewidth=1, color='r')
        self.ax.text(-2.8,3.92,'Yi = Yp - 4',fontsize=18,color='g')
        self.ax.text(-2.9,1.92,'Yi = -Yp + 2',fontsize=18,color='g')
        self.ax.text(-2.50,-0.18,'Yi = Yp',fontsize=18,color='g')
        self.ax.text(-2.85,-2.18,'Yi = -Yp - 2',fontsize=18,color='g')
        self.ax.text(-2.85,-4.18,'Yi = Yp + 4',fontsize=18,color='g')
        self.ax.axhline(y=5,xmin=0.1,xmax=0.5,linewidth=3,color='g')
        self.ax.axhline(y=3,xmin=0.1,xmax=0.5,linewidth=3,color='g')
        self.ax.axhline(y=1,xmin=0.1,xmax=0.5,linewidth=3,color='g')
        self.ax.axhline(y=-1,xmin=0.1,xmax=0.5,linewidth=2,color='g')
        self.ax.axhline(y=-3,xmin=0.1,xmax=0.5,linewidth=3,color='g')
        self.ax.axhline(y=-5,xmin=0.1,xmax=0.5,linewidth=3,color='g')

        # Court
        self.ax.add_patch(plt.Rectangle((-1,-1), court.COURT_WIDTH, court.COURT_HEIGHT, fill=False, linewidth=2))

        # Build the path projection arrow
        (ppa_x, ppa_y, ppa_dx, ppa_dy) = self.get_projected_arrow_geometry()
        self.projected_path_arrow = self.ax.add_patch(plt.Arrow(ppa_x,ppa_y,ppa_dx,ppa_dy,width=0.1,color='b'))
        
        self.projected_y_arrow = self.ax.add_patch(plt.Arrow(-3.5,self.projected_y,0.5,0.0,width=0.2,color='b'))
        self.final_y_arrow = self.ax.add_patch(plt.Arrow(1.5,self.predicted_y,-0.5,0.0,width=0.2,color='g'))
        self.path_markers, = self.ax.plot(self.ball_path.X, self.ball_path.Y, 'ko')

        return self.projected_path_arrow, self.projected_y_arrow, self.final_y_arrow, self.path_markers

    def update(self, frame):
        self.path_markers.set_data([], [])
        self.path_markers.set_data(self.ball_path.X, self.ball_path.Y)
        #print(f'The ball_path DataFrame shape is {self.ball_path.shape}')
        (ppa_x, ppa_y, ppa_dx, ppa_dy) = self.get_projected_arrow_geometry()
        self.projected_path_arrow = self.ax.add_patch(plt.Arrow(ppa_x,ppa_y,ppa_dx,ppa_dy,width=0.1,color='b'))
        self.projected_y_arrow = self.ax.add_patch(plt.Arrow(-3.5,self.projected_y,0.5,0.0,width=0.2,color='b'))
        self.final_y_arrow = self.ax.add_patch(plt.Arrow(1.5,self.predicted_y,-0.5,0.0,width=0.2,color='g'))

        return self.projected_path_arrow, self.projected_y_arrow, self.final_y_arrow, self.path_markers

    def start(self, fig):
        self.figure = fig
        if self.ax is None:
            self.ax = fig.add_subplot(111)
        if self.animation is not None:
            self.animation.event_source.stop()
        self.animation = FuncAnimation(self.figure, self.update, interval=200,
                            init_func=self.init, blit=True)