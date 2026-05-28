# api_wb

Python-клиент для скачивания отчета Wildberries **Внешний трафик** и получения
статистики по UTM-меткам в `pandas.DataFrame`.

## Установка

```bash
pip install -e .
```

## Зависимости

- `pandas`
- `openpyxl`
- `requests`

## Использование

Класс сам скачивает XLS-отчет из WB. Для доступа нужна cookie авторизованной
сессии `cmp.wildberries.ru`.

```python
from wb_utm_statistics import WildberriesUTMStatsClient

cookie = "сюда_вставить_cookie_из_браузера"

client = WildberriesUTMStatsClient(cookie=cookie)

data = client.get_utm_statistics(
    begin_date="2026-04-28",
    end_date="2026-05-28",
)

df = client.to_dataframe(data)
print(df.head())
```

## Сохранить XLS

```python
path = client.download_utm_report(
    begin_date="2026-04-28",
    end_date="2026-05-28",
    save_path="/Users/ivan/Downloads/Внешний трафик.xlsx",
)

print(path)
```

## Сводка по UTM

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

## Endpoint

Кнопка `Скачать в XLS` на странице `https://cmp.wildberries.ru/external-traffic`
вызывает:

```text
GET https://cmp.wildberries.ru/api/v5/events-external-traffic/xls
```

Параметры:

- `beginDate`
- `endDate`

Если WB возвращает `401` или `403`, значит cookie не передана или сессия
истекла.
