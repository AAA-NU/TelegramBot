from typing import Optional, List, Dict, Any
import requests
from dataclasses import dataclass


@dataclass
class User:
    """Модель пользователя"""
    tgID: str
    role: str
    name: str
    language: str


@dataclass
class SaveUserRequest:
    """Модель запроса для создания пользователя"""
    tgID: str
    language: str


@dataclass
class ApiResponse:
    """Базовая модель ответа API"""
    status: str
    message: Optional[str] = None


class BackendUsersController:
    """Контроллер для работы с Backend Users Service API"""

    base_url: str = "/api"

    @classmethod
    def set_base_url(cls, url: str) -> None:
        """Установить базовый URL для API"""
        cls.base_url = url.rstrip('/')

    @classmethod
    def ping(cls) -> Dict[str, str]:
        """
        Проверка доступности сервера

        Returns:
            Dict[str, str]: Ответ сервера с сообщением

        Raises:
            requests.RequestException: При ошибке запроса
        """
        response = requests.get(f"{cls.base_url}/ping")
        response.raise_for_status()
        return response.json()

    @classmethod
    def get_users(cls, role: Optional[str] = None) -> List[User]:
        """
        Получить список пользователей

        Args:
            role (Optional[str]): Фильтр по роли пользователя

        Returns:
            List[User]: Список пользователей

        Raises:
            requests.RequestException: При ошибке запроса
        """
        params = {}
        if role is not None:
            params['role'] = role

        response = requests.get(f"{cls.base_url}/users/", params=params)
        response.raise_for_status()

        users_data = response.json()
        return [User(**user_data) for user_data in users_data]

    @classmethod
    def create_user(cls, tgID: str, language: str) -> ApiResponse:
        """
        Создать пользователя

        Args:
            tgID (str): Telegram ID пользователя
            language (str): Язык пользователя

        Returns:
            ApiResponse: Статус создания пользователя

        Raises:
            requests.RequestException: При ошибке запроса
        """
        request_data = {
            "tgID": tgID,
            "language": language
        }

        response = requests.post(
            f"{cls.base_url}/users/",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()

        response_data = response.json()
        return ApiResponse(status=response_data["status"])

    @classmethod
    def get_user_by_tg_id(cls, tgID: str) -> User:
        """
        Получить пользователя по Telegram ID

        Args:
            tgID (str): Telegram ID пользователя

        Returns:
            User: Данные пользователя

        Raises:
            requests.RequestException: При ошибке запроса
        """
        response = requests.get(f"{cls.base_url}/users/{tgID}")
        response.raise_for_status()

        user_data = response.json()
        return User(**user_data)

    @classmethod
    def update_user(
        cls,
        tgID: str,
        role: Optional[str] = None,
        language: Optional[str] = None
    ) -> ApiResponse:
        """
        Обновить пользователя

        Args:
            tgID (str): Telegram ID пользователя
            role (Optional[str]): Новая роль пользователя
            language (Optional[str]): Новый язык пользователя

        Returns:
            ApiResponse: Статус обновления пользователя

        Raises:
            requests.RequestException: При ошибке запроса
        """
        params = {}
        if role is not None:
            params['role'] = role
        if language is not None:
            params['language'] = language

        response = requests.put(f"{cls.base_url}/users/{tgID}", params=params)
        response.raise_for_status()

        response_data = response.json()
        return ApiResponse(status=response_data["status"])

    @classmethod
    def delete_user(cls, tgID: str, fromUserID: str) -> ApiResponse:
        """
        Удалить пользователя (только админ)

        Args:
            tgID (str): Telegram ID удаляемого пользователя
            fromUserID (str): Telegram ID пользователя, выполняющего удаление

        Returns:
            ApiResponse: Статус удаления пользователя

        Raises:
            requests.RequestException: При ошибке запроса (включая 403 Forbidden)
        """
        params = {"fromUserID": fromUserID}

        response = requests.delete(
            f"{cls.base_url}/users/{tgID}", params=params)
        response.raise_for_status()

        response_data = response.json()
        return ApiResponse(status=response_data["status"])


BackendUsersController.set_base_url("http://93.189.231.250:8080/api")

# Пример использования:
if __name__ == "__main__":
    # Установка базового URL
    BackendUsersController.set_base_url("http://93.189.231.250:8080/api")

    all_users = BackendUsersController.get_users()
    print(all_users)
