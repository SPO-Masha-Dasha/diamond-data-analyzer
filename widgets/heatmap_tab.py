from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QCheckBox, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class HeatmapTab(QWidget):
    def __init__(self):
        super().__init__()
        self.df = None
        self.numeric_columns = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Тепловая карта корреляций")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Панель управления
        control_layout = QHBoxLayout()

        # Выбор цветовой схемы
        control_layout.addWidget(QLabel("Цветовая схема:"))
        self.cmap_combo = QComboBox()
        self.cmap_combo.addItems(['coolwarm', 'viridis', 'plasma', 'RdYlBu', 'Spectral'])
        self.cmap_combo.setCurrentText('coolwarm')
        control_layout.addWidget(self.cmap_combo)

        # Чекбокс для аннотаций
        self.annot_check = QCheckBox("Показать значения")
        self.annot_check.setChecked(True)
        control_layout.addWidget(self.annot_check)

        # Кнопка построения тепловой карты
        self.plot_btn = QPushButton("Построить тепловую карту")
        self.plot_btn.clicked.connect(self.plot_heatmap)
        control_layout.addWidget(self.plot_btn)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # Область для графика
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Информационная метка
        self.info_label = QLabel(
            "Нажмите кнопку для построения тепловой карты корреляций между всеми числовыми переменными")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: gray; font-style: italic; margin: 10px;")
        layout.addWidget(self.info_label)

        self.setLayout(layout)

    def update_data(self, df):
        self.df = df
        if self.df is not None:
            # Получаем только числовые колонки
            self.numeric_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
            if self.numeric_columns:
                self.info_label.setText(
                    f"Готово к построению. Доступно {len(self.numeric_columns)} числовых переменных")
            else:
                self.info_label.setText("Нет числовых переменных для анализа")

    def plot_heatmap(self):
        if self.df is None or not self.numeric_columns:
            QMessageBox.warning(self, "Ошибка", "Нет данных для построения тепловой карты")
            return

        try:
            # Очищаем предыдущий график
            self.figure.clear()

            # Вычисляем корреляционную матрицу
            corr_matrix = self.df[self.numeric_columns].corr()

            # Создаем subplot
            ax = self.figure.add_subplot(111)

            # Строим тепловую карту
            sns.heatmap(corr_matrix,
                        annot=self.annot_check.isChecked(),
                        fmt=".2f",
                        cmap=self.cmap_combo.currentText(),
                        center=0,
                        square=True,
                        cbar_kws={"shrink": .8},
                        ax=ax)

            ax.set_title('Тепловая карта корреляций числовых переменных')

            # Поворачиваем подписи для лучшей читаемости
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            plt.setp(ax.get_yticklabels(), rotation=0)

            self.figure.tight_layout()
            self.canvas.draw()

            # Находим самые сильные корреляции
            corr_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    corr_pairs.append({
                        'vars': (corr_matrix.columns[i], corr_matrix.columns[j]),
                        'value': corr_matrix.iloc[i, j]
                    })

            # Сортируем по абсолютному значению корреляции
            corr_pairs.sort(key=lambda x: abs(x['value']), reverse=True)

            info_text = f"Тепловая карта построена. Самые сильные корреляции:\n"
            for pair in corr_pairs[:3]:
                var1, var2 = pair['vars']
                value = pair['value']
                info_text += f"• {var1} & {var2}: {value:.3f}\n"

            self.info_label.setText(info_text)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось построить тепловую карту: {str(e)}")
            self.info_label.setText(f"Ошибка: {str(e)}")