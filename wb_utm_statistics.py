from __future__ import annotations

from datetime import date, datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Mapping

import pandas as pd
import requests


class WildberriesReportError(Exception):
    pass


class WildberriesUTMStatsClient:
    UTM_REPORT_URL = "https://cmp.wildberries.ru/api/v5/events-external-traffic/xls"
    UTM_COLUMNS = [
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
    ]
    METRIC_COLUMNS = [
        "Переходы",
        "Заказанные товары",
        "Стоимость заказов (руб)",
    ]
    REQUIRED_COLUMNS = [
        "Дата",
        *UTM_COLUMNS,
        *METRIC_COLUMNS,
        "Платформа",
    ]

    def __init__(
        self,
        cookie: str | None = None,
        cookies: Mapping[str, str] | None = None,
        timeout: int = 60,
    ) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": (
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet, application/octet-stream, */*"
                ),
                "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
                "Referer": "https://cmp.wildberries.ru/external-traffic",
                "User-Agent": "Mozilla/5.0",
            }
        )
        if cookie:
            self.session.headers["Cookie"] = cookie
        if cookies:
            self.session.cookies.update(cookies)

    def download_utm_report(
        self,
        begin_date: str | date | datetime,
        end_date: str | date | datetime,
        save_path: str | Path = "Внешний трафик.xlsx",
    ) -> Path:
        """Скачивает XLS-отчет WB 'Внешний трафик' на локальный компьютер."""

        response = self._get_report_response(begin_date, end_date)
        path = Path(save_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(response.content)
        return path

    def get_utm_statistics(
        self,
        begin_date: str | date | datetime,
        end_date: str | date | datetime,
        sheet_name: str = "События",
    ) -> list[dict[str, Any]]:
        """Скачивает XLS-отчет WB в память и возвращает список строк."""

        response = self._get_report_response(begin_date, end_date)
        df = self._read_excel_response(response, sheet_name=sheet_name)
        return df.to_dict("records")

    def to_dataframe(
        self,
        data: list[dict[str, Any]],
        group_by_utm: bool = False,
    ) -> pd.DataFrame:
        """Преобразует строки отчета в DataFrame и считает базовые метрики."""

        df = pd.DataFrame(data)
        if df.empty:
            return df

        missing_columns = [
            column for column in self.REQUIRED_COLUMNS if column not in df.columns
        ]
        if missing_columns:
            raise WildberriesReportError(
                f"В отчете нет нужных колонок: {missing_columns}"
            )

        df["Дата"] = pd.to_datetime(df["Дата"], errors="coerce")

        for column in self.METRIC_COLUMNS:
            df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

        if group_by_utm:
            df = (
                df.groupby(self.UTM_COLUMNS, dropna=False, as_index=False)[
                    self.METRIC_COLUMNS
                ]
                .sum()
                .sort_values("Переходы", ascending=False)
                .reset_index(drop=True)
            )

        return self._add_calculated_columns(df)

    def _get_report_response(
        self,
        begin_date: str | date | datetime,
        end_date: str | date | datetime,
    ) -> requests.Response:
        params = {
            "beginDate": self._format_date(begin_date),
            "endDate": self._format_date(end_date),
        }

        try:
            response = self.session.get(
                self.UTM_REPORT_URL,
                params=params,
                timeout=self.timeout,
            )
        except requests.RequestException as error:
            raise WildberriesReportError(f"Не удалось скачать отчет WB: {error}")

        self._handle_response_errors(response)
        return response

    def _handle_response_errors(self, response: requests.Response) -> None:
        if response.ok:
            return

        if response.status_code in {401, 403}:
            raise WildberriesReportError(
                "WB не отдал отчет: нужна cookie авторизованной сессии "
                "cmp.wildberries.ru"
            )

        raise WildberriesReportError(
            f"WB вернул ошибку {response.status_code}: {response.text[:500]}"
        )

    @staticmethod
    def _format_date(value: str | date | datetime) -> str:
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        return value

    def _read_excel_response(
        self,
        response: requests.Response,
        sheet_name: str,
    ) -> pd.DataFrame:
        try:
            return pd.read_excel(BytesIO(response.content), sheet_name=sheet_name)
        except Exception as error:
            content_type = response.headers.get("Content-Type", "")
            raise WildberriesReportError(
                "Не удалось прочитать XLS-отчет из ответа WB. "
                f"Content-Type: {content_type}. Ошибка: {error}"
            )

    def _add_calculated_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        clicks = df["Переходы"].astype(float)
        orders = df["Заказанные товары"].astype(float)
        amount = df["Стоимость заказов (руб)"].astype(float)

        df["Конверсия в заказ (%)"] = (
            orders.div(clicks.where(clicks != 0)).mul(100).fillna(0).round(2)
        )
        df["Средний заказ (руб)"] = (
            amount.div(orders.where(orders != 0)).fillna(0).round(2)
        )

        return df


WildberriesStatsClient = WildberriesUTMStatsClient
