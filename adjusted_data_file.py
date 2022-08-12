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
        print(sent_inform)
        self.coordinate_moved.emit()








