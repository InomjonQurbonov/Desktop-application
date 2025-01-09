import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QWidget
from PyQt5.QtCore import QTimer
import psutil
import sqlite3
from datetime import datetime

class SystemMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        print("QTimer создан")  
        self.recording = False
        self.start_time = None
        self.init_ui()
        print("Интерфейс инициализирован") 

    def init_ui(self):
        self.setWindowTitle("Монитор нагрузки системы")
        font = self.font()
        font.setFamily("Arial")
        self.setFont(font)

        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()

        self.cpu_label = QLabel("ЦП: 0%")
        self.ram_label = QLabel("ОЗУ: 0%")
        self.disk_label = QLabel("ПЗУ: 0%")
        self.time_label = QLabel("Время записи: 0s")

        self.start_button = QPushButton("Начать запись")
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button = QPushButton("Остановить запись")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.hide()

        self.layout.addWidget(self.cpu_label)
        self.layout.addWidget(self.ram_label)
        self.layout.addWidget(self.disk_label)
        self.layout.addWidget(self.time_label)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)
        print("Таймер запущен с интервалом 1 секунда") 

    def update_metrics(self):
        cpu, ram, disk = self.get_system_load()
        print(f"Получены данные: ЦП={cpu}%, ОЗУ={ram}%, ПЗУ={disk}%")  
        self.cpu_label.setText(f"ЦП: {cpu}%")
        self.ram_label.setText(f"ОЗУ: {ram}%")
        self.disk_label.setText(f"ПЗУ: {disk}%")
        
        if self.recording:
            elapsed = (datetime.now() - self.start_time).seconds
            self.time_label.setText(f"Время записи: {elapsed}s")
            print(f"Время записи: {elapsed} секунд") 
            self.save_to_db(cpu, ram, disk)

    def get_system_load(self):
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        print(f"Системная нагрузка: ЦП={cpu}, ОЗУ={ram}, ПЗУ={disk}")  
        return cpu, ram, disk

    def start_recording(self):
        self.start_button.hide()
        self.stop_button.show()
        self.recording = True
        self.start_time = datetime.now()
        print("Запись начата")  
        self.init_db()

    def stop_recording(self):
        self.start_button.show()
        self.stop_button.hide()
        self.recording = False
        self.time_label.setText("Время записи: 0s")
        print("Запись остановлена")  

    def init_db(self):
        conn = sqlite3.connect('system_load.db')
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS load_data (
                timestamp TEXT,
                cpu_load REAL,
                ram_load REAL,
                disk_load REAL
            )
        """)
        conn.commit()
        conn.close()
        print("База данных инициализирована или уже существует")  

    def save_to_db(self, cpu, ram, disk):
        conn = sqlite3.connect('system_load.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO load_data VALUES (?, ?, ?, ?)",
                       (datetime.now(), cpu, ram, disk))
        conn.commit()
        conn.close()
        print(f"Данные сохранены в БД: ЦП={cpu}, ОЗУ={ram}, ПЗУ={disk}") 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemMonitor()
    print("Приложение запущено") 
    window.show()
    sys.exit(app.exec_())
