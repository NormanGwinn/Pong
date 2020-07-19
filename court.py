# The game will be centered on the XY axes
# The "court" will be 2 x 2:
#     -- lower left ("LL") corner of the court is (-1,-1)
#     -- upper right corner of the court is (1,1)

COURT_WIDTH = 2.0
COURT_HEIGHT = 2.0

class Court():
    
    def __init__(self, year=1972):
        self.court_color = 'k'
        self.paddle_color = 'w'
        self.ball_color = 'w'
        self.net_color = 'w'
        self.score_color = 'w'
        if year == 2020:
            self.court_color = 'w'
            self.paddle_color = 'b'
            self.ball_color = 'g'
            self.net_color = 'r'
            self.score_color = 'r'
