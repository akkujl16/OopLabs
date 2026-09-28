import math

class Angle:
        # конструктор класса (инициализирует угол в радианах)
    def __init__(self, radians: float):
        self._radians = float(radians) # _ так как переменная приватная

        # фабричный метод для создания объекта Angle из значения в радианах
    @classmethod
    def from_radians(cls, rad: float):
        return cls(rad)

        # фабричный метод для создания объекта Angle из значения в градусах
    @classmethod
    def from_degrees(cls, deg: float):
        rad = math.radians(deg)  # конвертирование градусов в радианы с помощью встроенной функции
        return cls(rad)

        # геттеры и сеттеры @property
    def get_radians(self):
        return self._radians  # возвращение приватной переменной с радианами

    def set_radians(self, rad: float):
        self._radians = float(rad)  # перезаписывание внутреннего состояния новым значением в радианах

    def get_degrees(self):
        return math.degrees(self._radians)  # перевод внутренних радиан в градусы и возвращение их

    def set_degrees(self, deg: float):
        self._radians = math.radians(deg)  # перевод градусов в радианы и сохранение в состояние

        # вспомогательный метод для периодического сравнения (сбрасывает лишние обороты, приводя угол в диапазон от 0 до 2π)
    def _normalize(self):
        return self._radians % (2 * math.pi) # нахождение остатка от деления текущего угла на 2*pi (автоматически убирает все лишние полные обороты)

        # строковое представление
    def __str__(self): # читаемое строковое представление объекта для print и пользователя
        return f"{self.get_degrees():.2f}° ({self._radians:.4f} rad)"

    def __repr__(self): # официальное строковое представление объекта для отладки и разработчика
        return f"Angle({self._radians})"

        # преобразование угла
    def __float__(self): # преобразование объекта Angle во float (возвращение радиан)
        return self._radians

    def __int__(self): # преобразование объекта Angle в int (округление радиан)
        return int(self._radians)

        # сравнения углов с учетом периодичности
    def __eq__(self, other): # ==
        if not isinstance(other, Angle):  # если сравниваемый объект не является Angle
            return False  # углы могут быть равны только углам
        return math.isclose(self._normalize(), other._normalize()) # сравнение нормализованных значений с учетом погрешности вычислени

    def __lt__(self, other): # <
        if not isinstance(other, Angle):
            return NotImplemented
        return self._normalize() < other._normalize()  # сравнение приведенных к [0, 2π) углов

    def __le__(self, other): # <=
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other): # >
        if not isinstance(other, Angle):
            return NotImplemented
        return self._normalize() > other._normalize()  # сравнение приведенных к [0, 2π) углов

    def __ge__(self, other): # >=
        return self.__gt__(other) or self.__eq__(other)

    def __ne__(self, other): # !=
        return not self.__eq__(other)

        # арифметические операции
    def _to_rad(self, val) -> float: # метод для извлечения радиан из Angle
        if isinstance(val, Angle):  # если передан объект класса Angle
            return val.get_radians()  # то забираем его радианы
        elif isinstance(val, (int, float)):  # если передано число (в радианах)
            return float(val)
        else:
            raise TypeError("Операция только для Angle, float или int")

    def __add__(self, other): # сложение углов или угла с числом (в радианах)
        total_rad = self._radians + self._to_rad(other)
        return Angle(total_rad)

    def __radd__(self, other): # правое сложение (число + Angle)
        return self.__add__(other)

    def __sub__(self, other): # вычитание углов или числа из угла (в радианах)
        total_rad = self._radians - self._to_rad(other)
        return Angle(total_rad)

    def __rsub__(self, other): # правое вычитание (число - Angle)
        total_rad = self._to_rad(other) - self._radians
        return Angle(total_rad)

    def __mul__(self, other): # умножение угла на число (float или int)
        if not isinstance(other, (int, float)):  # умножать угол на другой угол некорректно
            return NotImplemented
        return Angle(self._radians * other)  # умножение радианы на число и возвращение нового Angle

    def __rmul__(self, other): # правое умножение (число * Angle)
        return self.__mul__(other)

    def __truediv__(self, other): # деление угла на число (float или int)
        if not isinstance(other, (int, float)):  # делить угол можно только на скалярное число
            return NotImplemented
        return Angle(self._radians / other)

