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
        self.resize(800, 600)

        self._data_model = None

        self._button.clicked.connect(self.set_pos)
        self._button.clicked.connect(self.send_moved_data)
        self._button1.clicked.connect(self.set_color)
        self._plot_wdg.setRange(xRange=[-10, 10], yRange=[-10, 10])

        self._mouseline = pg.LineSegmentROI([[0, 0], [1, 1]], movable=True, rotatable=False, pen=(1, 10))
        # self._mouseline.addRotateHandle([1, 1], [0, 0], name='1st')
        # self._mouseline.addRotateHandle([10, 2], [0, 0], name='2nd')
        # print(self._mouseline.handles)
        self._second_mouseline = pg.LineSegmentROI([[0, 0], [1, 1]], movable=True, rotatable=False, pen=(2, 4))
        # self._second_mouseline.addRotateHandle([4, 4], [0, 0])
        # self._second_mouseline.addRotateHandle([13, 5], [0, 0])
        self._plot_wdg.addItem(self._mouseline)
        self._plot_wdg.addItem(self._second_mouseline)
        self._mouseline.sigRegionChanged.connect(self.send_moved_data)

        self._points_data = None
        self._updated_data = None
        self._flag_point = False
        self._state_for_second = None
        self._points_data_second = None
        self._moved_data_second = None
        self._pos = [0, 0]
        self._colors = {'yellow': (2, 10), 'red': (1, 1), 'orange': (1, 10), 'green': (1, 3), 'blue': (2, 4),
                        'dark blue': (2, 3)}
        self._color_palette = ['yellow', 'red', 'orange', 'green', 'blue', 'dark blue']

    def set_data_model(self, dm: DataModel):
        self._data_model = dm

        self._data_model.coordinate_changed.connect(self._on_model_points_changed)
        self._data_model.coordinate_moved.connect(self.send_moved_data)
        self._data_model.coordinate_moved.connect(self.catch_up_movement)
        self._second_mouseline.sigRegionChangeFinished.connect(self.moved_second_graph)

        self._data_model.generate_new_coordinates()

    def _on_model_points_changed(self):

        if self._pos != [0, 0]:
            self._x1 = int(self._pos[0])
            self._y1 = int(self._pos[1])
            self._x2 = int(self._pos[2])
            self._y2 = int(self._pos[3])
        else:
            crdn = self._data_model.coordinates()
            self._x1 = crdn[0]
            self._x2 = crdn[1]
            self._y1 = crdn[2]
            self._y2 = crdn[3]

        self.drawing_lines()
        # state = {'pos': Point(0.000000, 0.000000), 'size': Point(1.000000, 1.000000), 'angle': 0.0,
        #          'points': [Point(self._x1, self._y1), Point(self._x2, self._y2)]}
        # self._state_for_second = {'pos': Point(0.000000, 0.000000), 'size': Point(1.000000, 1.000000), 'angle': 0.0,
        #                          'points': [Point(self._x1+3, self._y1+3), Point(self._x2+3, self._y2+3)]}
        #
        # self._second_mouseline.sigRegionChangeFinished.disconnect(self.moved_second_graph)
        # # self._mouseline.sigRegionChangeFinished.disconnect(self.send_moved_data)
        # self._mouseline.setState(state)
        # self._second_mouseline.setState(self._state_for_second)
        # # self._mouseline.sigRegionChangeFinished.connect(self.send_moved_data)
        # self._second_mouseline.sigRegionChangeFinished.connect(self.moved_second_graph)

    def drawing_lines(self):
        state = {'pos': Point(0.000000, 0.000000), 'size': Point(1.000000, 1.000000), 'angle': 0.0,
                 'points': [Point(self._x1, self._y1), Point(self._x2, self._y2)]}
        self._state_for_second = {'pos': Point(0.000000, 0.000000), 'size': Point(1.000000, 1.000000), 'angle': 0.0,
                                  'points': [Point(self._x1 + 3, self._y1 + 3), Point(self._x2 + 3, self._y2 + 3)]}

        # self._second_mouseline.sigRegionChangeFinished.disconnect(self.moved_second_graph) let it be there
        self._mouseline.setState(state)
        self._second_mouseline.setState(self._state_for_second)
        # self._second_mouseline.sigRegionChangeFinished.connect(self.moved_second_graph) same as 103 line

    def send_moved_data(self):
        if not self._flag_point:
            self._points_data = self._mouseline.getState()  # here, we get an array, which has multiple elements,
            p1 = self._points_data['pos'][0] + self._x1  # but only pos is needed
            p2 = self._points_data['pos'][1] + self._y1
            p3 = self._points_data['pos'][0] + self._x2
            p4 = self._points_data['pos'][1] + self._y2

            self._updated_data = [p1, p2, p3, p4]
            self._flag_point = True
            self._data_model.moved_data_acquiring(self._updated_data)
            self._flag_point = False

    def catch_up_movement(self):

        self._points_data_second = self._second_mouseline.getState()

        p1 = self._points_data_second['pos'][0]  # p1/p2 variables for translocation
        p2 = self._points_data_second['pos'][1]

        c1 = self._points_data['pos'][0] + self._x1 + 3  # c - variables for coordinates
        c2 = self._points_data['pos'][1] + self._y1 + 3
        c3 = self._points_data['pos'][0] + self._x2 + 3
        c4 = self._points_data['pos'][1] + self._y2 + 3

        # print(self._points_data_second, '\n')  off

        self._state_for_second = {'pos': Point(p1, p2), 'size': Point(1.000000, 1.000000), 'angle': 0.0,
                                  'points': [Point(c1, c2), Point(c3, c4)]}
        # self._second_mouseline.sigRegionChangeFinished.disconnect(self.moved_second_graph) let it be there
        self._second_mouseline.setState(self._state_for_second)
        # self._second_mouseline.sigRegionChangeFinished.connect(self.moved_second_graph) let it be there

    def position_for_second(self):
        data = self._second_mouseline.getState()
        return data

    def moved_second_graph(self):
        self._moved_data_second = self.position_for_second()

    def set_color(self):
        color_1, color_2 = self._data_model.set_color()
        if color_1 and color_2 in self._color_palette:
            self._mouseline.setPen(self._colors[color_1])
            self._second_mouseline.setPen(self._colors[color_2])
        else:
            print("wrong color or you've made a typo, try again")

    def set_pos(self):
        self._pos = self._data_model.set_pos()
        # print(self._pos)  off
        if self._pos is not None:
            self._on_model_points_changed()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = Viewer()
    data_model = DataModel()
    view.set_data_model(data_model)
    view.show()
    sys.exit(app.exec_())
