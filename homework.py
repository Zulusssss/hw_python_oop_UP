from dataclasses import dataclass, asdict
from typing import Type


@dataclass
class InfoMessage:
    """Информационное сообщение о тренировке."""
    training_type: str
    duration: float
    distance: float
    speed: float
    calories: float

    def get_message(self):
        return ('Тип тренировки: {training_type}; '
                'Длительность: {duration:.3f} ч.; '
                'Дистанция: {distance:.3f} км; '
                'Ср. скорость: {speed:.3f} км/ч; '
                'Потрачено ккал: {calories:.3f}.'
                .format(**asdict(self)))


class Training:
    """Базовый класс тренировки.
    Методы verify проверяют пригодность вводимых данных.
    """
    LEN_STEP = 0.65
    M_IN_KM = 1000
    MIN_IN_H = 60

    def __init__(self,
                 action: int,
                 duration: float,
                 weight: float,) -> None:
        self.action = action
        self.duration = duration
        self.weight = weight

    @classmethod
    def verify_action(cls, action):
        if type(action) is not int or action < 0:
            raise TypeError("Кол-во шагов должно быть типа int и больше 0")

    @classmethod
    def verify_duration(cls, duration):
        if type(duration) is not float or duration < 0:
            raise TypeError("Длительность тренировки должна быть типа float и больше 0")

    @classmethod
    def verify_weight(cls, weight):
        if type(weight) is not float or weight < 0:
            raise TypeError("Вес должен быть типа float и больше 0")

    @property
    def action(self):
        return self.__action

    @action.setter
    def action(self, action):
        self.verify_action(action)
        self.__action = action

    @property
    def duration(self):
        return self.__duration

    @duration.setter
    def duration(self, duration):
        self.verify_duration(duration)
        self.__duration = duration

    @property
    def weight(self):
        return self.__weight

    @weight.setter
    def weight(self, weight):
        self.verify_weight(weight)
        self.__weight = weight

    def get_distance(self) -> float:
        """Получить дистанцию в км."""
        return self.action * self.LEN_STEP / self.M_IN_KM

    def get_mean_speed(self) -> float:
        """Получить среднюю скорость движения."""
        return (self.action * self.LEN_STEP / self.M_IN_KM) / self.duration

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        pass

    def show_training_info(self) -> InfoMessage:
        """Вернуть информационное сообщение о выполненной тренировке."""
        return InfoMessage(self.__class__.__name__, self.duration,
                           self.get_distance(), self.get_mean_speed(),
                           self.get_spent_calories())


class Running(Training):
    """Тренировка: бег."""
    __CALORIES_MEAN_SPEED_MULTIPLIER = 18
    __CALORIES_MEAN_SPEED_SHIFT = 1.79

    def __init__(self, action: int, duration: float, weight: float) -> None:
        super().__init__(action, duration, weight)
    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        mean_speed = super().get_mean_speed()
        return ((self.__CALORIES_MEAN_SPEED_MULTIPLIER * mean_speed
                + self.__CALORIES_MEAN_SPEED_SHIFT) * self.weight
                / self.M_IN_KM * self.duration * self.MIN_IN_H)


class SportsWalking(Training):
    """Тренировка: спортивная ходьба."""
    __CALORIES_WEIGHT_MULTIPLIER = 0.035
    __CALORIES_SPEED_HEIGHT_MULTIPLIER = 0.029
    __KMH_IN_MSEC = 0.278
    __CM_IN_M = 100

    def __init__(self, action: int, duration: float,
                 weight: float, height: float) -> None:
        super().__init__(action, duration, weight)
        self.height = height

    @classmethod
    def verify_height(cls, height):
        if type(height) is not float or height < 0:
            raise TypeError("Рост должен быть типа float и больше 0")

    @property
    def height(self):
        return self.__height

    @height.setter
    def height(self, height):
        self.verify_height(height)
        self.__height = height       

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        return ((self.__CALORIES_WEIGHT_MULTIPLIER * self.weight
                + ((super().get_mean_speed()
                    * self.__KMH_IN_MSEC)**2 / (self.height / self.__CM_IN_M))
                * self.__CALORIES_SPEED_HEIGHT_MULTIPLIER
                * self.weight)
                * self.duration * self.MIN_IN_H)


class Swimming(Training):
    """Тренировка: плавание."""
    LEN_STEP = 1.38
    __CALORIES_WEIGHT_MULTIPLIER = 2
    __CALORIES_MEAN_SPEED_SHIFT = 1.1

    def __init__(self, action: int, duration: float,
                 weight: float, length_pool: float, count_pool: int) -> None:
        super().__init__(action, duration, weight)
        self.length_pool = length_pool
        self.count_pool = count_pool

    @classmethod
    def verify_length_pool(cls, length_pool):
        if type(length_pool) is not float or length_pool < 0:
            raise TypeError("Длина бассейна должна быть типа float и больше 0")

    @classmethod
    def verify_count_pool(cls, count_pool):
        if type(count_pool) is not int or count_pool < 0:
            raise TypeError("Число заплывов должно быть типа int и больше 0")

    @property
    def length_pool(self):
        return self.__length_pool

    @length_pool.setter
    def length_pool(self, length_pool):
        self.verify_length_pool(length_pool)
        self.__length_pool = length_pool  

    @property
    def count_pool(self):
        return self.__count_pool

    @count_pool.setter
    def count_pool(self, count_pool):
        self.verify_count_pool(count_pool)
        self.__count_pool = count_pool 

    def get_mean_speed(self) -> float:
        """Получить среднюю скорость движения."""
        return (self.length_pool * self.count_pool
                / self.M_IN_KM / self.duration)

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        mean_speed = self.get_mean_speed()
        return ((mean_speed + self.__CALORIES_MEAN_SPEED_SHIFT)
                * self.__CALORIES_WEIGHT_MULTIPLIER
                * self.weight * self.duration)


def read_package(workout_type: str, data: list) -> Training:
    """Прочитать данные полученные от датчиков."""
    dict_for_classes: dict[str, Type[Training]] = {'RUN': Running,
                                                   'SWM': Swimming,
                                                   'WLK': SportsWalking}
    if workout_type not in dict_for_classes:
        raise KeyError("Пришел неожиданный тип тренировки")
    return dict_for_classes[workout_type](*data)


def main(training: Training) -> None:
    """Главная функция."""
    info = training.show_training_info()
    print(info.get_message())


if __name__ == '__main__':
    packages = [
        ('SWM', [720, 1.0, 80.0, 25.0, 40]),
        ('RUN', [15000, 1.0, 75.0]),
        ('WLK', [9000, 1.0, 75.0, 180.0]),
    ]

    for workout_type, data in packages:
        training = read_package(workout_type, data)
        main(training)
