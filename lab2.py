import json
import os
from enum import Enum
from typing import Tuple, Dict, Any

# ANSI коды для цветов
class Color(Enum):
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    WHITE = "\033[37m"

class Printer:
    _font_data: Dict[str, Any] = {} # Словарь для хранение структуры шрифта

    # Чтение файла
    @classmethod
    def load_font(cls, filepath: str):
        with open(filepath, "r", encoding="utf-8") as f:
            cls._font_data = json.load(f)

    # Конструктор класса
    def __init__(self, color: Color, position: Tuple[int, int], symbol: str = "*"):
        self.color = color
        self.position = position
        self.symbol = symbol
        self._current_row_shift = 0 # Внутренний счетчик смещения вниз

    # Поддержка возвращения состояния консоли в исходное состояние
    def __enter__(self):
        print("\033[s", end="", flush=True)
        return self

    # Сбрасывание цвета и возвращение курсора в исходное состояние
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(Color.RESET.value, end="")
        print("\033[u", end="", flush=True)

    def print(self, *args, **kwargs): # *args и **kwargs для принятия абсолютно любых параметров в любом количестве и формате
        # Проверка на экземпляр класса
        if isinstance(self, Printer):
            if args:  # Текст передали просто так
                text = args[0]  # Первый аргумент из скобок
            else:  # Скобки пустые или именованные параметры
                text = kwargs.get("text", "")  # Параметр по имени text, иначе пустота
            start_row, start_col = self.position
            actual_row = start_row + self._current_row_shift
            height = self._render_text(text, self.color, (actual_row, start_col), self.symbol)
            self._current_row_shift += height + 1 # Смещение строки вниз
        # Cтатический метод класса и переназначение аргументов
        else:
            cls = self
            text = args[0] if len(args) > 0 else kwargs.get("text", "")
            color = args[1] if len(args) > 1 else kwargs.get("color", Color.WHITE)
            position = args[2] if len(args) > 2 else kwargs.get("position", (1, 1))
            symbol = args[3] if len(args) > 3 else kwargs.get("symbol", "*")
            Printer._render_text(text, color, position, symbol)

    @classmethod
    def _render_text(cls, text: str, color: Color, position: Tuple[int, int], symbol: str):
        if not cls._font_data:
            print("Шрифт не загружен")
            return 0

        height = cls._font_data.get("height", 5)
        letter_patterns = cls._font_data.get("letter_patterns", {})

        lines = [""] * height # Строки для букв
        for char in text.upper():
            letterPattern = letter_patterns.get(char, [" " * height] * height) # Если символа нет в файле, вывод пустых пробелов шириной с высоту шрифта
            for i in range(height):
                rendered_line = letterPattern[i].replace("*", symbol) # Замена шаблонного маркера '*' на выбранный пользователем символ
                lines[i] += rendered_line + "  "  # 2 пробела между буквами

        # ANSI-команды позиционирования курсора
        start_row, start_col = position
        for i, line in enumerate(lines):
            current_row = start_row + i
            print(f"\033[{current_row};{start_col}H", end="")
            print(color.value, end="")
            print(line, end="")
        print(Color.RESET.value, end="", flush=True)
        return height

# Функция для генерации демонстрационных файлов шрифтов
def create_fonts():
    font5 = {
        "height": 5,
        "letter_patterns": {
            "А": [
                "  *  ", 
                " * * ", 
                "*****", 
                "*   *", 
                "*   *"
            ],
            "Б": [
                "*****", 
                "*    ", 
                "**** ", 
                "*   *", 
                "**** "
            ],
            "В": [
                "**** ", 
                "*   *", 
                "**** ", 
                "*   *", 
                "**** "
            ],
            "Г": [
                "*****", 
                "*    ", 
                "*    ", 
                "*    ", 
                "*    "
            ],
            "Д": [
                "  *  ", 
                " * * ", 
                "*   *", 
                "*****", 
                "*   *"
            ]
        }
    }

    font7 = {
        "height": 7,
        "letter_patterns": {
            "А": [
                "   *   ", 
                "  * *  ", 
                " *   * ", 
                "*******", 
                "*     *", 
                "*     *", 
                "*     *"
            ],
            "Б": [
                "****** ", 
                "*      ", 
                "*      ", 
                "****** ", 
                "*     *", 
                "*     *", 
                "****** "
            ],
            "В": [
                "****** ", 
                "*     *", 
                "*     *", 
                "****** ", 
                "*     *", 
                "*     *", 
                "****** "
            ],
            "Г": [
                "****** ", 
                "*      ", 
                "*      ", 
                "*      ", 
                "*      ", 
                "*      ", 
                "*      "
            ],
            "Д": [
                "   *   ", 
                "  * *  ", 
                " *   * ", 
                "*     *", 
                "*******", 
                "*     *", 
                "*     *"
            ]
        }
    }

    with open("font5.json", "w", encoding="utf-8") as f: 
        json.dump(font5, f, ensure_ascii=False, indent=4)
    with open("font7.json", "w", encoding="utf-8") as f: 
        json.dump(font7, f, ensure_ascii=False, indent=4)

# Создание тестовых файлов конфигурации шрифтов
create_fonts()
    
# Очищение консоли перед демонстрацией
os.system('cls')

print("Шрифт высотой 5 символов")
Printer.load_font("font5.json")

# Работа статического метода
Printer.print(None, text="А", color=Color.GREEN, position=(4, 5), symbol="#")
    
# Работа через with
with Printer(color=Color.BLUE, position=(11, 5), symbol="@") as printer:
    printer.print("БА")
    printer.print("АБ")

print("\033[23;1H", end="")
input("Enter для переключения на шрифт с высотой 7")
os.system('cls')

print("Шрифт высотой 7 символов")
Printer.load_font("font7.json")

# Работа статического метода
Printer.print(None, text="Б", color=Color.YELLOW, position=(4, 5), symbol="*")

# Работа через with
with Printer(color=Color.YELLOW, position=(13, 5), symbol="?") as printer:
    printer.print("А")
    printer.print("Б")

print("\033[29;1H", end="")
print("Демонстрация завершена")