class AngleRange:
        # конструктор (инициализирует с помощью промежутка начальной и конечной точками, а также включениями)
    def __init__(self, start, end, include_start: bool = True, include_end: bool = True):
        if isinstance(start, Angle):
            self.start = start
        else:
            self.start = Angle(float(start))
        if isinstance(end, Angle):
            self.end = end
        else:
            self.end = Angle(float(end))
        self.include_start = include_start  # включать ли начальную точку в интервал (True/False)
        self.include_end = include_end  # включать ли конечную точку в интервал (True/False)

        # длина промежутка
    def __abs__(self):
        diff = self.end._normalize() - self.start._normalize() # разница между нормализованными углами конца и начала
        if diff < 0:  # если конец меньше начала на круге, значит интервал пересекает нулевую отметку
            diff += 2 * math.pi  # коррекция длины, добавление до полного оборота
        return diff  # длина интервала в радианах

        # строковое представление
    def __str__(self):
        left_bracket = "[" if self.include_start else "("  # скобка для начала
        right_bracket = "]" if self.include_end else ")"  # скобка для конца
        return f"{left_bracket}{self.start.get_degrees():.1f}°, {self.end.get_degrees():.1f}°{right_bracket}" # формирование итоговой строки с углами в градусах

    def __repr__(self):
        return f"AngleRange({repr(self.start)}, {repr(self.end)}, {self.include_start}, {self.include_end})"

        # сравнение промежутков
    def __eq__(self, other):
        if not isinstance(other, AngleRange):  # если сравниваемый объект не интервал
            return False
        # проверка равенства начальных/конечных углов и одинаковость включения скобок
        return (
            self.start == other.start
            and self.end == other.end
            and self.include_start == other.include_start
            and self.include_end == other.include_end
        )

    def __lt__(self, other): # на основе их длины (<)
        if not isinstance(other, AngleRange):
            return NotImplemented
        return abs(self) < abs(other)

    def __le__(self, other): # на основе их длины (<=)
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other): # на основе их длины (>)
        if not isinstance(other, AngleRange):
            return NotImplemented
        return abs(self) > abs(other)

    def __ge__(self, other): # на основе их длины (>=)
        return self.__gt__(other) or self.__eq__(other)

        # проверка вхождения
    def __contains__(self, item): # проверка, входит ли угол или другой промежуток в текущий промежуток
        if isinstance(item, Angle):  # конкретного угл
            # все углы к нормализованному виду [0, 2π) для линейного сравнения
            s = self.start._normalize()
            e = self.end._normalize()
            x = item._normalize()

            # проверка начальной границы интервала с учетом ее включения
            if math.isclose(x, s):
                return self.include_start
            # проверка конечной границы интервала с учетом ее включения
            if math.isclose(x, e):
                return self.include_end

            # проверяем, лежит ли точка внутри интервала
            if s <= e:  # стандартный интервал, не пересекающий 0 градусов
                return s < x < e
            else:  # интервал пересекает нулевую отметку
                return x > s or x < e

        elif isinstance(item, AngleRange):  # вхождение другого промежутка
            return item.start in self and item.end in self

        return False  # любые другие типы - False

        # сложение и вычитание промежутков
    def __add__(self, other): # сложение промежутков (объединение пересекающихся промежутков, иначе возвращение списка из двух)
        if not isinstance(other, AngleRange):
            return NotImplemented

        # один промежуток пересекается с другим или содержит его границы
        if (
            self.start in other
            or self.end in other
            or other.start in self
            or other.end in self
        ):
            # нахождение минимальной начальной точки и максимальной конечной точки на окружности
            # с произвольными разрывами возвращается список промежутков
            # если они полностью перекрываются, возвращаем один расширенный промежуток
            new_start = (
                self.start
                if self.start._normalize() < other.start._normalize()
                else other.start
            )
            new_end = (
                self.end
                if self.end._normalize() > other.end._normalize()
                else other.end
            )
            return [
                AngleRange(
                    new_start,
                    new_end,
                    self.include_start or other.include_start,
                    self.include_end or other.include_end,
                )
            ]

        # промежутки абсолютно не пересекаются, возвращаются их оба в списке
        return [self, other]

    def __sub__(self, other):
        if not isinstance(other, AngleRange):
            return NotImplemented

        # вычитаемый промежуток вообще не пересекается с текущим
        if (
            self.start not in other
            and self.end not in other
            and other.start not in self
        ):
            return [self]

        # вычитаемый промежуток полностью поглощает текущий(из текущего промежутка ничего не осталось, возвращение пустого списка)
        if self.start in other and self.end in other:
            return []

        # вычитаемый промежуток отрезает кусок изнутри (разделяет текущий на две части)
        if other.start in self and other.end in self:
            part1 = AngleRange(
                self.start, other.start, self.include_start, not other.include_start
            )
            part2 = AngleRange(
                other.end, self.end, not other.include_end, self.include_end
            )
            return [part1, part2]

        # отрезается только один из краев промежутка
        if other.start in self:
            return [
                AngleRange(
                    self.start, other.start, self.include_start, not other.include_start
                )
            ]
        if other.end in self:
            return [
                AngleRange(
                    other.end, self.end, not other.include_end, self.include_end
                )
            ]
        return [self]

    # демонстрация
