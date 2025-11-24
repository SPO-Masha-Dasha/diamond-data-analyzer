from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QTableWidget, QTableWidgetItem,
                             QPushButton, QHeaderView, QTabWidget, QTextEdit)
from PyQt5.QtCore import Qt
import pandas as pd
import numpy as np


class StatTab(QWidget):
    def __init__(self):
        super().__init__()
        self.df = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Статистика данных")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Кнопка обновления
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить статистику")
        self.refresh_btn.clicked.connect(self.update_stats)
        btn_layout.addWidget(self.refresh_btn)

        # Кнопка экспорта
        self.export_btn = QPushButton("Экспорт в CSV")
        self.export_btn.clicked.connect(self.export_stats)
        btn_layout.addWidget(self.export_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Создаем вкладки для разных видов статистики
        self.tabs = QTabWidget()

        # Вкладка основной статистики
        self.stats_tab = QWidget()
        stats_layout = QVBoxLayout(self.stats_tab)
        self.stats_table = QTableWidget()
        stats_layout.addWidget(self.stats_table)

        # Вкладка информации о данных
        self.info_tab = QWidget()
        info_layout = QVBoxLayout(self.info_tab)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)

        # Вкладка пропущенных значений
        self.missing_tab = QWidget()
        missing_layout = QVBoxLayout(self.missing_tab)
        self.missing_table = QTableWidget()
        missing_layout.addWidget(self.missing_table)

        # Вкладка уникальных значений
        self.unique_tab = QWidget()
        unique_layout = QVBoxLayout(self.unique_tab)
        self.unique_text = QTextEdit()
        self.unique_text.setReadOnly(True)
        unique_layout.addWidget(self.unique_text)

        self.tabs.addTab(self.stats_tab, "📈 Основная статистика")
        self.tabs.addTab(self.info_tab, "ℹ️ Информация о данных")
        self.tabs.addTab(self.missing_tab, "❓ Пропущенные значения")
        self.tabs.addTab(self.unique_tab, "🔍 Уникальные значения")

        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def update_data(self, df):
        self.df = df
        self.update_stats()

    def update_stats(self):
        if self.df is not None:
            try:
                self.update_basic_stats()
                self.update_info()
                self.update_missing()
                self.update_unique()
            except Exception as e:
                print(f"Ошибка обновления статистики: {e}")

    def update_basic_stats(self):
        # Получаем статистику для числовых колонок
        numeric_stats = self.df.describe(include=[np.number])

        # Добавляем медиану и моду для категориальных
        categorical_stats = self.df.describe(include=['object'])

        # Объединяем статистики
        stats = pd.concat([numeric_stats, categorical_stats], axis=1)

        # Настраиваем таблицу
        self.stats_table.setRowCount(stats.shape[0])
        self.stats_table.setColumnCount(stats.shape[1])

        # Заголовки столбцов
        self.stats_table.setHorizontalHeaderLabels(stats.columns)

        # Заголовки строк
        self.stats_table.setVerticalHeaderLabels(stats.index)

        # Заполняем данные
        for i in range(stats.shape[0]):
            for j in range(stats.shape[1]):
                value = stats.iloc[i, j]
                if pd.isna(value):
                    item = QTableWidgetItem("N/A")
                else:
                    if isinstance(value, (int, float)):
                        display_value = f"{value:.2f}" if abs(value) >= 0.01 else f"{value:.4f}"
                    else:
                        display_value = str(value)
                    item = QTableWidgetItem(display_value)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.stats_table.setItem(i, j, item)

        # Автоматическое растягивание столбцов
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def update_info(self):
        info_text = f"📊 ОБЩАЯ ИНФОРМАЦИЯ О ДАННЫХ\n\n"
        info_text += f"• Размер данных: {self.df.shape[0]} строк, {self.df.shape[1]} столбцов\n"
        info_text += f"• Объем памяти: {self.df.memory_usage(deep=True).sum() / 1024:.1f} KB\n\n"

        info_text += "📋 ТИПЫ ДАННЫХ:\n"
        dtype_counts = self.df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            info_text += f"• {dtype}: {count} колонок\n"

        info_text += "\n🔢 ДЕТАЛИ ПО КОЛОНКАМ:\n"
        for col in self.df.columns:
            info_text += f"• {col}: {self.df[col].dtype}\n"

        self.info_text.setText(info_text)

    def update_missing(self):
        # Считаем пропущенные значения
        missing = self.df.isnull().sum()
        missing_percent = (missing / len(self.df)) * 100

        # Создаем таблицу
        self.missing_table.setRowCount(len(missing))
        self.missing_table.setColumnCount(3)
        self.missing_table.setHorizontalHeaderLabels(["Колонка", "Пропущено", "%"])

        # Заполняем данные
        for i, (col, count) in enumerate(missing.items()):
            self.missing_table.setItem(i, 0, QTableWidgetItem(col))
            self.missing_table.setItem(i, 1, QTableWidgetItem(str(count)))
            self.missing_table.setItem(i, 2, QTableWidgetItem(f"{missing_percent[col]:.2f}%"))

        self.missing_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Подсветка проблемных колонок
        for i in range(len(missing)):
            if missing_percent.iloc[i] > 5:  # Более 5% пропусков
                for j in range(3):
                    if self.missing_table.item(i, j):
                        self.missing_table.item(i, j).setBackground(Qt.yellow)

    def update_unique(self):
        unique_text = "🎯 УНИКАЛЬНЫЕ ЗНАЧЕНИЯ ПО КОЛОНКАМ:\n\n"

        for col in self.df.columns:
            unique_count = self.df[col].nunique()
            unique_text += f"• {col}: {unique_count} уникальных значений"

            if unique_count <= 10:  # Показываем значения если их немного
                unique_values = self.df[col].unique()
                unique_text += f" → {list(unique_values)}\n"
            else:
                unique_text += f" (первые 5: {list(self.df[col].unique()[:5])}...)\n"

        self.unique_text.setText(unique_text)

    def export_stats(self):
        if self.df is not None:
            try:
                # Экспортируем основную статистику
                stats = self.df.describe(include='all')
                stats.to_csv('diamond_statistics.csv')
                self.info_text.append("\n✅ Статистика экспортирована в diamond_statistics.csv")
            except Exception as e:
                self.info_text.append(f"\n❌ Ошибка экспорта: {str(e)}")