# Импортируем необходимые библиотеки
import ollama  # Для взаимодействия с моделью Ollama
import time    # Для добавления задержек в работе программы
import requests  # Для отправки HTTP-запросов к API Яндекс.Поиска

# Создаем класс Assistant, который будет выполнять функции ассистента
class Assistant:
    def __init__(self, ollama_client):
        """
        Инициализация ассистента.
        
        :param ollama_client: Клиент для взаимодействия с моделью Ollama.
        """
        # Системный промт, который задает поведение модели Ollama
        self.system_prompt = (
            "Ты ассистент, отвечай ИСКЛЮЧИТЕЛЬНО НА РУССКОМ ЯЗЫКЕ. "
            "Ты получаешь вопрос и должен указать, есть ли в нём варианты ответа или нет. "
            "Если вариантов ответа в вопросе нет, строго возвращай null. "
            "Если варианты ответа есть"
        )
        # Клиент Ollama для генерации ответов
        self.ollama_client = ollama_client
        # IAM-токен для авторизации в API Яндекс.Поиска
        self.iam_token = "ajeo4583ejjr1g8ti443"  # Замените на ваш реальный IAM-токен
        # URL для отправки запросов к API Яндекс.Поиска
        self.url = "https://searchapi.api.cloud.yandex.net/v2/web/searchAsync"

    def search(self, query):
        """
        Отправляет запрос к API Яндекс.Поиска и возвращает результаты поиска.
        
        :param query: Поисковый запрос.
        :return: Результаты поиска в формате JSON или None в случае ошибки.
        """
        # Заголовки для HTTP-запроса
        headers = {
            "Authorization": f"Bearer {self.iam_token}",  # Авторизация через IAM-токен
            "Content-Type": "application/json"  # Указываем, что данные в формате JSON
        }
        # Тело запроса с параметрами поиска
        payload = {
            "query": {
                "searchType": "SEARCH_TYPE_RU",  # Тип поиска (русский язык)
                "queryText": query,  # Текст запроса
                "familyMode": "FAMILY_MODE_MODERATE",  # Режим фильтрации контента
                "page": "0",  # Номер страницы результатов
                "fixTypoMode": "FIX_TYPO_MODE_ON"  # Исправление опечаток
            },
            "sortSpec": {
                "sortMode": "SORT_MODE_BY_RELEVANCE",  # Сортировка по релевантности
                "sortOrder": "SORT_ORDER_DESC"  # Порядок сортировки (по убыванию)
            },
            "groupSpec": {
                "groupMode": "GROUP_MODE_DEEP",  # Группировка результатов
                "groupsOnPage": "3",  # Количество групп на странице
                "docsInGroup": "3"  # Количество документов в группе
            },
            "maxPassages": "2",  # Максимальное количество пассажей в ответе
            "region": "225",  # Регион поиска (Россия)
            "l10N": "LOCALIZATION_RU",  # Локализация (русский язык)
            "folderId": "AQVNwr3O4LWjl0icHkOEMSchspGFf3jRmGa-ErsV",  # Идентификатор каталога
            "responseFormat": "FORMAT_HTML",  # Формат ответа (HTML)
            "userAgent": ""  # User-Agent (не используется)
        }

        try:
            # Отправляем POST-запрос к API Яндекс.Поиска
            response = requests.post(self.url, headers=headers, json=payload)
            response.raise_for_status()  # Проверяем, не было ли ошибок в запросе
            return response.json()  # Возвращаем результат в формате JSON
        except requests.exceptions.RequestException as e:
            # В случае ошибки выводим сообщение и возвращаем None
            print(f"Ошибка при выполнении запроса к поисковому API: {e}")
            return None

    def generate_response(self, prompt):
        """
        Генерирует ответ на вопрос пользователя с помощью модели Ollama.
        
        :param prompt: Вопрос пользователя.
        :return: Сгенерированный ответ или None в случае ошибки.
        """
        try:
            # Отправляем запрос к модели Ollama
            response = self.ollama_client.chat(model='qwen2.5', messages=[
                {'role': 'system', 'content': self.system_prompt},  # Системный промт
                {'role': 'user', 'content': prompt}  # Вопрос пользователя
            ])
            return response['message']['content']  # Возвращаем сгенерированный ответ
        except Exception as e:
            # В случае ошибки выводим сообщение и возвращаем None
            print(f"Ошибка при генерации ответа с помощью Ollama: {e}")
            return None

    def run(self):
        """
        Основной цикл работы ассистента.
        Ассистент ожидает ввода вопроса от пользователя и обрабатывает его.
        """
        while True:
            # Запрашиваем ввод от пользователя
            user_input = input("Введите ваш вопрос: ").strip()
            # Если пользователь ввел команду для выхода, завершаем работу
            if user_input.lower() in ["выход", "exit", "quit"]:
                print("Завершение работы ассистента.")
                break

            # Генерируем предварительный ответ с помощью модели Ollama
            preanswer = self.generate_response(user_input)
            if preanswer is None:  # Если ответ не был сгенерирован, пропускаем итерацию
                continue

            # Проверяем, есть ли варианты ответа в вопросе
            if preanswer.strip().lower() == "null":
                print("Ответ: null (вариантов ответа нет)")
            else:
                # Если варианты ответа есть, выполняем поиск через API Яндекс.Поиска
                search_result = self.search(preanswer)
                if search_result:
                    print("Результаты поиска:", search_result)
                else:
                    print("Не удалось получить результаты поиска.")

            # Добавляем задержку перед следующим запросом
            time.sleep(1)

# Точка входа в программу
if __name__ == "__main__":
    # Создаем клиент Ollama
    ollama_client = ollama.Client()
    # Создаем экземпляр ассистента
    assistant = Assistant(ollama_client)
    # Запускаем основной цикл работы ассистента
    assistant.run()