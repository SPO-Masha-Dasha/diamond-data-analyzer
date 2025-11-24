from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QPushButton, 
                           QHBoxLayout, QLabel)
from PyQt5.QtCore import QDateTime

class LogTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Лог действий")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Очистить лог")
        clear_btn.clicked.connect(self.clear_log)
        btn_layout.addWidget(clear_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Текстовое поле для лога
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        self.setLayout(layout)
        
        # Добавляем первое сообщение
        self.add_log("🚀 Приложение запущено")
    
    def add_log(self, message):
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def clear_log(self):
        self.log_text.clear()
        self.add_log("📝 Лог очищен")