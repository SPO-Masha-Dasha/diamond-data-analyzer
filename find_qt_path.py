import PyQt5
import os

print("Путь к PyQt5:", PyQt5.__file__)

# Поиск папки plugins
qt_path = os.path.dirname(PyQt5.__file__)
plugins_path = os.path.join(qt_path, 'Qt5', 'plugins', 'platforms')
print("Путь к плагинам platforms:", plugins_path)
print("Существует?", os.path.exists(plugins_path))

if os.path.exists(plugins_path):
    print("Содержимое папки platforms:")
    for file in os.listdir(plugins_path):
        print("  -", file)
else:
    # Попробуем другой возможный путь
    plugins_path2 = os.path.join(qt_path, 'Qt', 'plugins', 'platforms')
    print("Альтернативный путь:", plugins_path2)
    print("Существует?", os.path.exists(plugins_path2))