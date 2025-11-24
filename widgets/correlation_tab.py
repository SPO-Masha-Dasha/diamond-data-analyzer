from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class CorrelationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.df = None
        self.numeric_columns = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Графики корреляции")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Панель управления
        control_layout = QHBoxLayout()

        control_layout.addWidget(QLabel("Выберите переменные:"))

        # Выпадающий список для выбора переменных
        self.var_combo = QComboBox()
        self.var_combo.setMinimumWidth(200)
        control_layout.addWidget(self.var_combo)

        # Кнопка построения графика
        self.plot_btn = QPushButton("Построить графики")
        self.plot_btn.clicked.connect(self.plot_correlation)
        control_layout.addWidget(self.plot_btn)

        # Кнопка сброса
        self.reset_btn = QPushButton("Сбросить выбор")
        self.reset_btn.clicked.connect(self.reset_selection)
        control_layout.addWidget(self.reset_btn)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # Область для графиков
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Информационная метка
        self.info_label = QLabel("Выберите переменные для построения графиков корреляции")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: gray; font-style: italic; margin: 10px;")
        layout.addWidget(self.info_label)

        self.setLayout(layout)

        # Изначально скрываем кнопки
        self.plot_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)

    def update_data(self, df):
        self.df = df
        if self.df is not None:
            # Получаем только числовые колонки
            self.numeric_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
            self.var_combo.clear()
            self.var_combo.addItems(self.numeric_columns)

            if self.numeric_columns:
                self.plot_btn.setEnabled(True)
                self.reset_btn.setEnabled(True)
                self.info_label.setText(f"Доступно {len(self.numeric_columns)} числовых переменных")
            else:
                self.info_label.setText("Нет числовых переменных для анализа")

    def plot_correlation(self):
        if self.df is None or not self.numeric_columns:
            QMessageBox.warning(self, "Ошибка", "Нет данных для построения графиков")
            return

        selected_var = self.var_combo.currentText()

        try:
            # Очищаем предыдущий график
            self.figure.clear()

            # Создаем subplot
            ax = self.figure.add_subplot(111)

            # Строим pairplot для выбранной переменной со всеми остальными
            numeric_df = self.df[self.numeric_columns]

            # Если выбрана одна переменная, строим корреляции с остальными
            if selected_var:
                # Вычисляем корреляции
                correlations = numeric_df.corr()[selected_var].sort_values(ascending=False)
                correlations = correlations[correlations.index != selected_var]  # Убираем самую с собой

                # Строим барплот корреляций
                bars = ax.barh(range(len(correlations)), correlations.values)
                ax.set_yticks(range(len(correlations)))
                ax.set_yticklabels(correlations.index)
                ax.set_xlabel('Коэффициент корреляции')
                ax.set_title(f'Корреляции переменной "{selected_var}" с другими переменными')

                # Добавляем значения на столбцы
                for i, (bar, value) in enumerate(zip(bars, correlations.values)):
                    ax.text(value + 0.01, i, f'{value:.2f}', va='center')

                self.info_label.setText(f"Показаны корреляции переменной '{selected_var}' с другими переменными")

            self.figure.tight_layout()
            self.canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось построить график: {str(e)}")
            self.info_label.setText(f"Ошибка: {str(e)}")

    def reset_selection(self):
        self.var_combo.setCurrentIndex(0)
        self.figure.clear()
        self.canvas.draw()
        self.info_label.setText("Выберите переменные для построения графиков корреляции")