import math

class Angle:
    def __init__(self, radians: float):
        self._radians = float(radians)

    # Фабричные методы
    @classmethod
    def from_radians(cls, rad: float):
        return cls(rad)

    @classmethod
    def from_degrees(cls, deg: float):
        return cls(math.radians(deg))

    # Строковое представление
    def __str__(self) -> str:
        return f"{self.get_degrees():.2f}° ({self._radians:.4f} rad)"

    def __repr__(self) -> str:
        return f"Angle(radians={self._radians})"

    # Геттеры и Сеттеры (без @property)
    def get_radians(self) -> float:
        return self._radians

    def set_radians(self, rad: float):
        self._radians = float(rad)

    def get_degrees(self) -> float:
        return math.degrees(self._radians)

    def set_degrees(self, deg: float):
        self._radians = math.radians(deg)

    # Вспомогательный метод для нормализации угла
    def _normalize(self) -> float:
        return self._radians % (2 * math.pi)

    # Сравнение углов с учетом периодичности
    def __eq__(self, other) -> bool:
        if not isinstance(other, Angle):
            return False
        return math.isclose(self._normalize(), other._normalize(), abs_tol=1e-9)

    def __lt__(self, other) -> bool:
        if not isinstance(other, Angle):
            return NotImplemented
        return self._normalize() < other._normalize()

    def __le__(self, other) -> bool:
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other) -> bool:
        if not isinstance(other, Angle):
            return NotImplemented
        return self._normalize() > other._normalize()

    def __ge__(self, other) -> bool:
        return self.__gt__(other) or self.__eq__(other)

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    # Преобразование типов
    def __float__(self) -> float:
        return self._radians

    def __int__(self) -> int:
        return int(self._radians)

    # Математические операции
    def __add__(self, other):
        if isinstance(other, Angle):
            return Angle(self._radians + other._radians)
        elif isinstance(other, (int, float)):
            return Angle(self._radians + other)
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Angle):
            return Angle(self._radians - other._radians)
        elif isinstance(other, (int, float)):
            return Angle(self._radians - other)
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return Angle(other - self._radians)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Angle(self._radians * other)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Деление угла на ноль невозможно.")
            return Angle(self._radians / other)
        return NotImplemented


class AngleRange:
    def __init__(self, start, end, include_start: bool = True, include_end: bool = True):
        # Принимает start и end в виде float, int (считаются радианами) или Angle.
        # include_start / include_end определяют, включающие ли границы (True - [, False - ().
        
        self.start = start if isinstance(start, Angle) else Angle(float(start))
        self.end = end if isinstance(end, Angle) else Angle(float(end))
        self.include_start = include_start
        self.include_end = include_end

    # Сравнение промежутков
    def __eq__(self, other) -> bool:
        if not isinstance(other, AngleRange):
            return False
        return (self.start == other.start and self.end == other.end and
                self.include_start == other.include_start and self.include_end == other.include_end)

    def __lt__(self, other) -> bool:
        if not isinstance(other, AngleRange):
            return NotImplemented
        return abs(self) < abs(other)

    def __le__(self, other) -> bool:
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other) -> bool:
        if not isinstance(other, AngleRange):
            return NotImplemented
        return abs(self) > abs(other)

    def __ge__(self, other) -> bool:
        return self.__gt__(other) or self.__eq__(other)

    # Строковое представление
    def __str__(self) -> str:
        left_bracket = "[" if self.include_start else "("
        right_bracket = "]" if self.include_end else ")"
        return f"{left_bracket}{self.start.get_degrees():.1f}°, {self.end.get_degrees():.1f}°{right_bracket}"

    def __repr__(self) -> str:
        return (f"AngleRange({repr(self.start)}, {repr(self.end)}, "
                f"include_start={self.include_start}, include_end={self.include_end})")

    # Длина промежутка
    def __abs__(self) -> float:
        # Возвращаемая длина промежутка в радианах
        # Промежуток может переходить через 0
        diff = self.end.get_radians() - self.start.get_radians()
        return diff if diff >= 0 else (diff + 2 * math.pi)

    def length_degrees(self) -> float:
        return math.degrees(abs(self))

    # Проверка вхождения
    def __contains__(self, item) -> bool:
        # Проверка вхождение угла в промежуток
        if isinstance(item, (Angle, int, float)):
            target = item if isinstance(item, Angle) else Angle(float(item))
            
            # Нормализование относительно начала отсчета промежутка
            start_rad = self.start.get_radians()
            end_rad = self.end.get_radians()
            target_rad = target.get_radians()
            
            # Сдвиг, чтобы start_rad был нулем
            shift = start_rad
            max_len = (end_rad - start_rad) % (2 * math.pi)
            if max_len == 0 and start_rad != end_rad:
                max_len = 2 * math.pi
                
            check_rad = (target_rad - shift) % (2 * math.pi)
            
            # Проверка границ
            if math.isclose(check_rad, 0, abs_tol=1e-9):
                return self.include_start
            if math.isclose(check_rad, max_len, abs_tol=1e-9):
                return self.include_end
                
            return 0 < check_rad < max_len

        # Проверка вхождение одного промежутка в другой
        elif isinstance(item, AngleRange):
            # Промежуток входит в другой, если входят обе его крайние точки
            if item.start not in self or item.end not in self:
                return False
            
            # Проверка строгости границ при совпадении точек
            if item.start == self.start and item.include_start and not self.include_start:
                return False
            if item.end == self.end and item.include_end and not self.include_end:
                return False
            return True
            
        return False

    # Сложение и вычитание промежутков
    def __add__(self, other):
        # Сложение промежутка с углом или числом (сдвиг промежутка)
        if isinstance(other, (Angle, int, float)):
            shift = other if isinstance(other, Angle) else Angle(float(other))
            return [AngleRange(self.start + shift, self.end + shift, self.include_start, self.include_end)]
        return NotImplemented

    def __sub__(self, other):
        # Вычитание из промежутка угла/числа (сдвиг назад)
        if isinstance(other, (Angle, int, float)):
            shift = other if isinstance(other, Angle) else Angle(float(other))
            return [AngleRange(self.start - shift, self.end - shift, self.include_start, self.include_end)]
        return NotImplemented

