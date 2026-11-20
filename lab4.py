from typing import Any, Generic, Protocol, TypeVar

# 1 Протокол обработчика событий
class EventArgs: # базовый класс для объеденения в иерархию
    pass

TEventArgs = TypeVar("TEventArgs", bound=EventArgs, contravariant=True) # прин EventArgs или его наследников, разр подпис на конкр события более общие обработчики

class EventHandler(Protocol[TEventArgs]): # протокол обработчик, соответствующий любому классу и имеющий метод handle для обработки событий TEventArgs без явного наследования
    def handle(self, sender: object, args: TEventArgs):
        ...

# 2 Обобщенный класс Event (подписки, отписки и оповещения)
T = TypeVar("T", bound=EventArgs) # перемен обобщ типа, прин только  EventArgs или любых его наследников

class Event(Generic[T]): # обобщ класс диспетчера событий
    def __init__(self): # конструктор класса для внутр пустого списка хранения всех подписанных обработчиков событий
        self._handlers: list[EventHandler[T]] = []

    def __iadd__(self, handler: EventHandler[T]): # перегрузка +=
        if handler not in self._handlers: # проверка на дублирование подписок
            self._handlers.append(handler) # переданный обработчик в конец списка подписчиков
        return self

    def __isub__(self, handler: EventHandler[T]): # перегрузка -=
        if handler in self._handlers:
            self._handlers.remove(handler)
        return self

    def invoke(self, sender: object, args: T): # оповещение подписантов
        for handler in list(self._handlers): # цикл по временной копии списка подписчиков от отписок во время события
            handler.handle(sender, args)

    def __call__(self, sender: object, args: T): # экземпляра события как обычную функцию
        self.invoke(sender, args) # переправка в invoke

# 3 Аргументы события после изменения свойства
class PropertyChangedEventArgs(EventArgs): # класс аргументов события, происходящего после изменения свойства
    def __init__(self, property_name: str):
        self.property_name: str = property_name # имя свойства в публичный атрибут экземпляра, чтобы подписчики знали какое поле изменилось

# 4 Обработчик события изменения свойства (логирование в консоль)
class ConsolePropertyChangedLogger: # обработчик события изменения свойства (логирование в консоль)
    def __init__(self, logger_name: str = "Logger"): # опциональное имя логгера для различия экземпляров логгеров.
        self.logger_name = logger_name

    def handle(self, sender: object, args: PropertyChangedEventArgs): # метод вызывающийся при срабатывании события после изменения свойства
        print(f"[{self.logger_name}] Объект {sender} изменил свойство '{args.property_name}'.")

# 5 Аргументы события до изменения свойства с возможностью отмены
class PropertyChangingEventArgs(EventArgs): # класс аргументов события до изменения свойства (с возможностью отмены)
    def __init__(self, property_name: str, old_value: Any, new_value: Any):
        self.property_name: str = property_name
        self.old_value: Any = old_value
        self.new_value: Any = new_value
        self.can_change: bool = True

# 6 Обработчик события и валидатор
class UserValidator: # класс обработчик для проверки корректности данных пользователя перед их сохранением
    def handle(self, sender: object, args: PropertyChangingEventArgs): # метод проверки, который вызывается до изменения свойства и получает объект с данными о предстоящем изменении
        if args.property_name == "age":
            if not isinstance(args.new_value, int) or not (0 <= args.new_value <= 120):
                print(f"[Валидатор] Ошибка: недопустимый возраст ({args.new_value}). Изменение отменено")
                args.can_change = False # сигнали User о необходимости отменить запись нового значения
        elif args.property_name == "name":
            if not isinstance(args.new_value, str) or len(args.new_value.strip()) == 0:
                print("[Валидатор] Ошибка: имя не может быть пустым. Изменение отменено")
                args.can_change = False

class ProductValidator: # класс обработчик для проверки корректности данных товара перед их изменением
    def handle(self, sender: object, args: PropertyChangingEventArgs):
        if args.property_name == "price":
            if not isinstance(args.new_value, (int, float)) or args.new_value < 0:
                print(f"[Валидатор] Ошибка: цена ({args.new_value}) не может быть отрицательной. Изменение отменено")
                args.can_change = False
        elif args.property_name == "stock":
            if not isinstance(args.new_value, int) or args.new_value < 0:
                print(f"[Валидатор] Ошибка: остаток ({args.new_value}) не может быть меньше нуля. Изменение отменено")
                args.can_change = False

