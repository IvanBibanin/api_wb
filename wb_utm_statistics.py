from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


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

    def get_utm_statistics(
        self,
        report_path: str | Path,
        sheet_name: str = "События",
    ) -> list[dict[str, Any]]:
        """Читает Excel-отчет WB 'Внешний трафик' и возвращает список строк."""

        path = Path(report_path).expanduser()
        self._handle_file_errors(path)

        try:
            df = pd.read_excel(path, sheet_name=sheet_name)
        except Exception as error:
            raise WildberriesReportError(f"Не удалось прочитать Excel-отчет: {error}")

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

    def _handle_file_errors(self, path: Path) -> None:
        if not path.exists():
            raise WildberriesReportError(f"Файл не найден: {path}")
        if path.suffix.lower() not in {".xlsx", ".xls"}:
            raise WildberriesReportError("Нужен Excel-файл .xlsx или .xls")

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
