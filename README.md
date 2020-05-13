# Сценарий передачи данных IoT платформы Яндекс в Managed PostgreSql через Serverless функцию (IoTCoreAdapter). 
Сценарий состоит из:
<ol>
<li>Python-скрипта с кодом функции <a href=https://github.com/MaxKhlupnov/IoTCoreAdapter/blob/master/iotadapter.py>iotadapter.py</a></li>
<li><a href=https://github.com/MaxKhlupnov/IoTCoreAdapter/tree/master/terraform>Скриптов</a> для terraform, которые разворачивают в указанном <a href=https://cloud.yandex.ru/docs/overview/>Яндекс.Облаке</a> необходимые для работы примера сервисы:
- Managed PostgreSql database
- IoT Core реестр с IoT устройством
- Cloud function и триггеры для сохранения сообщений из сервиса IoT Core в PostgreDatabase
</li>
</ol>
