import pandas as pd

try:
    df = pd.read_csv('diamonds.csv')
    print("Данные успешно загружены!")
    print(f"Размер данных: {df.shape}")
    print(f"Колонки: {list(df.columns)}")
    print("\nПервые 5 строк:")
    print(df.head())
except Exception as e:
    print(f"Ошибка загрузки: {e}")