# Сценарий передачи данных IoT платформы Яндекс в Managed PostgreSql через Serverless функцию (IoTCoreAdapter). 
Сценарий состоит из:
- Python-скрипта с кодом функции <a href=https://github.com/MaxKhlupnov/IoTCoreAdapter/blob/master/iotadapter.py>iotadapter.py</a>
- <a href=>Скриптов</a> для terraform, которые разворачивают в указанном <a href=>Яндекс.Облаке</a> необходимые для работы примера сервисы:
<ol>
<li>- Managed PostgreSql database</li>
<li>- IoT Core реестр с IoT устройством</li>
<li>- Cloud function и триггеры для сохранения сообщений из сервиса IoT Core в PostgreDatabase</li>
</ol>
