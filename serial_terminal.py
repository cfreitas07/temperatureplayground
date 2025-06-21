import sys
import serial
import serial.tools.list_ports
import re
from datetime import datetime
from collections import deque
from statistics import mean
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QComboBox, QPushButton, QLabel, QFrame, QGridLayout, QFileDialog, QLineEdit)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import csv
import os
from scipy.interpolate import make_interp_spline
import numpy as np

class TemperaturePlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        self.temps = []
        self.seconds = []
        self.axes.set_title('Temperature History')
        self.axes.set_xlabel('Sample #')
        self.axes.set_ylabel('°C')
        self.axes.grid(True)
        self.line, = self.axes.plot([], [], color='#00A4E3', linewidth=2)
        self.fig = fig

    def update_plot(self, temp, elapsed_sec=None):
        self.temps.append(temp)
        if elapsed_sec is not None:
            self.seconds.append(elapsed_sec)
            self.line.set_data(self.seconds, self.temps)
            self.axes.set_xlim(0, max(20, int(self.seconds[-1]) + 1))
            # Dynamic x-tick interval
            max_sec = int(self.seconds[-1]) if self.seconds else 0
            if max_sec <= 120:
                tick_interval = 10
            elif max_sec <= 300:
                tick_interval = 30
            elif max_sec <= 600:
                tick_interval = 60
            else:
                tick_interval = 120
            self.axes.set_xticks(list(range(0, max_sec + tick_interval, tick_interval)))
            self.axes.set_xticklabels([str(x) for x in range(0, max_sec + tick_interval, tick_interval)])
            if self.temps:
                min_temp = min(self.temps)
                max_temp = max(self.temps)
                if min_temp == max_temp:
                    min_temp -= 1
                    max_temp += 1
                self.axes.set_ylim(min_temp-1, max_temp+1)
            self.draw()
        else:
            self.line.set_data(range(len(self.temps)), self.temps)
            self.axes.set_xlim(0, max(20, len(self.temps)))
            self.axes.set_xticks([])
            if self.temps:
                min_temp = min(self.temps)
                max_temp = max(self.temps)
                if min_temp == max_temp:
                    min_temp -= 1
                    max_temp += 1
                self.axes.set_ylim(min_temp-1, max_temp+1)
            self.draw()

    def clear_plot(self):
        self.temps = []
        self.seconds = []
        self.line.set_data([], [])
        self.axes.set_xlim(0, 20)
        self.axes.set_ylim(0, 50)
        self.draw()

    def plot_full_data(self, times, temps, save_path=None):
        self.axes.clear()
        self.axes.set_title('Collected Temperature Data')
        self.axes.set_xlabel('Time')
        self.axes.set_ylabel('°C')
        self.axes.grid(True)
        self.axes.plot(range(len(temps)), temps, color='#00A4E3', linewidth=2)
        self.axes.set_xlim(0, max(20, len(temps)))
        if temps:
            min_temp = min(temps)
            max_temp = max(temps)
            if min_temp == max_temp:
                min_temp -= 1
                max_temp += 1
            self.axes.set_ylim(min_temp-1, max_temp+1)
        self.fig.tight_layout()
        self.draw()
        if save_path:
            self.fig.savefig(save_path)

