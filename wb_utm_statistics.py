from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd
import requests


class WildberriesAPIError(Exception):
    pass


class WildberriesStatsClient:
    SALES_URL = "https://statistics-api.wildberries.ru/api/v1/supplier/sales"

    def __init__(self, token: str, timeout: int = 30) -> None:
        self.token = token
        self.timeout = timeout

    def get_sales_statistics(
        self,
        date_from: str | date | datetime,
        flag: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Получает статистику продаж WB.

        date_from:
            - '2026-05-01' или '2026-05-01T00:00:00'
        flag:
            - 0: данные, измененные с date_from
            - 1: все данные за указанную дату
        """

        response = requests.get(
            self.SALES_URL,
            headers={"Authorization": self.token},
            params={
                "dateFrom": self._format_date(date_from),
                "flag": flag,
            },
            timeout=self.timeout,
        )
        self._handle_response_errors(response)
        return response.json()

    def to_dataframe(self, data: list[dict[str, Any]]) -> pd.DataFrame:
        """Преобразует ответ WB API в pandas DataFrame."""

        df = pd.DataFrame(data)
        if df.empty:
            return df

        for column in ("date", "lastChangeDate", "cancelDate"):
            if column in df.columns:
                df[column] = pd.to_datetime(df[column], errors="coerce")

        if "saleID" in df.columns:
            df["is_return"] = df["saleID"].astype(str).str.startswith("R")

        return df

    def _handle_response_errors(self, response: requests.Response) -> None:
        if response.ok:
            return

        try:
            error_text = response.json()
        except ValueError:
            error_text = response.text

        raise WildberriesAPIError(
            f"WB API error {response.status_code}: {error_text}"
        )

    @staticmethod
    def _format_date(value: str | date | datetime) -> str:
        if isinstance(value, datetime):
            return value.isoformat(timespec="seconds")
        if isinstance(value, date):
            return value.isoformat()
        return value
