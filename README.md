# Задание для DE

ПО, ЯП и их библиотеки, нотации на ваше усмотрение.
Вы вправе выполнить любое количество заданий.
Оптимальный срок выполнения - 3 дня.

## Задания

1. Продумайте обработку, хранение, преобразование данных (в т.ч. для нормализации) и набор витрин + ПО которое собираетесь использовать. Нарисуйте диаграммы для ETL (DataFlow) и ER в DWH. Используйте данные из 3-х датасетов data.mos.ru и из Википедии.
2. Предложите набор показателей и дашбордов для контроля качества данных.
3. Сделайте выводы о качестве данных и предложите пути его улучшения.

## Данные

Портал открытых данных правительства Москвы data.mos.ru
- Велопарковки. датасет № 916
- Залы спортивные. датасет № 60622
- Площадки для выгула собак. датасет № 2663

Википедия — свободная энциклопедия wikipedia.org
[Население районов](https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D1%80%D0%B0%D0%B9%D0%BE%D0%BD%D0%BE%D0%B2_%D0%B8_%D0%BF%D0%BE%D1%81%D0%B5%D0%BB%D0%B5%D0%BD%D0%B8%D0%B9_%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D1%8B)


## 1

В файлах:
- main.py - реализовано создание базы stone.db на sqlite3 на основе всех данных указанных в задании
- models.py - формализация моделей таблиц для базы данных

Использовались следующие библиотеки:
- peewee - ORM, с помощью которой реализовано создание моделей и взаимодействие с бд (можно было использовать sqlalchemy, alembic)
- pandas
- requests
- logging
- ssl
- re

Скрипт сначала создает бд на sqlite3 со всеми таблицами и взаимосвязями согласно описанной модели, затем парсит данные таблицы из Википедии, преобразовывает и сохраняет необходимые данные в таблицы, после по очередности забирает все данные по API data.mos.ru с каждого датасета пачками по 500 записей и так же преобразовывает, сохраняет данные в таблицы.

В качестве дополнительного ПО можно использовать airflow в дальнейшем для апдейта данных.
Датасеты согласно своим пасспортам данных обновляются - ежеквартально, ежемесячно и еженедельно. Соответственно можно настроить апдейт этих данных и проверку текущих согласно каждому периоду для датасета.

[ETL диаграмма с AirFlow](https://github.com/kp042/tz_stone/blob/main/etl_stone.png)

Данные с wiki можно скачать, преобразовать и сохранить единожды. А сами датасеты можно поставить на периодические процессы.

[Ссылка на ER диаграмму](https://github.com/kp042/tz_stone/blob/main/er_stone.png)

На данный момент, время, к сожалению, для выполнения задания подошло к концу, но на мой взгляд можно было еще доработать таблицу по Спортивным залам. Только сейчас обнаружил, что в таблице некоторые данные дублируются, поскольку сами данные в данном датасете отталкиваются не от спортивного заведения, а от спортивного зала и соответственно присутствует избыточность в таблице, связанная непосредственно со спортивным заведением, все это можно еще оптимизировать.

## 2 и 3

По поводу качества данных в датасетах стоит отметить следующие моменты:

- Поскольку данные на русском языке, то необходимо учитывать нюансы его использования. А именно возникали такие ситуации, когда в одном и том же слове по смыслу использовались либо буква "е", либо буква "ё" и это создавало проблему в избыточности итоговых данных.
- Некоторые url, указанные в качестве вебсайтов для спортивных залов были нерабочие. В данном случае была реализована функция в скрипте для проверки валидности доступа к url сайта. В данном случае я вынес все сайты в отдельную таблицу, где есть дополнительный атрибут negotiability, который указывает резолвится ли данный url. Можно сделать отдельный SQL запрос для дашборда нерабочих сайтов организаций.
- В качестве дополнительной проверки качества данных можно сделать проверку на дубликаты данных и отсутствия каких либо значений (Null значений), чтобы подсвечивать такие моменты в отдельных дашбордах. Так же выводить контрольные суммы записей по DWH и по API (get count запрос)
- Столкнулся с проблемой несоответствия используемых типов данных по некоторым атрибутам. Например, в поле Elements (Площадки для выгула собак) для большинства записей использовался в качестве типа данных список, но в случае если был один элемент - то он указывался не в списке, а в качестве строки.
- В датасете "велосипедных парковок" для каждой записи в качестве подведомственной организации была указана одна и та же организация "ГКУ Центр организации дорожного движения Правительства Москвы" с одним и тем же телефоном, но указана была в трех вариантах: один нормальный полный вариант, второй неполный вариант названия, а в третьем случае вместо названия организации был написан адрес. В данном случае, мне пришлось захардкодить этот (что не очень хорошо в целом и нужно еще подумать как с этим быть).
- Для районов использовалось по разному написание их обозначения. Иногда "район" или "поселение" могли написать в начале, а иногда в конце. С помощью регулярных выражений решил проблему со сопоставлением данных относительно тех, что были получены через Wiki. 
