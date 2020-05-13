# Сценарий передачи данных IoT платформы Яндекс в Managed PostgreSql через Serverless функцию (IoTCoreAdapter). 
Сценарий состоит из:
<ol>
<li>Python-скрипта с кодом функции <a href=https://github.com/MaxKhlupnov/IoTCoreAdapter/blob/master/iotadapter.py>iotadapter.py</a></li>
<li><a href=https://github.com/MaxKhlupnov/IoTCoreAdapter/tree/master/terraform>Скриптов</a> для terraform, которые разворачивают в указанном <a href=https://cloud.yandex.ru/docs/overview/>Яндекс.Облаке</a> необходимые для работы примера сервисы:
  <div>- Managed PostgreSql database<div>
  <div>- IoT Core реестр с IoT устройством</div>
  <div>- Cloud function и триггеры для сохранения сообщений из сервиса IoT Core в PostgreDatabase</div>
</li> 
  <li>Консольного <a href=https://github.com/MaxKhlupnov/IoTSimulator>приложения IoTSimulator</a>, которое эммулирует работу IoT устройства и предает данные в сервис IoT Core</li>
</ol>
