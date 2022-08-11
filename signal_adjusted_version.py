import sys
import numpy as np
import pyqtgraph as pg

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QSizePolicy
from pyqtgraph import Point

from adjusted_data_file import DataModel


class Viewer(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._central_widget = QWidget()
        self._button = QPushButton('Push me')
        self._button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._plot_wdg = pg.PlotWidget(enableMenu=False, title="TEST")

        layout = QVBoxLayout()
        layout.addWidget(self._button)
        layout.addWidget(self._plot_wdg)
        self._central_widget.setLayout(layout)
        self.setCentralWidget(self._central_widget)
        self.resize(800, 600)

        self._data_model = None

        self._button.clicked.connect(self._on_button_clicked)
        self._button.clicked.connect(self.send_moved_data)
        self._plot_wdg.setRange(xRange=[-10, 10], yRange=[-10, 10])

        self.mouseline = pg.LineSegmentROI([[0, 0], [1, 1]], movable=True, rotatable=False, pen=(1, 9))
        self.second_mouseline = pg.LineSegmentROI([[0, 0], [1, 1]], movable=True, rotatable=False, pen=(2, 9))

        self._plot_wdg.addItem(self.mouseline)
        self._plot_wdg.addItem(self.second_mouseline)
        self.mouseline.sigRegionChangeFinished.connect(self.send_moved_data)

        # self.second_mouseline.sigRegionChangeFinished.connect(self.moved_second_graph)

        # self.mouseline.sigRegionChangeFinished.connect(self.catch_up_movement)

        self.sending = None
        self.points_data = None
        self.updated_data = None
        self.flag_point = False
        self.state_for_second = None
        self.temp = {'pos': Point(0, 0)}
        self.points_data_second = None
        self.moved_data_second = None

    def set_data_model(self, dm: DataModel):
        self._data_model = dm

        self._data_model.coordinate_changed.connect(self._on_model_points_changed)
        self._data_model.coordinate_moved.connect(self.send_moved_data)  # new line
        self._data_model.coordinate_moved.connect(self.catch_up_movement)  # newer line
        self.second_mouseline.sigRegionChangeFinished.connect(self.moved_second_graph)

        self._data_model.generate_new_coordinates()

    def _on_button_clicked(self):
        self._data_model.generate_new_coordinates()

    def _on_model_points_changed(self):

        self.crdn = self._data_model.coordinates()
        self.x1 = self.crdn[0]
        self.x2 = self.crdn[1]
        self.y1 = self.crdn[2]
        self.y2 = self.crdn[3]
        # self.xdata = self.crdn[4] data for sin graph
        state = {'pos': Point(0.000000, 0.000000), 'size': Point(1.000000, 1.000000), 'angle': 0.0,
                 'points': [Point(self.x1, self.y1), Point(self.x2, self.y2)]}
        self.state_for_second = {'pos': Point(0.000000, 0.000000), 'size': Point(1.000000, 1.000000), 'angle': 0.0,
                                 'points': [Point(self.x1+3, self.y1+3), Point(self.x2+3, self.y2+3)]}

        self.second_mouseline.sigRegionChangeFinished.disconnect(self.moved_second_graph)
        self.mouseline.sigRegionChangeFinished.disconnect(self.send_moved_data)
        self.mouseline.setState(state)
        self.second_mouseline.setState(self.state_for_second)
        self.mouseline.sigRegionChangeFinished.connect(self.send_moved_data)
        self.second_mouseline.sigRegionChangeFinished.connect(self.moved_second_graph)

        # self._plot_wdg.getPlotItem().clear()     let it be there
        # self._plot_wdg.getPlotItem().plot().setData(x=self.xdata, y=np.sin(self.xdata) * 2) old sin graph

    # def send_data(self):
    #     self._data_model.acquiring_data(self.crdn)

    def send_moved_data(self):
        if not self.flag_point:
            self.points_data = self.mouseline.getState()  # here, we get an array, which has multiple elements,
            self.p1 = self.points_data['pos'][0] + self.x1     # but only pos is needed
            self.p2 = self.points_data['pos'][1] + self.y1
            self.p3 = self.points_data['pos'][0] + self.x2
            self.p4 = self.points_data['pos'][1] + self.y2

            self.updated_data = [self.p1, self.p2, self.p3, self.p4]
            self.flag_point = True
            self._data_model.moved_data_acquiring(self.updated_data)
            self.flag_point = False

    def catch_up_movement(self):

        self.points_data_second = self.second_mouseline.getState()
        if not ((self.points_data_second['pos'][0] == 0 and self.points_data_second['pos'][1] == 0) or (
                self.points_data_second['pos'][0] == self.temp['pos'][0] and self.points_data_second['pos'][1] == self.temp['pos'][1])):
            c1 = self.points_data_second['pos'][0] + self.points_data['pos'][0] + self.x1 + 3
            c2 = self.points_data_second['pos'][1] + self.points_data['pos'][1] + self.y1 + 3
            c3 = self.points_data_second['pos'][0] + self.points_data['pos'][0] + self.x2 + 3
            c4 = self.points_data_second['pos'][1] + self.points_data['pos'][1] + self.y2 + 3
            self.temp = self.points_data_second
        else:
            c1 = self.temp['pos'][0] + self.points_data['pos'][0] + self.x1 + 3
            c2 = self.temp['pos'][1] + self.points_data['pos'][1] + self.y1 + 3
            c3 = self.temp['pos'][0] + self.points_data['pos'][0] + self.x2 + 3
            c4 = self.temp['pos'][1] + self.points_data['pos'][1] + self.y2 + 3
        # self.temp = self.points_data_second

        # if not self.temp == self.moved_data_second:
        #     self.points_data_second = self.moved_data_second
        #     self.temp = self.moved_data_second
        # else:
        #     self.points_data_second = self.second_mouseline.getState()
        print(self.points_data_second)
        # print(self.second_mouseline.getState())
        # print(self.points_data_second['points'])
        # print(self.points_data_second['points'][1][1])

        # c1 = self.points_data_second['pos'][0] + self.points_data['pos'][0] + self.x1 + 3 #- self.temp[0]
        # c2 = self.points_data_second['pos'][1] + self.points_data['pos'][1] + self.y1 + 3 #- self.temp[1]
        # c3 = self.points_data_second['pos'][0] + self.points_data['pos'][0] + self.x2 + 3 #- self.temp[0]
        # c4 = self.points_data_second['pos'][1] + self.points_data['pos'][1] + self.y2 + 3 #- self.temp[1]
        # self.temp[0] = self.points_data['pos'][0]
        # self.temp[1] = self.points_data['pos'][1]

        self.state_for_second = {'pos': Point(0.000000, 0.000000), 'size': Point(1.000000, 1.000000), 'angle': 0.0,
                                 'points': [Point(c1, c2), Point(c3, c4)]}

        self.second_mouseline.sigRegionChangeFinished.disconnect(self.moved_second_graph)
        self.second_mouseline.setState(self.state_for_second)
        self.second_mouseline.sigRegionChangeFinished.connect(self.moved_second_graph)

    def position_for_second(self):
        data = self.second_mouseline.getState()
        print(data)
        return data

    def moved_second_graph(self):
        self.moved_data_second = self.position_for_second()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = Viewer()
    data_model = DataModel()
    view.set_data_model(data_model)
    view.show()
    sys.exit(app.exec_())
