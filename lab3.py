import datetime
import re
from enum import Enum
from typing import List, Protocol

# перечислитель LogLevel
class LogLevel(Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"

# протокол для фильтров (True, если лог проходит фильтр, и False, если нет)
class LogFilterProtocol(Protocol):
    def match(self, log_level: LogLevel, text: str) -> bool:
        ...

# классы фильтров
class SimpleLogFilter: # фильтрация по вхождению обычной строки в текст сообщения
    def __init__(self, pattern: str):
        self.pattern = pattern
    def match(self, log_level: LogLevel, text: str) -> bool:
        return (self.pattern in text)  # True, если подстрока есть в тексте, иначе False

class ReLogFilter: # фильтрация по вхождению регулярного выражения в текст сообщения
    def __init__(self, pattern: str):
        self.pattern = pattern
    def match(self, log_level: LogLevel, text: str) -> bool:
        return bool(re.search(self.pattern, text))  # True, если регулярка нашла совпадение

class LevelFilter: # фильтрация по LogLevel
    def __init__(self, allowed_level: LogLevel):
        self.allowed_level = allowed_level  # сохранение уровня, который разрешается пропускать
    def match(self, log_level: LogLevel, text: str) -> bool: # text ради совместимости с протоколом LogFilterProtocol
        return (log_level == self.allowed_level)  # True, если уровень совпадает с разрешенным

# протокол для для обработки и вывода сообщения лога
class LogHandlerProtocol(Protocol):
    def handle(self, log_level: LogLevel, text: str) -> None:
        ...

# классы обработчиков
class FileHandler: # запись логов в файл
    def __init__(self, filename: str = "app.log"):
        self.filename = filename
    def handle(self, log_level: LogLevel, text: str) -> None:
        with open(self.filename, "a", encoding="utf-8") as f:  # файл в режиме добавления a
            f.write(text + "\n")  # запись строки лога и перенос указателя на новую строку

class SocketHandler: # отправка логов через сокет
    def handle(self, log_level: LogLevel, text: str) -> None:
        print(f"[Socket] Отправка через сокет: {text}")

class ConsoleHandler: # вывод логов в консоль
    def handle(self, log_level: LogLevel, text: str) -> None:
        print(text)

class SyslogHandler: # записи в системные логи
    def handle(self, log_level: LogLevel, text: str) -> None:
        print("[Syslog] Запись в систему: {text}")

class FtpHandler: # записи логов на удаленный FTP сервер
    def handle(self, log_level: LogLevel, text: str) -> None:
        print(f"[FTP] Загрузка файла лога на FTP: {text}")

# протокол для форматирования текста (возвращение измененной строки лога)
class LogFormatterProtocol(Protocol):
    def format(self, log_level: LogLevel, text: str) -> str:
        ...

# конкретное форматирование по шаблону [<log_level>] [<data:yyyy.MM.dd hh:mm:ss>] <text>
class DefaultFormatter:
    def format(self, log_level: LogLevel, text: str) -> str:
        now = (datetime.datetime.now())  # текущая дата и время на компьютере
        date_str = now.strftime("%Y.%m.%d %H:%M:%S")  # форматирование даты в нужный формат
        return f"[{log_level.value}] [{date_str}] {text}"  # сбор и возвращение итоговой строки

# класс Logger (агрегация)
class Logger:
    def __init__(
        self,
        filters: List[LogFilterProtocol],  # список фильтров
        formatters: List[LogFormatterProtocol],  # список форматировщиков
        handlers: List[LogHandlerProtocol],  # список обработчиков
    ):
        self.filters = filters  # сохранение переданных фильтров в объект
        self.formatters = formatters  # сохранение переданных форматировщиков
        self.handlers = handlers  # сохранение переданных обработчиков

    def log(self, log_level: LogLevel, text: str) -> None: # проверка фильтров (хотя один фильтр вернет False, логирование прерывается), применение форматирования и передача обработчикам
        for log_filter in self.filters:
            if not log_filter.match(log_level, text):
                return  # лог отброшен фильтром

        # прогонка текста через все форматировщики по цепочке
        formatted_text = text
        for formatter in self.formatters:
            formatted_text = formatter.format(log_level, formatted_text)

        # итоговый текст каждому обработчику из списка
        for handler in self.handlers:
            handler.handle(log_level, formatted_text)

    def log_info(self, text: str) -> None: # вызов для логов уровня INFO
        self.log(LogLevel.INFO, text)

    def log_warn(self, text: str) -> None: # вызов для логов уровня WARN
        self.log(LogLevel.WARN, text)

    def log_error(self, text: str) -> None: # вызов для логов уровня ERROR
        self.log(LogLevel.ERROR, text)

# демонстрация работы
print(" старт")

# фильтр по слову
my_filters = [SimpleLogFilter(pattern="важно")]

my_formatters = [DefaultFormatter()]

# вывод логов одновременно в консоль и записывание в файл
my_handlers = [ConsoleHandler(), FileHandler("demo_logs.txt")]

# инициализация Logger (списки через агрегацию)
logger = Logger(filters=my_filters, formatters=my_formatters, handlers=my_handlers)

print("\n сообщение без ключевого слова: ")
logger.log_info("рядовой процесс")  # не выведется

print("\n корректные сообщения: ")
logger.log_info("Это важно: система запущена")  # выведется
logger.log_warn("Очень важно: заканчивается свободное место")  # выведется

print("\n конец (логи сохранены в demo_logs.txt)")
