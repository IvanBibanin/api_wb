# api_wb

Простой Python-клиент для обработки серверного ответа Wildberries **Внешний
трафик** и получения статистики по UTM-меткам в `pandas.DataFrame`.

Клиент не сохраняет отчет на локальный компьютер: Excel/CSV/JSON читаются прямо
из HTTP-ответа в памяти.

## Установка

```bash
pip install -e .
```

## Зависимости

- `pandas`
- `openpyxl`
- `requests`

## Использование

```python
from wb_utm_statistics import WildberriesUTMStatsClient

client = WildberriesUTMStatsClient(token="ТВОЙ_ТОКЕН")

response = client.get_utm_statistics(
    url="URL_ОТЧЕТА_ВНЕШНИЙ_ТРАФИК",
)

df = client.to_dataframe(response)
print(df.head())
```

## Сводка по UTM

Чтобы получить агрегированную статистику по UTM-меткам:

```python
utm_df = client.to_dataframe(response, group_by_utm=True)

print(utm_df.head())
```

В сводку входят:

- `utm_source`
- `utm_medium`
- `utm_campaign`
- `utm_term`
- `utm_content`
- `Переходы`
- `Заказанные товары`
- `Стоимость заказов (руб)`
- `Конверсия в заказ (%)`
- `Средний заказ (руб)`

## Важно

В публичной документации WB API нет отдельного официального метода для отчета
`Внешний трафик` по UTM. Поэтому в `url` нужно передать адрес серверной выгрузки,
если он доступен в кабинете или во внутреннем сервисе.

## Ошибки

Если сервер вернул ошибку, ответ не удалось разобрать или в отчете нет нужных
колонок, клиент выбрасывает `WildberriesReportError`.
