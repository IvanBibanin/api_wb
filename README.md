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

client = WildberriesUTMStatsClient()

response = client.get_utm_statistics(
    begin_date="2026-04-28",
    end_date="2026-05-28",
    cookies={
        # cookies авторизованной сессии cmp.wildberries.ru
    },
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

Кнопка `Скачать в XLS` на странице `https://cmp.wildberries.ru/external-traffic`
вызывает endpoint:

```text
GET https://cmp.wildberries.ru/api/v5/events-external-traffic/xls
```

Параметры:

- `beginDate`
- `endDate`

Этот endpoint требует авторизованную сессию кабинета WB. Обычный WB API-токен
может не подойти, потому что метод не описан как публичный WB API endpoint.

## Ошибки

Если сервер вернул ошибку, ответ не удалось разобрать или в отчете нет нужных
колонок, клиент выбрасывает `WildberriesReportError`.
