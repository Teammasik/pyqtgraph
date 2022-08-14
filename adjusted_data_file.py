import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject
from random import randint


class DataModel(QObject):
    coordinate_changed = pyqtSignal()
    coordinate_moved = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x1, self.x2, self.y1, self.y2 = None, None, None, None
        self.moved_data = None
        self.pos = ["w", "w"]

    def coordinates(self):
        return [self.x1, self.x2, self.y1, self.y2]

    def generate_new_coordinates(self):
        self.x1 = randint(-10, 10)
        self.x2 = randint(-10, 10)
        self.y1 = randint(-10, 10)
        self.y2 = randint(-10, 10)
        self.coordinate_changed.emit()

    def moved_data_acquiring(self, sent_inform):
        self.moved_data = sent_inform
        # print(sent_inform)  off
        self.coordinate_moved.emit()

    def set_color(self):
        print('available colors: yellow, red, orange, green, blue, dark blue')
        color_1 = input('enter color for the 1st line ')
        color_2 = input('enter color for the 2st line ')
        return color_1, color_2

    def set_pos(self):
        self.pos[0] = input('Enter a position of 1st dot, then press enter, example: 1,1\n ')
        self.pos[1] = input('Enter a position of 2nd dot - ')
        if self.pos[0].count(',') == 1 and self.pos[1].count(',') == 1:
            self.pos = self.pos[0].split(',') + self.pos[1].split(',')
            return self.pos
        else:
            print("wrong coordinates! try again")








