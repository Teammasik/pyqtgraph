import sys
import pyqtgraph as pg

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QSizePolicy
from pyqtgraph import Point

from adjusted_data_file import DataModel


class Viewer(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._central_widget = QWidget()
        self._button = QPushButton('Push me to enter the coordinates')
        self._button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self._button1 = QPushButton('Push me to put the color')
        self._button1.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self._plot_wdg = pg.PlotWidget(enableMenu=False, title="Moving lines")

        layout = QVBoxLayout()
        layout.addWidget(self._button)
        layout.addWidget(self._button1)
        layout.addWidget(self._plot_wdg)
        self._central_widget.setLayout(layout)
        self.setCentralWidget(self._central_widget)
        self.resize(800, 600)                                           # set the window size

        self._data_model = None

        self._button.clicked.connect(self.set_pos)                      # get pos from user
        self._button.clicked.connect(self.send_moved_data)              # move this data to data_file
        self._button1.clicked.connect(self.set_color)                   # get color of each line from user
        self._plot_wdg.setRange(xRange=[-10, 10], yRange=[-10, 10])     # set the coordinate system

        # creating 2 movable lines
        self._mouseline = pg.LineSegmentROI([[1, 1], [10, 2]], movable=True, rotatable=False, pen=(1, 10))
        self._second_mouseline = pg.LineSegmentROI([[4, 4], [13, 5]], movable=True, rotatable=False, pen=(2, 4))

        # making them unmovable when holding the handles
        handles = self._mouseline.handles
        for handle in handles:
            handle['item'].disconnectROI(self._mouseline)
        handles = self._second_mouseline.handles
        for handle in handles:
            handle['item'].disconnectROI(self._second_mouseline)

        self._plot_wdg.addItem(self._mouseline)
        self._plot_wdg.addItem(self._second_mouseline)
        self._mouseline.sigRegionChanged.connect(self.send_moved_data)   # sending data///

        self._points_data = None
        self._updated_data = None
        self._flag_point = False
        self._state_for_second = None
        self._points_data_second = None
        self._moved_data_second = None
        self._pos = [0, 0]
        self._p1, self._p2, self._c1, self._c2, self._c3, self._c4 = None, None, None, None, None, None

        # dicts for error control
        self._colors = {'yellow': (2, 10), 'red': (1, 1), 'orange': (1, 10), 'green': (1, 3), 'blue': (2, 4),
                        'dark blue': (2, 3)}
        self._color_palette = ['yellow', 'red', 'orange', 'green', 'blue', 'dark blue']

    def set_data_model(self, dm: DataModel):
        self._data_model = dm

        self._data_model.coordinate_changed.connect(self._on_model_points_changed)  # to draw for the 1st time
        self._data_model.coordinate_moved.connect(self.send_moved_data)             # sending data to a data_file
        self._data_model.coordinate_moved.connect(self.catch_up_movement)           # making 2nd line move together
                                                                                    # with the 1st

        self._data_model.generate_new_coordinates()  # by calling this func, signal crd_changed emits

    def _on_model_points_changed(self):
        # when points change, we 'draw' lines, when entered for the 1st time, _pos == [0,0], else statement works
        # if we moved line by ourselves, _pos acquires points, thus _pos != [0, 0]
        if self._pos != [0, 0]:
            self._x1 = int(self._pos[0])                    # in line 150 we get _pos value
            self._y1 = int(self._pos[1])
            self._x2 = int(self._pos[2])
            self._y2 = int(self._pos[3])
        else:
            crdn = self._data_model.coordinates()           # getting coordinates from data_file, which were
            self._x1 = crdn[0]                              # generated randomly
            self._y1 = crdn[1]
            self._x2 = crdn[2]
            self._y2 = crdn[3]

        self.drawing_lines(True)

    def drawing_lines(self, statement):
        # If we move 1st line (which moves both lines), we set coordinates for both lines / statement == True
        # If we move 2nd line, we set pos only for 2nd line                               / statement == False
        if statement:
            state = {'pos': Point(0.000000, 0.000000), 'size': Point(1.000000, 1.000000), 'angle': 0.0,
                     'points': [Point(self._x1, self._y1), Point(self._x2, self._y2)]}
            self._state_for_second = {'pos': Point(0.000000, 0.000000), 'size': Point(1.000000, 1.000000), 'angle': 0.0,
                                      'points': [Point(self._x1 + 3, self._y1 + 3), Point(self._x2 + 3, self._y2 + 3)]}

            self._mouseline.setState(state)
            self._second_mouseline.setState(self._state_for_second)

        else:
            self._state_for_second = {'pos': Point(self._p1, self._p2), 'size': Point(1.000000, 1.000000), 'angle': 0.0,
                                      'points': [Point(self._c1, self._c2), Point(self._c3, self._c4)]}
            
            self._second_mouseline.setState(self._state_for_second)

    def send_moved_data(self):
        # _flag_point being used for loop avoidance
        if not self._flag_point:
            self._points_data = self._mouseline.getState()  # here, we get a dict, which has multiple elements,
            p1 = self._points_data['pos'][0] + self._x1     # but only pos is needed
            p2 = self._points_data['pos'][1] + self._y1
            p3 = self._points_data['pos'][0] + self._x2
            p4 = self._points_data['pos'][1] + self._y2

            self._updated_data = [p1, p2, p3, p4]
            self._flag_point = True
            self._data_model.moved_data_acquiring(self._updated_data)
            self._flag_point = False

    def catch_up_movement(self):
        # here we get coordinates to move 2nd line, when 1st being dragged by user
        self._points_data_second = self._second_mouseline.getState()

        self._p1 = self._points_data_second['pos'][0]  # self._p1/self._p2 variables for translocation
        self._p2 = self._points_data_second['pos'][1]

        self._c1 = self._points_data['pos'][0] + self._x1 + 3  # _c - variables for coordinates
        self._c2 = self._points_data['pos'][1] + self._y1 + 3
        self._c3 = self._points_data['pos'][0] + self._x2 + 3
        self._c4 = self._points_data['pos'][1] + self._y2 + 3

        self.drawing_lines(False)

    def set_color(self):
        # getting color from data_file
        color_1, color_2 = self._data_model.set_color()
        if color_1 and color_2 in self._color_palette:              # checking if word from user matches
            self._mouseline.setPen(self._colors[color_1])           # the value from dic
            self._second_mouseline.setPen(self._colors[color_2])
        else:
            print("wrong color or you've made a typo, try again")

    def set_pos(self):
        # getting coordinates from data_file
        self._pos = self._data_model.set_pos()
        if self._pos is not None:                               # checks, if user entered everything correctly
            self._on_model_points_changed()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = Viewer()
    data_model = DataModel()
    view.set_data_model(data_model)
    view.show()
    sys.exit(app.exec_())
