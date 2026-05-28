from __future__ import annotations

from io import BytesIO, StringIO
from typing import Any, Mapping

import pandas as pd
import requests


class WildberriesReportError(Exception):
    pass


class WildberriesUTMStatsClient:
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

    def __init__(self, token: str | None = None, timeout: int = 60) -> None:
        self.token = token
        self.timeout = timeout

    def get_utm_statistics(
        self,
        url: str,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> requests.Response:
        """Получает ответ сервера с отчетом WB 'Внешний трафик'."""

        response = requests.get(
            url,
            params=params,
            headers=self._make_headers(headers),
            timeout=self.timeout,
        )
        self._handle_response_errors(response)
        return response

    def to_dataframe(
        self,
        response_or_data: requests.Response | bytes | list[dict[str, Any]] | dict[str, Any],
        group_by_utm: bool = False,
        sheet_name: str = "События",
    ) -> pd.DataFrame:
        """Преобразует ответ сервера в DataFrame и считает базовые метрики."""

        df = self._read_dataframe(response_or_data, sheet_name=sheet_name)
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

    def _make_headers(
        self,
        headers: Mapping[str, str] | None,
    ) -> dict[str, str]:
        result = dict(headers or {})
        if self.token:
            result.setdefault("Authorization", self.token)
        return result

    def _handle_response_errors(self, response: requests.Response) -> None:
        if response.ok:
            return

        try:
            error_text = response.json()
        except ValueError:
            error_text = response.text

        raise WildberriesReportError(
            f"WB server error {response.status_code}: {error_text}"
        )

    def _read_dataframe(
        self,
        response_or_data: requests.Response | bytes | list[dict[str, Any]] | dict[str, Any],
        sheet_name: str,
    ) -> pd.DataFrame:
        if isinstance(response_or_data, requests.Response):
            return self._read_response(response_or_data, sheet_name)
        if isinstance(response_or_data, bytes):
            return self._read_bytes(response_or_data, sheet_name)
        if isinstance(response_or_data, list):
            return pd.DataFrame(response_or_data)
        if isinstance(response_or_data, dict):
            return self._read_json_payload(response_or_data)

        raise WildberriesReportError(
            "Нужно передать requests.Response, bytes, list[dict] или dict"
        )

    def _read_response(
        self,
        response: requests.Response,
        sheet_name: str,
    ) -> pd.DataFrame:
        content_type = response.headers.get("Content-Type", "").lower()

        if "json" in content_type:
            return self._read_json_payload(response.json())
        if "csv" in content_type or "text/plain" in content_type:
            return pd.read_csv(StringIO(response.text))

        try:
            return self._read_bytes(response.content, sheet_name)
        except Exception as excel_error:
            try:
                return self._read_json_payload(response.json())
            except ValueError:
                raise WildberriesReportError(
                    f"Не удалось разобрать ответ сервера: {excel_error}"
                )

    def _read_bytes(self, content: bytes, sheet_name: str) -> pd.DataFrame:
        try:
            return pd.read_excel(BytesIO(content), sheet_name=sheet_name)
        except Exception:
            return pd.read_csv(BytesIO(content))

    def _read_json_payload(self, payload: Any) -> pd.DataFrame:
        if isinstance(payload, list):
            return pd.DataFrame(payload)
        if isinstance(payload, dict):
            for key in ("data", "result", "rows", "events", "items"):
                value = payload.get(key)
                if isinstance(value, list):
                    return pd.DataFrame(value)
            return pd.DataFrame([payload])

        raise WildberriesReportError("JSON-ответ должен быть списком или словарем")

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