# 7 Два класса с минимум тремя полями, генерирующие события до и после изменений
class User:
    def __init__(self, name: str, age: int, email: str):
        self.property_changing = Event[PropertyChangingEventArgs]() # диспетчер событий для оповещения подписчиков до фактического изменения любого свойства
        self.property_changed = Event[PropertyChangedEventArgs]() # диспетчер событий для оповещения подписчиков после успешного изменения свойства
        self._name = name
        self._age = age
        self._email = email

    def _set_property(self, prop_name: str, attr_name: str, new_value: Any): # общий вспомогательный метод для безопасной смены любого свойства с запуском всех нужных событий
        old_value = getattr(self, attr_name) # текущее значение внутреннего атрибута объекта по его строковому имени
        if old_value == new_value:
            return

        changing_args = PropertyChangingEventArgs(prop_name, old_value, new_value) # объект с информацией о предстоящем изменении (имя свойства, старое и новое значения)
        self.property_changing.invoke(self, changing_args) # оповещение всех подписчиков о попытке изменить свойство

        if not changing_args.can_change:
            return

        setattr(self, attr_name, new_value) # новое проверенное значение во внутренний атрибут объекта
        self.property_changed(self, PropertyChangedEventArgs(prop_name)) # оповещение всех подписчиков, что свойство успешно изменилось

    @property # превращает метод в геттер
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._set_property("name", "_name", value)

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value: int):
        self._set_property("age", "_age", value) # "age" для событий, "_age" для самого объекта (памяти)

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value: str):
        self._set_property("email", "_email", value)

    def __repr__(self):
        return f"User(name='{self._name}', age={self._age}, email='{self._email}')"

class Product:
    def __init__(self, title: str, price: float, stock: int):
        self.property_changing = Event[PropertyChangingEventArgs]()
        self.property_changed = Event[PropertyChangedEventArgs]()
        self._title = title
        self._price = price
        self._stock = stock

    def _set_property(self, prop_name: str, attr_name: str, new_value: Any):
        old_value = getattr(self, attr_name)
        if old_value == new_value:
            return

        changing_args = PropertyChangingEventArgs(prop_name, old_value, new_value)
        self.property_changing.invoke(self, changing_args)

        if not changing_args.can_change:
            return

        setattr(self, attr_name, new_value)
        self.property_changed.invoke(self, PropertyChangedEventArgs(prop_name))

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value: str):
        self._set_property("title", "_title", value)

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value: float):
        self._set_property("price", "_price", value)

    @property
    def stock(self):
        return self._stock

    @stock.setter
    def stock(self, value: int):
        self._set_property("stock", "_stock", value)

    def __repr__(self):
        return f"Product(title='{self._title}', price={self._price}, stock={self._stock})"

# 8 Демонстрация работы
if __name__ == "__main__":
    print("Создание объектов, подписчиков и подписка")
    user = User("Алексей", 25, "alex@example.com")
    product = Product("Ноутбук", 75000.0, 10)

    logger_main = ConsolePropertyChangedLogger("Главный логгер")
    logger_audit = ConsolePropertyChangedLogger("Аудит")
    user_validator = UserValidator()
    product_validator = ProductValidator()

    # подписываемся через +=
    user.property_changing += user_validator
    user.property_changed += logger_main
    user.property_changed += logger_audit

    product.property_changing += product_validator
    product.property_changed += logger_main

    print("\n Успешное изменение")
    user.age = 26
    product.price = 72000.0

    print("\n Неудачное изменение")
    user.age = -5
    user.name = "   "
    product.price = -100
    print(f"Текущее состояние User: {user}")
    print(f"Текущее состояние Product: {product}")

    print("\n Отписка одного из обработчиков и повторное изменение")
    user.property_changed -= logger_audit
    user.property_changing -= user_validator

    # отписка Аудит и UserValidator, замена имени на пустое и возраст на 150
    user.name = ""
    user.age = 150
    print(f"Итоговое состояние User: {user}")
