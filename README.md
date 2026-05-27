# api_wb

Простой Python-клиент для получения статистики продаж Wildberries через API и
перевода ответа в `pandas.DataFrame`.

## Установка

```bash
pip install -e .
```

## Зависимости

- `requests`
- `pandas`

## Использование

```python
from wb_utm_statistics import WildberriesStatsClient

client = WildberriesStatsClient(token="ТВОЙ_WB_API_ТОКЕН")

data = client.get_sales_statistics(
    date_from="2026-05-01",
    flag=1,
)

df = client.to_dataframe(data)
print(df.head())
```

## Параметры

`date_from` — дата начала выгрузки. Можно передать строку, `date` или
`datetime`.

`flag`:

- `0` — получить данные, измененные с `date_from`;
- `1` — получить все данные за указанную дату.

## Ошибки API

Если Wildberries API возвращает ошибку, клиент выбрасывает
`WildberriesAPIError` с кодом ответа и текстом ошибки.
