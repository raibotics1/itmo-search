# FastAPI Baseline Service

Это пример базового приложения, которое реализует API для получения запроса и возврата ответа. Приложение написано на FastAPI и разворачивается с помощью Docker Compose.

## Структура проекта

- `main.py`: Основной файл приложения, содержащий логику API.
- `llm.py`: Файл с моделью ИИ, к которой будет обращаться приложение.
- `Dockerfile`: Файл для создания Docker-образа приложения.
- `docker-compose.yml`: Файл для запуска приложения с помощью Docker Compose.
- `requirements.txt`: Список зависимостей Python.
- `README.md`: Этот файл с описанием проекта.

## Сборка и запуск

Для запуска приложения выполните следующую команду:

```bash
docker-compose up -d

Эта команда соберёт Docker-образ и запустит контейнер. После успешного запуска приложение будет доступно по адресу http://localhost:8080.

Проверка работы
Чтобы проверить работу API, отправьте POST-запрос на эндпоинт /api/request. Например, с помощью curl:

bash
Copy
curl --location --request POST 'http://localhost:8080/api/request' \
--header 'Content-Type: application/json' \
--data-raw '{
  "query": "В каком городе находится главный кампус Университета ИТМО?\n1. Москва\n2. Санкт-Петербург\n3. Екатеринбург\n4. Нижний Новгород",
  "id": 1
}'
В ответ вы получите JSON следующего вида:

json
Copy
{
  "id": 1,
  "answer": 1,
  "reasoning": "Из информации на сайте",
  "sources": [
    "https://itmo.ru/ru/",
    "https://abit.itmo.ru/"
  ]
}
id будет соответствовать тому, что вы отправили в запросе.

answer (в базовой версии) всегда будет 1.

Кастомизация
Чтобы изменить логику ответа, отредактируйте функцию handle_request в файле main.py. Если вам нужно использовать дополнительные библиотеки, добавьте их в requirements.txt и пересоберите Docker-образ.

Чтобы остановить сервис, выполните команду:

bash
Copy
docker-compose down
