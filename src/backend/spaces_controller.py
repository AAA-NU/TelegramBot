import requests
from dataclasses import dataclass
from datetime import date


@dataclass
class RoomModel:
    """Модель комнаты"""
    id: str
    is_booked: bool
    booked_by: str


@dataclass
class CoworkingModel:
    """Модель коворкинга"""
    id: str
    booked_time: list[str]


@dataclass
class CoworkingMetaResponse:
    """Ответ с доступным временем коворкинга"""
    id: str
    available_times: list[str]


@dataclass
class AddBookingTime:
    """Модель для добавления времени бронирования"""
    time: str


class SpacesApiController:
    """Контроллер для работы с Spaces API"""

    base_url: str = "/api"

    @classmethod
    def set_base_url(cls, url: str) -> None:
        """Установить базовый URL для API"""
        cls.base_url = url.rstrip('/')

    @classmethod
    def ping(cls) -> dict[str, str]:
        """
        Проверка доступности сервера

        Returns:
            dict[str, str]: Ответ сервера с сообщением

        Raises:
            requests.RequestException: При ошибке запроса
        """
        response = requests.get(f"{cls.base_url}/ping")
        response.raise_for_status()
        return response.json()

    @classmethod
    def get_rooms(cls) -> list[RoomModel]:
        """
        Получить список всех комнат

        Returns:
            List[RoomModel]: Список комнат

        Raises:
            requests.RequestException: При ошибке запроса
        """
        response = requests.get(f"{cls.base_url}/rooms/")
        response.raise_for_status()

        rooms_data = response.json()
        return [RoomModel(**room_data) for room_data in rooms_data]

    @classmethod
    def update_room_booking(
        cls,
        room_id: str,
        is_booked: bool,
        booked_by: str
    ) -> RoomModel:
        """
        Обновить бронирование комнаты

        Args:
            room_id (str): ID комнаты
            is_booked (bool): Статус бронирования
            booked_by (str): Кем забронирована

        Returns:
            RoomModel: Обновленная комната

        Raises:
            requests.RequestException: При ошибке запроса
        """
        request_data = {
            "id": room_id,
            "is_booked": is_booked,
            "booked_by": booked_by
        }

        response = requests.put(
            f"{cls.base_url}/rooms/",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()

        room_data = response.json()
        return RoomModel(**room_data)

    @classmethod
    def get_room_by_id(cls, room_id: str) -> RoomModel:
        """
        Получить информацию о комнате по ID

        Args:
            room_id (str): ID комнаты

        Returns:
            RoomModel: Данные комнаты

        Raises:
            requests.RequestException: При ошибке запроса (включая 404)
        """
        response = requests.get(f"{cls.base_url}/rooms/{room_id}")
        response.raise_for_status()

        room_data = response.json()
        return RoomModel(**room_data)

    @classmethod
    def get_coworkings(cls) -> list[CoworkingModel]:
        """
        Получить список всех коворкингов

        Returns:
            List[CoworkingModel]: Список коворкингов

        Raises:
            requests.RequestException: При ошибке запроса
        """
        response = requests.get(f"{cls.base_url}/coworkings/")
        response.raise_for_status()

        coworkings_data = response.json()
        return [CoworkingModel(**coworking_data) for coworking_data in coworkings_data]

    @classmethod
    def get_coworking_available_time(
        cls,
        coworking_id: str,
        date_param: date
    ) -> CoworkingMetaResponse:
        """
        Получить доступное время для коворкинга по дате

        Args:
            coworking_id (str): ID коворкинга
            date_param (date): Дата для проверки доступности

        Returns:
            CoworkingMetaResponse: Доступное время

        Raises:
            requests.RequestException: При ошибке запроса (включая 400, 404)
        """
        params = {"date": date_param.isoformat()}

        response = requests.get(
            f"{cls.base_url}/coworkings/{coworking_id}",
            params=params
        )
        response.raise_for_status()

        response_data = response.json()
        return CoworkingMetaResponse(**response_data)

    @classmethod
    def add_coworking_booking_time(
        cls,
        coworking_id: str,
        time: str
    ) -> AddBookingTime:
        """
        Добавить новое забронированное время для коворкинга

        Args:
            coworking_id (str): ID коворкинга
            time (str): Время бронирования

        Returns:
            AddBookingTime: Добавленное время

        Raises:
            requests.RequestException: При ошибке запроса (включая 400, 409)
        """
        request_data = {"time": time}

        response = requests.post(
            f"{cls.base_url}/coworkings/{coworking_id}",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()

        response_data = response.json()
        return AddBookingTime(**response_data)


# Пример использования:
if __name__ == "__main__":
    from datetime import date

    # Установка базового URL
    SpacesApiController.set_base_url("http://93.189.231.250:8081/api")

    all_rooms = SpacesApiController.get_rooms()

    coworkings = SpacesApiController.get_coworkings()
    print(coworkings, all_rooms)
