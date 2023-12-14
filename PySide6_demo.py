import sys
import requests
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QScatterSeries, QDateTimeAxis, QValueAxis
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPainter, QColor

print("Pyside6_demo v0.1.1")
print("Launch the API program in your terminal.")
print("After launching, execute the program by pressing the 'Load Data' button.")


class DataVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.detections = {}
        self.initUI()

    def initUI(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        self.load_button = QPushButton('Load Data')
        self.load_button.clicked.connect(self.load_data)
        self.layout.addWidget(self.load_button)
        self.load_button.setFixedSize(100, 40)

        self.chart = QChart()
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.layout.addWidget(self.chart_view)

        self.alert_text_box = QTextEdit()
        self.alert_text_box.setReadOnly(True)
        self.alert_text_box.setFixedHeight(150)
        self.layout.addWidget(self.alert_text_box)

        self.setGeometry(620, 310, 1280, 720)
        self.setWindowTitle('Data Visualization')

    def load_data(self):
        print("Calling API to get detections data...")
        detections_response = requests.get(
            'http://localhost:3000/api/v0.1.2/detections')
        self.detections = detections_response.json()
        print("Detections data loaded.")

        print("Calling API to get collecteds data...")
        collecteds_response = requests.get(
            'http://localhost:3000/api/v0.1.2/collecteds')
        collecteds_data = collecteds_response.json()
        print("Collecteds data loaded.")
        print(collecteds_data)
        self.update_chart(collecteds_data)

    def update_chart(self, data):
        self.chart = QChart()
        self.chart_view.setChart(self.chart)

        axisX = QDateTimeAxis()
        axisX.setFormat("HH:mm:ss")
        axisX.setTitleText("Time")
        self.chart.addAxis(axisX, Qt.AlignBottom)

        axisY = QValueAxis()
        axisY.setTitleText("Value")
        self.chart.addAxis(axisY, Qt.AlignLeft)

        alert_values = []

        for register, values in data.items():
            series = QLineSeries()
            series.setName("Data")
            scatter_series = QScatterSeries()
            scatter_series.setName("Detection Points")
            scatter_series.setMarkerSize(10.0)

            max_threshold = None
            min_threshold = None

            if register in self.detections:
                detection = self.detections[register]
                if 'max' in detection:
                    max_threshold = detection['max']['threshold']
                if 'min' in detection:
                    min_threshold = detection['min']['threshold']

            for i, y in enumerate(values['y_axis_labels']):
                if i < len(values['x_axis_labels']):
                    time_str = values['x_axis_labels'][i]
                    time = QDateTime.fromString(
                        f"2023-01-01T{time_str}", "yyyy-MM-ddTHH:mm:ss")
                    series.append(time.toMSecsSinceEpoch(), y)

                    if register in self.detections:
                        detection = self.detections[register]
                        if (('max' in detection and detection['max']['condition'] == 'below' and y > detection['max']['threshold']) or
                                ('min' in detection and detection['min']['condition'] == 'above' and y < detection['min']['threshold'])):
                            scatter_series.append(time.toMSecsSinceEpoch(), y)
                            alert_values.append((time_str, y))

            self.chart.addSeries(series)
            series.attachAxis(axisX)
            series.attachAxis(axisY)
            self.chart.addSeries(scatter_series)
            scatter_series.attachAxis(axisX)
            scatter_series.attachAxis(axisY)

        if max_threshold is not None:
            self.add_alert_line(max_threshold, axisX, axisY, "max")
        if min_threshold is not None:
            self.add_alert_line(min_threshold, axisX, axisY, "min")

        alert_text = "Alert Values:\n"
        for time_str, value in alert_values:
            alert_text += f"Time: {time_str}, Value: {value}\n"
        self.alert_text_box.setText(alert_text)

        self.chart.legend().show()
        self.chart.setTitle(f'Data Visualization - {register}')

    def add_alert_line(self, threshold, axisX, axisY, line_type):
        alert_line = QLineSeries()
        alert_line.setName(f"{line_type.capitalize()} Threshold")

        if line_type == "max":
            alert_line.setColor(QColor("red"))
        elif line_type == "min":
            alert_line.setColor(QColor("blue"))

        start_time = QDateTime.fromString(
            f"2023-01-01T00:00:00", "yyyy-MM-ddTHH:mm:ss")
        end_time = QDateTime.fromString(
            f"2023-01-01T23:59:59", "yyyy-MM-ddTHH:mm:ss")
        alert_line.append(start_time.toMSecsSinceEpoch(), threshold)
        alert_line.append(end_time.toMSecsSinceEpoch(), threshold)

        self.chart.addSeries(alert_line)
        alert_line.attachAxis(axisX)
        alert_line.attachAxis(axisY)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DataVisualizer()
    ex.show()
    sys.exit(app.exec())
