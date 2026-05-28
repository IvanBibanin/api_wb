# api_wb

Простой Python-клиент для обработки отчета Wildberries **Внешний трафик** и
получения статистики по UTM-меткам в `pandas.DataFrame`.

## Установка

```bash
pip install -e .
```

## Зависимости

- `pandas`
- `openpyxl`

## Использование

```python
from wb_utm_statistics import WildberriesUTMStatsClient

client = WildberriesUTMStatsClient()

data = client.get_utm_statistics("/Users/ivan/Downloads/Внешний трафик.xlsx")
df = client.to_dataframe(data)

print(df.head())
```

## Сводка по UTM

Чтобы получить агрегированную статистику по UTM-меткам:

```python
utm_df = client.to_dataframe(data, group_by_utm=True)

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

## Ошибки

Если файл не найден, имеет неверный формат или в отчете нет нужных колонок,
клиент выбрасывает `WildberriesReportError`.
