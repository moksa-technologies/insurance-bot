from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import pandas as pd


LOGGER = logging.getLogger(__name__)


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_for_match(value: Any) -> str:
    text = _normalize_text(value).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _normalize_pincode(value: Any) -> str:
    text = _normalize_text(value)
    digits = re.sub(r"\D", "", text)
    return digits[:6] if len(digits) >= 6 else digits


def _contains_token(haystack: str, needle: str) -> bool:
    if not haystack or not needle:
        return False
    if needle in haystack:
        return True
    return needle.replace(" ", "") in haystack.replace(" ", "")


class ExcelSearchService:
    def __init__(self, hospital_path: Path, garage_path: Path) -> None:
        self.hospital_path = hospital_path
        self.garage_path = garage_path
        self._hospitals = self._load(hospital_path)
        self._garages = self._load(garage_path)

    @staticmethod
    def _load(path: Path) -> pd.DataFrame:
        if not path.exists():
            LOGGER.warning("excel_load: file_not_found path=%s", path)
            return pd.DataFrame()
        df = pd.read_excel(path)
        df.columns = [str(c).strip().lower() for c in df.columns]
        loaded = df.fillna("")
        LOGGER.info(
            "excel_load: path=%s rows=%s columns=%s",
            path,
            len(loaded),
            list(loaded.columns),
        )
        return loaded

    def refresh(self) -> None:
        self._hospitals = self._load(self.hospital_path)
        self._garages = self._load(self.garage_path)

    def search_hospitals(
        self,
        area: str | None = None,
        city: str | None = None,
        pincode: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        df = self._hospitals.copy()
        if df.empty:
            LOGGER.warning("hospital_search: hospital excel is empty")
            return []

        query_area = _normalize_for_match(area) if area else ""
        query_city = _normalize_for_match(city) if city else ""
        query_pin = _normalize_pincode(pincode) if pincode else ""

        provided = sum(1 for item in [query_area, query_city, query_pin] if item)
        if provided == 0:
            LOGGER.info("hospital_search: no search params provided")
            return []

        required_matches = 2 if provided >= 2 else 1

        records: list[tuple[int, dict[str, Any]]] = []
        rows = df.to_dict(orient="records")
        for row in rows:
            row_pin = _normalize_pincode(row.get("pincode"))

            searchable = " ".join(
                [
                    _normalize_for_match(row.get("name")),
                    _normalize_for_match(row.get("address")),
                    _normalize_for_match(row.get("city")),
                    _normalize_for_match(row.get("area")),
                    _normalize_for_match(row.get("locality")),
                    _normalize_for_match(row.get("district")),
                ]
            ).strip()

            pin_match = bool(query_pin and row_pin and row_pin == query_pin)
            area_match = bool(query_area and searchable and _contains_token(searchable, query_area))
            city_match = bool(query_city and searchable and _contains_token(searchable, query_city))

            match_count = int(pin_match) + int(area_match) + int(city_match)
            if match_count < required_matches:
                continue

            phone_value = row.get("phone") or row.get("contact_number") or row.get("mobile_no")
            entry = {
                "name": _normalize_text(row.get("name")),
                "address": _normalize_text(row.get("address")),
                "phone": _normalize_text(phone_value),
                "pincode": _normalize_text(row.get("pincode")),
            }
            # Prefer better matching rows while keeping deterministic order.
            score = (match_count * 10) + (3 if pin_match else 0) + (2 if city_match else 0) + (1 if area_match else 0)
            records.append((score, entry))

        if not records:
            LOGGER.info(
                "hospital_search: no_match area=%s city=%s pincode=%s required_matches=%s total_rows=%s",
                query_area or None,
                query_city or None,
                query_pin or None,
                required_matches,
                len(rows),
            )
            return []

        records.sort(key=lambda item: item[0], reverse=True)
        top = [row for _, row in records[:limit]]
        LOGGER.info(
            "hospital_search: matched=%s returned=%s area=%s city=%s pincode=%s required_matches=%s",
            len(records),
            len(top),
            query_area or None,
            query_city or None,
            query_pin or None,
            required_matches,
        )
        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.debug("hospital_search: top_results=%s", top)
        return top

    def search_garages(
        self,
        area: str | None = None,
        city: str | None = None,
        pincode: str | None = None,
        vehicle_type: str | None = None,
        manufacturer: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        df = self._garages.copy()
        if df.empty:
            return []

        ranked: list[tuple[int, dict[str, Any]]] = []
        for row in df.to_dict(orient="records"):
            score = 0
            row_city = _normalize_text(row.get("city")).lower()
            row_pin = _normalize_text(row.get("pincode"))
            row_product = _normalize_text(row.get("product")).lower()
            row_manufacturer = _normalize_text(row.get("manufacturer")).lower()

            if pincode and row_pin == _normalize_text(pincode):
                score += 4
            if city and city.lower() in row_city:
                score += 2
            if area and area.lower() in _normalize_text(row.get("address")).lower():
                score += 1
            if vehicle_type and vehicle_type.lower() in row_product:
                score += 2
            if manufacturer and manufacturer.lower() in row_manufacturer:
                score += 2
            if not any([pincode, city, area, vehicle_type, manufacturer]):
                score = 1

            if score > 0:
                ranked.append((score, {k: _normalize_text(v) for k, v in row.items()}))

        ranked.sort(key=lambda item: item[0], reverse=True)
        return [row for _, row in ranked[:limit]]