class SerialTerminal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.temp_buffer = deque(maxlen=10)
        self.last_valid_temp = None
        self.collecting = False
        self.collected_times = []
        self.collected_temps = []
        self.collected_seconds = []
        self.calibration_offset = 0.0
        self.collection_start_time = None
        self.temp_display_c = None  # Celsius display
        self.temp_display_f = None  # Fahrenheit display
        self.initUI()
        # Maximize window on launch
        self.showMaximized()
        
    def initUI(self):
        self.setWindowTitle('Temperature Playground')
        self.setGeometry(100, 100, 1100, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #333333;
            }
            QPushButton {
                background-color: #00A4E3;  /* Microchip Blue */
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton#startBtn {
                background-color: #43A047; /* Green */
            }
            QPushButton#startBtn:disabled {
                background-color: #A5D6A7;
                color: #e0e0e0;
            }
            QPushButton#startBtn:hover:!disabled {
                background-color: #388E3C;
            }
            QPushButton#startBtn:pressed {
                background-color: #2E7D32;
            }
            QPushButton#stopBtn {
                background-color: #FF7043; /* Softer, more readable red */
                color: #fff;
            }
            QPushButton#stopBtn:disabled {
                background-color: #FFCCBC;
                color: #e0e0e0;
            }
            QPushButton#stopBtn:hover:!disabled {
                background-color: #FF5722;
            }
            QPushButton#stopBtn:pressed {
                background-color: #E64A19;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #00A4E3;  # Microchip Blue
                border-radius: 8px;
                padding: 15px;
            }
            QLabel {
                color: white;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        title_label = QLabel('Temperature Playground')
        title_label.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label = QLabel('2025 Configurable Logic Design Challenge')
        subtitle_label.setFont(QFont('Arial', 14))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Fun, encouraging subtitle for students
        fun_label = QLabel('Author: Claudio de Freitas')
        fun_label.setFont(QFont('Arial', 13, QFont.Weight.Bold))
        fun_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addWidget(fun_label)
        main_layout.addWidget(header_frame)
        
        # Control panel
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #E0E0E0;
            }
        """)
        control_layout = QGridLayout(control_frame)
        control_layout.setSpacing(15)
        control_layout.addWidget(QLabel('Serial Port:'), 0, 0)
        self.port_combo = QComboBox()
        self.refresh_ports()
        control_layout.addWidget(self.port_combo, 0, 1)
        control_layout.addWidget(QLabel('Baud Rate:'), 0, 2)
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        self.baud_combo.setCurrentText('9600')
        control_layout.addWidget(self.baud_combo, 0, 3)
        control_layout.addWidget(QLabel('Calibration Offset (°C):'), 0, 4)
        self.calib_input = QLineEdit('0.0')
        self.calib_input.setFixedWidth(60)
        self.calib_input.setToolTip('Enter a calibration offset to match your reference')
        self.calib_input.editingFinished.connect(self.update_calibration)
        control_layout.addWidget(self.calib_input, 0, 5)
        self.connect_btn = QPushButton('Connect')
        self.connect_btn.clicked.connect(self.toggle_connection)
        control_layout.addWidget(self.connect_btn, 0, 6)
        refresh_btn = QPushButton('Refresh Ports')
        refresh_btn.clicked.connect(self.refresh_ports)
        control_layout.addWidget(refresh_btn, 0, 7)
        # Start/Stop buttons
        self.start_btn = QPushButton('Start Collecting')
        self.start_btn.setObjectName('startBtn')
        self.start_btn.clicked.connect(self.start_collecting)
        control_layout.addWidget(self.start_btn, 1, 0, 1, 4)
        self.stop_btn = QPushButton('Stop & Export')
        self.stop_btn.setObjectName('stopBtn')
        self.stop_btn.clicked.connect(self.stop_and_export)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn, 1, 4, 1, 4)
        main_layout.addWidget(control_frame)
        # Main content: temperature + plot
        content_layout = QHBoxLayout()
        # Temperature display frame
        temp_frame = QFrame()
        temp_frame.setStyleSheet("""
            QFrame {
                background-color: #E3F2FD;
                border-radius: 16px;
                padding: 20px;
                border: 2px solid #00A4E3;
                box-shadow: 0 0 16px #B3E5FC;
            }
        """)
        temp_layout = QVBoxLayout(temp_frame)
        temp_layout.setSpacing(10)
        status_layout = QHBoxLayout()
        self.status_label = QLabel('Status: Disconnected')
        self.status_label.setFont(QFont('Arial', 12))
        self.time_label = QLabel()
        self.time_label.setFont(QFont('Arial', 12))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.time_label)
        temp_layout.addLayout(status_layout)
        
        # Temperature displays in a horizontal layout
        temp_displays_layout = QHBoxLayout()
        
        # Celsius display
        celsius_frame = QFrame()
        celsius_frame.setStyleSheet("""
            QFrame {
                background-color: #E8F5E8;
                border-radius: 12px;
                padding: 15px;
                border: 2px solid #4CAF50;
            }
        """)
        celsius_layout = QVBoxLayout(celsius_frame)
        celsius_title = QLabel('Celsius')
        celsius_title.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        celsius_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        celsius_title.setStyleSheet('color: #2E7D32;')
        celsius_layout.addWidget(celsius_title)
        
        self.temp_display_c = QLabel('--.-')
        self.temp_display_c.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temp_display_c.setFont(QFont('Arial', 72, QFont.Weight.Bold))
        self.temp_display_c.setStyleSheet('QLabel { color: #2E7D32; }')
        celsius_layout.addWidget(self.temp_display_c)
        
        celsius_unit = QLabel('°C')
        celsius_unit.setFont(QFont('Arial', 36))
        celsius_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        celsius_unit.setStyleSheet('color: #2E7D32;')
        celsius_layout.addWidget(celsius_unit)
        
        temp_displays_layout.addWidget(celsius_frame)
        
        # Fahrenheit display
        fahrenheit_frame = QFrame()
        fahrenheit_frame.setStyleSheet("""
            QFrame {
                background-color: #FFF3E0;
                border-radius: 12px;
                padding: 15px;
                border: 2px solid #FF9800;
            }
        """)
        fahrenheit_layout = QVBoxLayout(fahrenheit_frame)
        fahrenheit_title = QLabel('Fahrenheit')
        fahrenheit_title.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        fahrenheit_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fahrenheit_title.setStyleSheet('color: #E65100;')
        fahrenheit_layout.addWidget(fahrenheit_title)
        
        self.temp_display_f = QLabel('--.-')
        self.temp_display_f.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temp_display_f.setFont(QFont('Arial', 72, QFont.Weight.Bold))
        self.temp_display_f.setStyleSheet('QLabel { color: #E65100; }')
        fahrenheit_layout.addWidget(self.temp_display_f)
        
        fahrenheit_unit = QLabel('°F')
        fahrenheit_unit.setFont(QFont('Arial', 36))
        fahrenheit_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fahrenheit_unit.setStyleSheet('color: #E65100;')
        fahrenheit_layout.addWidget(fahrenheit_unit)
        
        temp_displays_layout.addWidget(fahrenheit_frame)
        
        temp_layout.addLayout(temp_displays_layout)
        content_layout.addWidget(temp_frame, 2)
        # Temperature plot
        self.temp_plot = TemperaturePlotCanvas(width=5, height=4, dpi=100)
        self.plot_frame = QFrame()
        self.plot_frame.setStyleSheet("""
            QFrame {
                background-color: #fff;
                border-radius: 16px;
                padding: 10px;
                border: 2px solid #B3E5FC;
            }
        """)
        plot_layout = QVBoxLayout(self.plot_frame)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.addWidget(self.temp_plot)
        content_layout.addWidget(self.plot_frame, 3)
        main_layout.addLayout(content_layout)
        # Dedicated area for the final picture (always visible, below plot)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFixedHeight(400)
        self.image_label.setStyleSheet('background: #fff; border: 1px solid #E0E0E0; border-radius: 8px;')
        self.image_label.setVisible(False)
        main_layout.addWidget(self.image_label)
        # Timers
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial)
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_time)
        self.clock_timer.start(1000)
        self.update_time()
    def update_time(self):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.time_label.setText(f'Time: {current_time}')
    def refresh_ports(self):
        self.port_combo.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo.addItems(ports)
    def toggle_connection(self):
        if self.serial_port is None or not self.serial_port.is_open:
            try:
                self.serial_port = serial.Serial(
                    port=self.port_combo.currentText(),
                    baudrate=int(self.baud_combo.currentText()),
                    timeout=0.1
                )
                self.connect_btn.setText('Disconnect')
                self.timer.start(50)
                self.status_label.setText('Status: Connected')
                self.status_label.setStyleSheet('color: #4CAF50;')
                self.temp_buffer.clear()
                self.last_valid_temp = None
                self.collected_times.clear()
                self.collected_temps.clear()
                self.collected_seconds.clear()
                self.collecting = False
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.image_label.setVisible(False)
            except Exception as e:
                self.status_label.setText(f'Error: {str(e)}')
                self.status_label.setStyleSheet('color: #F44336;')
        else:
            self.serial_port.close()
            self.timer.stop()
            self.connect_btn.setText('Connect')
            self.status_label.setText('Status: Disconnected')
            self.status_label.setStyleSheet('color: #F44336;')
            self.temp_display_c.setText('--.-')
            self.temp_display_f.setText('--.-')
            self.temp_plot.clear_plot()
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            self.image_label.setVisible(False)
    def is_valid_temperature(self, temp):
        return -40 <= temp <= 125
    def start_collecting(self):
        self.collected_times.clear()
        self.collected_temps.clear()
        self.collected_seconds.clear()
        self.collecting = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.image_label.setVisible(False)
        # Clear the plot for new session
        self.temp_plot.axes.clear()
        self.temp_plot.axes.set_title('Temperature History')
        self.temp_plot.axes.set_xlabel('Seconds')
        self.temp_plot.axes.set_ylabel('°C')
        self.temp_plot.axes.grid(True)
        self.temp_plot.line, = self.temp_plot.axes.plot([], [], color='#00A4E3', linewidth=2)
        self.temp_plot.clear_plot()
        self.collection_start_time = datetime.now()
        # Add a blue glow to the plot area during collection
        self.plot_frame.setStyleSheet("""
            QFrame {
                background-color: #fff;
                border-radius: 16px;
                padding: 10px;
                border: 2px solid #00A4E3;
                box-shadow: 0 0 24px #00A4E3;
            }
        """)
    def update_calibration(self):
        try:
            self.calibration_offset = float(self.calib_input.text())
        except ValueError:
            self.calibration_offset = 0.0
            self.calib_input.setText('0.0')
    def stop_and_export(self):
        self.collecting = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        if not self.collected_times or not self.collected_temps or not hasattr(self, 'collected_seconds'):
            return
        # Export to CSV
        default_name = f"temperature_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        save_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", default_name, "CSV Files (*.csv)")
        if save_path:
            with open(save_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Seconds', 'Temperature (°C)', 'Temperature (°F)', 'Timestamp'])
                for sec, temp, t in zip(self.collected_seconds, self.collected_temps, self.collected_times):
                    writer.writerow([sec, temp, temp * 1.8 + 32, t])
        # Remove the blue glow from the plot area after collection
        self.plot_frame.setStyleSheet("""
            QFrame {
                background-color: #fff;
                border-radius: 16px;
                padding: 10px;
                border: 2px solid #B3E5FC;
            }
        """)
        self.image_label.clear()
        self.image_label.setVisible(False)
    def read_serial(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                while self.serial_port.in_waiting:
                    line = self.serial_port.readline()
                    try:
                        text = line.decode('ascii', errors='replace').strip()
                        temp_pattern = r'(?:temp:?\s*)?(-?\d+\.?\d*)(?:\s*°?[Cc])?'
                        matches = re.findall(temp_pattern, text)
                        if matches:
                            temp = float(matches[-1])
                            if self.is_valid_temperature(temp):
                                calibrated_temp = temp + self.calibration_offset
                                self.temp_display_c.setText(f'{calibrated_temp:.2f}')
                                self.temp_display_f.setText(f'{calibrated_temp * 1.8 + 32:.2f}')
                                self.last_valid_temp = calibrated_temp
                                # Optional: keep smoothing for the plot only
                                self.temp_buffer.append(calibrated_temp)
                                if self.collecting:
                                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    self.collected_times.append(now)
                                    self.collected_temps.append(calibrated_temp)
                                    elapsed_sec = (datetime.strptime(now, '%Y-%m-%d %H:%M:%S') - self.collection_start_time).total_seconds()
                                    self.collected_seconds.append(round(elapsed_sec, 2))
                                    self.temp_plot.update_plot(mean(self.temp_buffer), elapsed_sec=round(elapsed_sec, 2))
                    except Exception:
                        pass
            except Exception as e:
                self.status_label.setText(f'Error: {str(e)}')
                self.status_label.setStyleSheet('color: #F44336;')
                self.toggle_connection()
    def closeEvent(self, event):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        event.accept()
if __name__ == '__main__':
    import matplotlib
    matplotlib.use('Qt5Agg')
    app = QApplication(sys.argv)
    terminal = SerialTerminal()
    terminal.show()
    sys.exit(app.exec()) 