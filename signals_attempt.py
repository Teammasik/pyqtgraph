import sys
import numpy as np
import pyqtgraph as pg

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QSizePolicy

from data_file import DataModel


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

    def set_data_model(self, dm: DataModel):
        self._data_model = dm

        self._data_model.coordinate_changed.connect(self._on_model_points_changed)

        self._data_model.generate_new_coordinates()

    def _on_button_clicked(self):
        self._data_model.generate_new_coordinates()

    def _on_model_points_changed(self):

        self.crdn = self._data_model.coordinates()
        self.x1 = self.crdn[0]
        self.x2 = self.crdn[1]
        self.y1 = self.crdn[2]
        self.y2 = self.crdn[3]
        self.xdata = self.crdn[4]

        self._plot_wdg.getPlotItem().clear()
        mouseline = pg.LineSegmentROI([[self.x1, self.y1], [self.x2, self.y2]], movable=True, rotatable=False)
        self._plot_wdg.addItem(mouseline)
        self._plot_wdg.getPlotItem().plot().setData(x=self.xdata, y=np.sin(self.xdata) * 2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = Viewer()
    data_model = DataModel()
    view.set_data_model(data_model)
    view.show()
    sys.exit(app.exec_())