print("Тестирование класса Angle")
# Фабричные методы и вывод
a1 = Angle.from_degrees(90)
a2 = Angle.from_radians(math.pi / 2)
a3 = Angle.from_degrees(450)
    
print(f"a1 (90 deg): {a1} | repr: {repr(a1)}")
print(f"a3 (450 deg): {a3}")
    
# Геттеры и сеттеры
a1.set_degrees(180)
print(f"a1 после изменения на 180°: {a1.get_radians():.4f} rad")
a1.set_radians(math.pi / 2)
    
# Проверка периодичности при сравнении
print(f"a1 == a2 (90° == π/2): {a1 == a2}")
print(f"a1 == a3 (90° == 450° с учетом периодичности): {a1 == a3}")
    
# Преобразование типов
print(f"float(a1): {float(a1):.4f}")
print(f"int(a1): {int(a1)}")
    
# Математические операции
print(f"a1 + 45°: {a1 + Angle.from_degrees(45)}")
print(f"a1 + 1.0 (число в рад): {a1 + 1.0}")
print(f"a1 * 2: {a1 * 2}")
print(f"a1 / 2: {a1 / 2}")
print()

print("Тестирование класса AngleRange")
# Создание промежутков
range1 = AngleRange(Angle.from_degrees(0), Angle.from_degrees(180), include_start=True, include_end=False)
range2 = AngleRange(0, math.pi, include_start=True, include_end=False) # через числа
    
print(f"range1: {range1} | repr: {repr(range1)}")
print(f"range1 == range2: {range1 == range2}")
    
# Длина промежутка
print(f"Длина range1 в градусах: {range1.length_degrees()}°")
print(f"abs(range1) в радианах: {abs(range1):.4f}")
    
# Операция 'in' для угла
test_angle1 = Angle.from_degrees(90)
test_angle2 = Angle.from_degrees(180)
print(f"90° в {range1}: {test_angle1 in range1}") # True
print(f"180° в {range1} (исключая границу): {test_angle2 in range1}") # False
    
# Операция 'in' для промежутков (подмножество)
sub_range = AngleRange(Angle.from_degrees(30), Angle.from_degrees(150))
print(f"Промежуток [30°, 150°] в {range1}: {sub_range in range1}") # True
    
# Сравнение промежутков по длине
large_range = AngleRange(0, Angle.from_degrees(270))
print(f"range1 < large_range: {range1 < large_range}") # True
    
# Сложение и вычитание (сдвиг промежутков)
shifted_ranges = range1 + Angle.from_degrees(90)
print(f"range1 + 90° (сдвиг): {shifted_ranges[0]}") # Сдвиг на [90°, 270°)
    
# Добавим для полноты картины вычитание угла (сдвиг назад)
subtracted_ranges = range1 - Angle.from_degrees(45)
print(f"range1 - 45° (сдвиг): {subtracted_ranges[0]}") # Сдвиг на [315°, 135°)
