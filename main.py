import os
import sys

# Указываем правильный путь к плагинам Qt
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = r'C:\Users\Солнце\AppData\Local\Programs\Python\Python312\Lib\site-packages\PyQt5\Qt5\plugins'

import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, 
                           QWidget, QMessageBox, QFileDialog, QStatusBar)
from PyQt5.QtCore import QTimer

# Импорты наших кастомных вкладок
from widgets.stat_tab import StatTab
from widgets.correlation_tab import CorrelationTab
from widgets.heatmap_tab import HeatmapTab
from widgets.linear_tab import LinearTab
from widgets.log_tab import LogTab

class DiamondApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df = None  # Здесь будут храниться наши данные
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Diamond Data Analyzer')
        self.setGeometry(100, 100, 1200, 800)
        
        # Создаем центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Создаем вкладки
        self.tabs = QTabWidget()
        
        # Создаем экземпляры наших вкладок
        self.stat_tab = StatTab()
        self.correlation_tab = CorrelationTab()
        self.heatmap_tab = HeatmapTab()
        self.linear_tab = LinearTab()
        self.log_tab = LogTab()
        
        # Добавляем вкладки
        self.tabs.addTab(self.stat_tab, "📊 Статистика")
        self.tabs.addTab(self.correlation_tab, "📈 Графики корреляции")
        self.tabs.addTab(self.heatmap_tab, "🎨 Тепловая карта")
        self.tabs.addTab(self.linear_tab, "📉 Линейные графики")
        self.tabs.addTab(self.log_tab, "📝 Лог действий")
        
        layout.addWidget(self.tabs)
        
        # Создаем статус бар
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Готов к работе. Загрузите данные через меню.")
        
        # Создаем меню
        self.createMenu()
        
        # Автозагрузка diamonds.csv если он есть
        QTimer.singleShot(100, self.autoLoadData)
    
    def createMenu(self):
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu('Файл')
        
        load_action = file_menu.addAction('Загрузить данные')
        load_action.triggered.connect(self.loadData)
        
        exit_action = file_menu.addAction('Выход')
        exit_action.triggered.connect(self.close)
    
    def autoLoadData(self):
        """Автоматически загружает diamonds.csv при запуске"""
        if os.path.exists('diamonds.csv'):
            try:
                self.df = pd.read_csv('diamonds.csv')
                self.statusBar.showMessage(f"Данные загружены: {len(self.df)} записей")
                self.log_tab.add_log("✅ Автоматически загружен файл diamonds.csv")
                
                # Передаем данные во все вкладки
                self.updateAllTabs()
                
            except Exception as e:
                self.statusBar.showMessage(f"Ошибка загрузки: {str(e)}")
                self.log_tab.add_log(f"❌ Ошибка загрузки данных: {str(e)}")
    
    def loadData(self):
        """Загрузка данных через диалог выбора файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Выберите файл данных', '', 
            'CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*)'
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.df = pd.read_csv(file_path)
                elif file_path.endswith('.xlsx'):
                    self.df = pd.read_excel(file_path)
                
                self.statusBar.showMessage(f"Данные загружены: {len(self.df)} записей")
                self.log_tab.add_log(f"✅ Загружен файл: {os.path.basename(file_path)}")
                
                # Обновляем все вкладки
                self.updateAllTabs()
                
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить файл: {str(e)}')
                self.log_tab.add_log(f"❌ Ошибка загрузки: {str(e)}")
    
    def updateAllTabs(self):
        """Обновляет все вкладки с новыми данными"""
        if self.df is not None:
            self.stat_tab.update_data(self.df)
            self.correlation_tab.update_data(self.df)
            self.heatmap_tab.update_data(self.df)
            self.linear_tab.update_data(self.df)
            self.log_tab.add_log("📊 Данные обновлены во всех вкладках")

def main():
    app = QApplication(sys.argv)
    
    # Устанавливаем стиль приложения
    app.setStyle('Fusion')
    
    window = DiamondApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()