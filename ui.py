import subprocess
import threading
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QTextEdit, QHBoxLayout, QGroupBox, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QTextCursor

class ZwiftUI(QWidget):
    def __init__(self):
        super().__init__()
        self.process = None
        self.battery_level = None
        self.zwift_mac = None
        self.zwift_status = "Not Connected"
        self.setup_ui()
        self.update_battery_display()
        self.update_zwift_status_display()
        self.update_zwift_mac_display()

    def setup_ui(self):
        self.setWindowTitle("Zwift Click Handler")
        self.setGeometry(100, 100, 350, 400)

        layout = QVBoxLayout()

        # Info Group Box
        info_group = QGroupBox("Info")
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.status_label = QLabel("Service Status: Not Running")
        info_layout.addWidget(self.status_label)

        self.battery_label = QLabel("")
        info_layout.addWidget(self.battery_label)

        self.zwift_status_label = QLabel(f"Zwift Click Status: {self.zwift_status}")
        info_layout.addWidget(self.zwift_status_label)

        self.zwift_mac_label = QLabel("Zwift Click MAC Address: Not Available")
        info_layout.addWidget(self.zwift_mac_label)

        # Plus Button Status
        plus_layout = QHBoxLayout()
        plus_label = QLabel("Plus Button:")
        self.plus_status = QFrame()
        self.plus_status.setFixedSize(25, 25)
        self.plus_status.setStyleSheet("""
            background-color: none;
            border-top: 1px solid #fff;
            border-right: 1px solid #fff;
            border-bottom: 1px solid #fff;
            border-left: 1px solid #fff;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            border-bottom-left-radius: 0;
            border-bottom-right-radius: 0;
        """)
        plus_layout.addWidget(plus_label)
        plus_layout.addWidget(self.plus_status)
        info_layout.addLayout(plus_layout)

        # Minus Button Status
        minus_layout = QHBoxLayout()
        minus_label = QLabel("Minus Button:")
        self.minus_status = QFrame()
        self.minus_status.setFixedSize(25, 25)
        self.minus_status.setStyleSheet("""
            background-color: none;
            border-top: 1px solid #fff;
            border-right: 1px solid #fff;
            border-bottom: 1px solid #fff;
            border-left: 1px solid #fff;
            border-top-left-radius: 0;
            border-top-right-radius: 0;
            border-bottom-left-radius: 10px;
            border-bottom-right-radius: 10px;
        """)
        minus_layout.addWidget(minus_label)
        minus_layout.addWidget(self.minus_status)
        info_layout.addLayout(minus_layout)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        button_layout = QHBoxLayout()

        self.start_button = QPushButton("Start Service")
        self.start_button.clicked.connect(self.start_service)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Service")
        self.stop_button.clicked.connect(self.stop_service)
        self.stop_button.setDisabled(True)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)

        self.view_details_button = QPushButton("View Details")
        self.view_details_button.clicked.connect(self.toggle_log_display)
        self.view_details_button.setStyleSheet("QPushButton { background: none; border: none; color: blue; text-decoration: underline; } QPushButton:hover { color: darkblue; }")
        self.view_details_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        layout.addWidget(self.view_details_button)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setVisible(False)
        layout.addWidget(self.log_display)

        self.setLayout(layout)

    def log_message(self, message):
        self.log_display.append(message)
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_display.setTextCursor(cursor)
        with open("log.txt", "a") as log_file:
            log_file.write(message + "\n")

    def start_service(self):
        if self.process is None:
            self.process = subprocess.Popen([sys.executable, "app.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, universal_newlines=True)
            self.status_label.setText("Service Status: Running")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

            self.monitor_thread = threading.Thread(target=self.monitor_process, daemon=True)
            self.monitor_thread.start()

    def stop_service(self):
        if self.process and self.process.poll() is None:
            self.log_message("Stopping service...")
            self.process.terminate()
            self.process.wait()
            self.process = None
            self.status_label.setText("Service Status: Not Running")
            self.log_message("Service stopped.")
            self.start_button.setEnabled(True)
            self.stop_button.setDisabled(True)

    def monitor_process(self):
        if self.process is None:
            return
        for line in iter(self.process.stdout.readline, ""):
            line = line.strip()
            if "Current battery level is" in line:
                try:
                    level_str = line.split("is")[1].split("app.py")[0].strip()
                    self.battery_level = int(level_str)
                    self.update_battery_display()
                except (ValueError, IndexError):
                    pass
            elif "Plus button PRESSED" in line:
                self.plus_status.setStyleSheet("""
                background-color: green;
                border-top: 1px solid #fff;
                border-right: 1px solid #fff;
                border-bottom: 1px solid #fff;
                border-left: 1px solid #fff;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom-left-radius: 0;
                border-bottom-right-radius: 0;
            """)
            elif "Plus button RELEASED" in line:
                self.plus_status.setStyleSheet("""
                background-color: none;
                border-top: 1px solid #fff;
                border-right: 1px solid #fff;
                border-bottom: 1px solid #fff;
                border-left: 1px solid #fff;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom-left-radius: 0;
                border-bottom-right-radius: 0;
            """)
            elif "Minus button PRESSED" in line:
                self.minus_status.setStyleSheet("""
                background-color: green;
                border-top: 1px solid #fff;
                border-right: 1px solid #fff;
                border-bottom: 1px solid #fff;
                border-left: 1px solid #fff;
                border-top-left-radius: 0;
                border-top-right-radius: 0;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            """)
            elif "Minus button RELEASED" in line:
                self.minus_status.setStyleSheet("""
                background-color: none;
                border-top: 1px solid #fff;
                border-right: 1px solid #fff;
                border-bottom: 1px solid #fff;
                border-left: 1px solid #fff;
                border-top-left-radius: 0;
                border-top-right-radius: 0;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            """)
            elif 'Using MAC of "' in line:
                try:
                    self.zwift_mac = line.split('Using MAC of "')[1].split('"')[0].strip()
                    self.zwift_status = "Connected"
                    self.update_zwift_status_display()
                    self.update_zwift_mac_display()
                except IndexError:
                    pass
            elif "Disconnected" in line:
                self.zwift_status = "Not Connected"
                self.zwift_mac = "Not Available"
                self.update_zwift_status_display()
                self.update_zwift_mac_display()

            self.log_message(line)

    def closeEvent(self, event):
        self.stop_service()
        event.accept()

    def toggle_log_display(self):
        self.log_display.setVisible(not self.log_display.isVisible())

    def update_battery_display(self):
        if self.battery_level is not None:
            self.battery_label.setText(f"Battery: {self.battery_level}%")
        else:
            self.battery_label.setText("")

    def update_zwift_status_display(self):
        self.zwift_status_label.setText(f"Zwift Click Status: {self.zwift_status}")

    def update_zwift_mac_display(self):
        if self.zwift_mac:
            self.zwift_mac_label.setText(f"Zwift Click MAC Address: {self.zwift_mac}")
        else:
            self.zwift_mac_label.setText("Zwift Click MAC Address: Not Available")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ZwiftUI()
    window.show()
    sys.exit(app.exec())