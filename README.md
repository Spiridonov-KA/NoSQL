# Проект по NoSQL
## Задача 
Задача - разработать прототип распределенного приложения для бронирования комнат.
## Работу выполнил:
Спиридонов К. А. М8О-107М-19
## Сценарии
- Поиск свободных комнат (Elastic Search). Поиск по описанию, адресу и датам бронирования. Для удобства поиска по датам, при сохранении брони в MongoDB в ElasticSearch можно индексировать свободные даты.
 - Бронирование комнаты. Клиент после выбора комнаты и дат бронирования, нажимает "бронировать", бронь сохраняется в MongoDB, комната блокируется.
## План работы
 * Обсудить предметную область, детально описать модель хранимых данных.
 * Разработка
    - Заполнить тестовыми данными MongoDB (Клиент, комната)
    - Разработать класс-сервис бронирования
    - Расширить сервис бронирования индексированием данных в ElasticSearch
 * Интеграция и тестирование
    - Подготовить данные (порядка десятков тысяч клиентов, десятков тысяч комнат, миллионов броней)
    - Источник данных:
        - http://data.insideairbnb.com/united-kingdom/england/london/2017-03-04/data/listings.csv.gz
        - Клиентов - пользователей stackoverflow
        - Брони - сгенерировать
 * Функциональное тестирование и исправление ошибок
 * Протестировать поведение системы при отключении одного узла
## Ключевые сущности:
 * Клиент 
    - id
    - name
 * Комната
    - id
    - address
    - description
    - attributes
 * Бронь
    - id_room
    - id_client
    - booking date
    - booking status
  
## Используемые технологии
- python в качестве основного языка программирования
- javascript для скриптов в mongodb
- fastapi для rest-api приложения
- mongodb как основное хранилище данных
- elasticsearch для полнотекстового поиска
- memcached в качестве кэширования
- docker для виртуализации
- docker-compose для оркестрации и запуска кластера
- nginx в качестве балансировщика нагрузки


## Запуск кластера в docker
Запуск:
```
docker compose up --build -d
```
## Архитектура кластера
![alt text](images/architecture.png "Architecture")
