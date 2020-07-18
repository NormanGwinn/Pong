import pandas as pd
import numpy as np
from sklearn import linear_model
import court

class Predictor():
    epsilon = 0.0001

    def __init__(self):
        self.predicted_y = 0.0
        self.ball_path = pd.DataFrame(columns=['X','Y'])

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
                projected_y = regr.predict(np.array([[projected_x]]))[0][0]
                self.predicted_y = self.fold_y(projected_y)
                #print(f'Precited a y intercept of {self.predicted_y}')
            else:
                pass
                #print('But third point was not colinear.')

        return self.predicted_y