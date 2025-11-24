from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from scipy import stats


class LinearTab(QWidget):
    def __init__(self):
        super().__init__()
        self.df = None
        self.numeric_columns = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Линейные графики и тренды")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Панель управления
        control_layout = QHBoxLayout()

        control_layout.addWidget(QLabel("Ось X:"))
        self.x_combo = QComboBox()
        self.x_combo.setMinimumWidth(120)
        control_layout.addWidget(self.x_combo)

        control_layout.addWidget(QLabel("Ось Y:"))
        self.y_combo = QComboBox()
        self.y_combo.setMinimumWidth(120)
        control_layout.addWidget(self.y_combo)

        # Чекбокс для линии тренда
        self.trend_check = QCheckBox("Линия тренда")
        self.trend_check.setChecked(True)
        control_layout.addWidget(self.trend_check)

        # Кнопка построения графика
        self.plot_btn = QPushButton("Построить график")
        self.plot_btn.clicked.connect(self.plot_linear)
        control_layout.addWidget(self.plot_btn)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # Вторая панель управления
        control_layout2 = QHBoxLayout()

        # Выбор типа графика
        control_layout2.addWidget(QLabel("Тип графика:"))
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems(['Точечный', 'Линейный', 'Гистограмма X', 'Гистограмма Y'])
        control_layout2.addWidget(self.plot_type_combo)

        control_layout2.addStretch()
        layout.addLayout(control_layout2)

        # Область для графика
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Информационная метка
        self.info_label = QLabel("Выберите переменные для осей X и Y")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: gray; font-style: italic; margin: 10px;")
        layout.addWidget(self.info_label)

        self.setLayout(layout)

    def update_data(self, df):
        self.df = df
        if self.df is not None:
            # Получаем только числовые колонки
            self.numeric_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
            self.x_combo.clear()
            self.y_combo.clear()
            self.x_combo.addItems(self.numeric_columns)
            self.y_combo.addItems(self.numeric_columns)

            if self.numeric_columns:
                # По умолчанию выбираем carat для X и price для Y (самые интересные для diamonds)
                if 'carat' in self.numeric_columns:
                    self.x_combo.setCurrentText('carat')
                if 'price' in self.numeric_columns:
                    self.y_combo.setCurrentText('price')

                self.info_label.setText(f"Доступно {len(self.numeric_columns)} числовых переменных")
            else:
                self.info_label.setText("Нет числовых переменных для анализа")

    def plot_linear(self):
        if self.df is None or not self.numeric_columns:
            QMessageBox.warning(self, "Ошибка", "Нет данных для построения графика")
            return

        x_var = self.x_combo.currentText()
        y_var = self.y_combo.currentText()
        plot_type = self.plot_type_combo.currentText()

        if x_var == y_var and plot_type in ['Точечный', 'Линейный']:
            QMessageBox.warning(self, "Ошибка", "Выберите разные переменные для осей X и Y")
            return

        try:
            # Очищаем предыдущий график
            self.figure.clear()

            # Создаем subplot
            ax = self.figure.add_subplot(111)

            if plot_type == 'Точечный':
                # Точечный график
                ax.scatter(self.df[x_var], self.df[y_var], alpha=0.5, s=10)
                ax.set_xlabel(x_var)
                ax.set_ylabel(y_var)
                ax.set_title(f'Зависимость {y_var} от {x_var}')

                # Добавляем линию тренда если выбрано
                if self.trend_check.isChecked():
                    z = np.polyfit(self.df[x_var], self.df[y_var], 1)
                    p = np.poly1d(z)
                    ax.plot(self.df[x_var], p(self.df[x_var]), "r--", alpha=0.8, linewidth=2,
                            label=f'Тренд (R²={np.corrcoef(self.df[x_var], self.df[y_var])[0, 1] ** 2:.3f})')
                    ax.legend()

                # Вычисляем корреляцию
                correlation = self.df[x_var].corr(self.df[y_var])
                info_text = f"Корреляция между {x_var} и {y_var}: {correlation:.3f}"

            elif plot_type == 'Линейный':
                # Линейный график (сортировка по X)
                sorted_df = self.df.sort_values(by=x_var)
                ax.plot(sorted_df[x_var], sorted_df[y_var], 'b-', alpha=0.7)
                ax.set_xlabel(x_var)
                ax.set_ylabel(y_var)
                ax.set_title(f'Линейный график: {y_var} от {x_var}')
                info_text = f"Линейный график: {y_var} от {x_var}"

            elif plot_type == 'Гистограмма X':
                # Гистограмма для X
                ax.hist(self.df[x_var], bins=30, alpha=0.7, edgecolor='black')
                ax.set_xlabel(x_var)
                ax.set_ylabel('Частота')
                ax.set_title(f'Распределение {x_var}')
                info_text = f"Гистограмма распределения {x_var}"

            elif plot_type == 'Гистограмма Y':
                # Гистограмма для Y
                ax.hist(self.df[y_var], bins=30, alpha=0.7, edgecolor='black')
                ax.set_xlabel(y_var)
                ax.set_ylabel('Частота')
                ax.set_title(f'Распределение {y_var}')
                info_text = f"Гистограмма распределения {y_var}"

            self.figure.tight_layout()
            self.canvas.draw()

            self.info_label.setText(info_text)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось построить график: {str(e)}")
            self.info_label.setText(f"Ошибка: {str(e)}")