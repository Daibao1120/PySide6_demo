import sys
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                             QWidget, QPushButton, QTextEdit, QCheckBox, QFormLayout, QHBoxLayout,
                             QDateEdit, QLabel)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime


class CustomMatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super(CustomMatplotlibCanvas, self).__init__(self.fig)
        self.setParent(parent)


class DataVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.detections = {}
        self.initUI()

    def initUI(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        # 主水平布局
        hLayout = QHBoxLayout(self.main_widget)

        # 左側容器（用於放置折線圖）
        left_container = QWidget()
        left_vLayout = QVBoxLayout(left_container)

        # 折線圖畫布
        self.canvas = CustomMatplotlibCanvas(
            self.main_widget, width=5, height=10, dpi=100)
        left_vLayout.addWidget(self.canvas)
        left_vLayout.setAlignment(Qt.AlignTop)

        # 將左側容器添加到主水平布局
        hLayout.addWidget(left_container, 1)

        # 右側容器（用於放置日期選擇器、加載數據按鈕、警報文本框和勾選框）
        right_container = QWidget()
        right_vLayout = QVBoxLayout(right_container)

        # 日期選擇器
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Start Date:"))
        self.start_date_input = QDateEdit(self)
        self.start_date_input.setCalendarPopup(True)
        date_layout.addWidget(self.start_date_input)

        date_layout.addWidget(QLabel("End Date:"))
        self.end_date_input = QDateEdit(self)
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())
        date_layout.addWidget(self.end_date_input)
        right_vLayout.addLayout(date_layout)

        # 加載數據按鈕
        self.load_button = QPushButton('Load Data')
        self.load_button.clicked.connect(self.load_data)
        self.load_button.setFixedSize(100, 40)
        right_vLayout.addWidget(self.load_button)

        # 勾選框區域
        self.search_layout = QFormLayout()
        right_vLayout.addLayout(self.search_layout)
        right_vLayout.setAlignment(Qt.AlignTop)

        # 警報文本框
        self.alert_text_box = QTextEdit()
        self.alert_text_box.setReadOnly(True)
        self.alert_text_box.setFixedHeight(150)
        right_vLayout.addWidget(self.alert_text_box)

        # 將右側容器添加到主水平布局
        hLayout.addWidget(left_container, 3)  # 左側的權重增加
        hLayout.addWidget(right_container, 1)  # 右側的權重保持不變
        hLayout.addWidget(right_container, 1)

        self.resize(1280, 768)
        self.setWindowTitle('Data Visualization')

    def load_data(self):
        try:
            detections_response = requests.get(
                'http://localhost:3000/api/v0.1.2/detections')
            self.detections = detections_response.json()

            self.create_checkboxes()

            collecteds_response = requests.get(
                'http://localhost:3000/api/v0.1.2/collecteds')
            self.collecteds_data = collecteds_response.json()

            self.update_chart()
        except requests.RequestException as e:
            self.alert_text_box.setText(f"Error loading data: {e}")

    def create_checkboxes(self):
        self.checkboxes = {}
        for key in self.detections.keys():
            checkbox = QCheckBox(key)
            checkbox.stateChanged.connect(self.update_chart)
            self.checkboxes[key] = checkbox
            self.search_layout.addRow(checkbox)

    def update_chart(self):
        selected_keys = [
            key for key, checkbox in self.checkboxes.items() if checkbox.isChecked()]
        self.display_data(selected_keys)

    def display_data(self, selected_keys):
        self.canvas.ax.clear()
        alert_values = []

        for key in selected_keys:
            if key in self.collecteds_data:
                if 'x_axis_labels' not in self.collecteds_data[key].keys():
                    continue
                dates = [datetime.strptime(d, "%Y/%m/%d %H:%M:%S.%f")
                         for d in self.collecteds_data[key]['x_axis_labels']]
                values = self.collecteds_data[key]['y_axis_labels']

                self.canvas.ax.plot(dates, values, label=f"{key} Data")

                for date, value in zip(dates, values):
                    detection = self.detections.get(key, {})
                    if (('max' in detection and detection['max']['condition'] == 'below' and value > detection['max']['threshold']) or
                            ('min' in detection and detection['min']['condition'] == 'above' and value < detection['min']['threshold'])):
                        self.canvas.ax.scatter(date, value, color='red')
                        alert_values.append(
                            (key, date.strftime("%Y/%m/%d %H:%M:%S"), value))

        self.canvas.ax.legend()
        self.canvas.ax.set_xlabel("Date and Time")
        self.canvas.ax.set_ylabel("Value")
        self.canvas.ax.grid(True)
        self.canvas.draw()

        alert_text = "Alert Values:\n" + \
            "\n".join(
                [f"Key: {k}, Time: {t}, Value: {v}" for k, t, v in alert_values])
        self.alert_text_box.setText(alert_text)


if __name__ == '__main__':
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    ex = DataVisualizer()
    ex.show()
    sys.exit(app.exec())
