# Http-based robot-client communication

### Для запуска тестовой системы Web->Topic и Topic->Web
1) Импортируем в Postman [коллекцию](postman/Clap.postman_collection_last.json) 
и [окружение](postman/Clap.postman_environment_last.json).

2) Запускаем [скрипт](sync_api_check_wheels.py) для прослушки тестового топика `wheels`:
        
        python sync_api_check_wheels.py
        
    Операция блокирует ввод/вывод
3) Запускаем в другом терминале [скрипт](sync_api_pub_mass.py) для публикации в тестовый топик `mass`:

        python sync_api_pub_mass.py
        
4) Запускаем [Web-Topic интерфейс](sync_api_to_pub.py):

        python sync_api_to_pub.py
        
5) Теперь посылаем из Postman сообщение в топик wheels (ручка `Messages/PubToTopic`).
    Убеждаемся, что во вкладке `sync_api_check_wheels.py` появилось сообщение.
    
6) Подписываемся на топик `mass` из интернета, для этого в Postman дёргаем ручку
    `Messages/Supscribe to Topiс` .
    
7) Посылаем из вкладки `sync_api_pub_mass.py` какой-нибудь `float`. Проверяем, что в интернет долетело: 
    ручка Postman `Messages/List Messages` (отключить галочку `after` вкладки `params` для первого раза).
    
    
Всё работает!