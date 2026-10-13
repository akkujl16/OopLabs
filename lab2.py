import json
import os
from enum import Enum
from typing import Dict, Any

# ANSI коды для цветов
class Color(Enum):
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    WHITE = "\033[37m"

class Printer:
    _font_data: Dict[str, Any] = {} # Словарь для хранения структуры шрифта

    # Чтение файлов
    @classmethod
    def load_font(cls, filepath: str):
        with open(filepath, "r", encoding="utf-8") as f:
            cls._font_data = json.load(f)
        print(f" УСПЕШНО ЗАГРУЖЕН ФАЙЛ {filepath}. Данные: {cls._font_data}")

    # Конструктор (инициализации объекта)
    def __init__(self, color: Color, position: int = 0, symbol: str = "*"):
        self.color = color
        self.position = position
        self.symbol = symbol

    # Метод сохранения текущей позиции курсора в памяти терминала
    def __enter__(self):
        print("\033[s", end="", flush=True)
        return self

    # Метод сбрасывание цвета и возвращение курсора в исходное состояние
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(Color.RESET.value, end="")
        print("\033[u", end="", flush=True)

    def print(self, color=None, position=None, symbol=None):
        if isinstance(self, Printer): # Проверка на вызов через экземпляр класса
            text = color if color is not None else "" # Так как self это сам принтер, то color становится текстом
            Printer._render_text(text, self.color, self.position, self.symbol)
        else: # Статический метод класса
            text = self # Питон передает строку текста в качестве первого аргумента
            final_color = color if color is not None else Color.WHITE
            final_position = position if position is not None else 0
            final_symbol = symbol if symbol is not None else "*"
            Printer._render_text(text, final_color, final_position, final_symbol)

    @classmethod
    def _render_text(cls, text: str, color: Color, position: int, symbol: str):
        if not cls._font_data:
            print("Шрифт не загружен")
            return
        first_letter = list(cls._font_data.keys())[0]
        height = len(cls._font_data[first_letter])
        lines = [" " * position for i in range(height)] # Инициализация строки сразу с нужным горизонтальным отступом
        for char in text.upper():
            letter_pattern = cls._font_data.get(char, [" " * height] * height) # Если символа нет в файле, то пустые пробелы по высоте шрифта
            for i in range(height):
                rendered_line = letter_pattern[i].replace("*", symbol)
                lines[i] += rendered_line + "  "  # Склеивание строчек буквы и добавление пробелов для красоты
        # Построчный вывод
        print(color.value, end="")
        for line in lines:
            print(line)
        print(Color.RESET.value, end="", flush=True)


# ДЕМОНСТРАЦИЯ РАБОТЫ
os.system('cls')
print("Чтение существующего шрифта высотой 5 символов")
Printer.load_font("font5.json")
# Работа статического метода (вместо позиции передается число пробелов для отступа)
Printer.print("A", Color.GREEN, 4, "#")
# Работа через with
with Printer(color=Color.BLUE, position=8, symbol="@") as printer:
    printer.print("BA")
    printer.print("AB")
print()
input("\n\n\n\n\n\n\n\n\n\nEnter для переключения на шрифт с высотой 7")

os.system('cls')
print("Чтение существующего шрифта высотой 7 символов")
Printer.load_font("font7.json")
# Работа статического метода
Printer.print("B", Color.YELLOW, 2, "*")
# Работа через with
with Printer(color=Color.YELLOW, position=6, symbol="?") as printer:
    printer.print("A")
    printer.print("B")
print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