print(" Тестирование класса Angle ")

    # фабричные методы
a1 = Angle.from_degrees(90)  # угол 90 градусов
a2 = Angle.from_radians(math.pi)  # угол Пи радиан (180 градусов)
print(f"a1 (из градусов): {a1}")  # строковое представление str
print(f"a2 (из радиан): {repr(a2)}")  # отладочное представление repr

    # геттеры и сеттеры
a1.set_degrees(45)  # изменение угла на 45 градусов через сеттер
print(f"Измененный a1 в радианах: {a1.get_radians():.4f}")  # геттер радиан
print(f"Измененный a1 в градусах: {a1.get_degrees():.1f}°")  # геттер градусов

    # сравнения с учетом периодичности
a3 = Angle.from_degrees(30)  # угол 30 градусов
a4 = Angle.from_degrees(390)  # угол 390 градусов
print(f"Угол 30° == 390°? -> {a3 == a4}")  # True из-за периодичности
print(f"Угол 180° > 45°? -> {a2 > a1}")  # сравнение углов

    # преобразование типов
print(f"float(a3): {float(a3):.4f}")  # преобразование во float (радианы)
print(f"int(a2): {int(a2)}")  # преобразование в int

    # арифметические операции
sum_angle = a3 + a1  # сложение двух объектов Angle
print(f"30° + 45° = {sum_angle}")
sum_with_num = a3 + math.pi  # сложение угла с числом (в радианах)
print(f"30° + пи рад = {sum_with_num}")
mul_angle = a3 * 3  # умножение угла на число
print(f"30° * 3 = {mul_angle}")


print("\n Тестирование класса AngleRange ")
    # создание промежутков (включающих и исключающих)
    # создание интервала от 0 до 180 градусов, включая 0 и исключая 180
range1 = AngleRange(
        Angle.from_degrees(0),
        Angle.from_degrees(180),
        include_start=True,
        include_end=False,
)
print(f"Промежуток 1: {range1}")

    # длина промежутка
print(f"Длина промежутка 1 (через abs): {abs(range1):.4f} рад")  # в радианах

    # проверка вхождения (in)
test_angle1 = Angle.from_degrees(90)  # точка внутри интервала
test_angle2 = Angle.from_degrees(180)  # точка на исключенной границе
print(f"Входит ли 90° в {range1}? -> {test_angle1 in range1}")  # True
print(f"Входит ли 180° в {range1}? -> {test_angle2 in range1}")  # False (так как граница исключена)

    # сравнение промежутков
range2 = AngleRange(0, math.pi / 2)  # интервал от 0 до 90 градусов (длина меньше)
print(f"Промежуток 1 == Промежуток 2? -> {range1 == range2}")  # сравнение на эквивалентность
print(f"Промежуток 1 > Промежуток 2 (по длине)? -> {range1 > range2}")  # сравнение по длине

    # сложение и вычитание промежутков
print(f"Сложение непересекающихся: {range1 + AngleRange(Angle.from_degrees(200), Angle.from_degrees(250))}")
sub_result = range1 - range2  # из [0, 180) вычитается [0, 90]
print(f"Результат вычитания интервалов: {sub_result}")  # остаток интервала
