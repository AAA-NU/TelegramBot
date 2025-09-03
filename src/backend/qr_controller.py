import requests
from dataclasses import dataclass


@dataclass
class VerifyResponse:
    """Модель ответа верификации"""
    uuid: str
    valid: bool


class VerifyApiController:
    """Контроллер для работы с Verify API"""

    base_url: str = "/api"

    @classmethod
    def set_base_url(cls, url: str) -> None:
        """Установить базовый URL для API"""
        cls.base_url = url.rstrip('/')

    @classmethod
    def verify_uuid(cls, uuid: str) -> VerifyResponse:
        """
        Проверить валидность UUID

        Args:
            uuid (str): UUID для проверки

        Returns:
            VerifyResponse: Результат проверки с uuid и статусом valid

        Raises:
            requests.RequestException: При ошибке запроса
        """
        response = requests.post(f"{cls.base_url}/verify/{uuid}")
        response.raise_for_status()

        response_data = response.json()
        return VerifyResponse(**response_data)


VerifyApiController.set_base_url("http://93.189.231.250:8082/api")

# Пример использования:
if __name__ == "__main__":
    # Установка базового URL
    VerifyApiController.set_base_url("http://93.189.231.250:8082/api")

    # Проверка UUID
    verify_result = VerifyApiController.verify_uuid(
        "490ebfb4-eae7-4b7c-864e-cc47a93f4b2b"
    )
    print(f"UUID: {verify_result.uuid}")
    print(f"Валиден: {verify_result.valid}")
