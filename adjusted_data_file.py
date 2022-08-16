from PyQt5.QtCore import pyqtSignal, QObject
from random import randint


class DataModel(QObject):
    coordinate_changed = pyqtSignal()
    coordinate_moved = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._x1_d, self._x2_d, self._y1_d, self._y2_d = None, None, None, None
        self._pos_data = ["w", "w"]

    def coordinates(self):
        return [self._x1_d, self._y1_d, self._x2_d, self._y2_d]

    def generate_new_coordinates(self):
        # generating coordinates for the 1st time
        self._x1_d = randint(-10, 10)
        self._x2_d = randint(-10, 10)
        self._y1_d = randint(-10, 10)
        self._y2_d = randint(-10, 10)
        self.coordinate_changed.emit()

    def moved_data_acquiring(self, state):
        # emits when line changes its position
        self.coordinate_moved.emit()

    def set_color(self):
        # getting color from user
        print('available colors: yellow, red, orange, green, blue, dark blue')
        color_1 = input('enter color for the 1st line\n type: ')
        color_2 = input('enter color for the 2st line\n type: ')
        return color_1, color_2

    def set_pos(self):
        # getting coordinates from user, checking if everything is correct
        self._pos_data[0] = input('Enter a position of 1st dot, then press enter, example: 1,1\n type: ')
        self._pos_data[1] = input('Enter a position of 2nd dot \n type: ')
        if self._pos_data[0].count(',') == 1 and self._pos_data[1].count(',') == 1:
            self._pos_data = self._pos_data[0].split(',') + self._pos_data[1].split(',')
            return self._pos_data
        else:
            print("wrong coordinates! try again")








