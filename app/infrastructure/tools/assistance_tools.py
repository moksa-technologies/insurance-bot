from __future__ import annotations

from typing import Any

from app.infrastructure.external.excel_search_service import ExcelSearchService


class AssistanceTools:
    def __init__(self, excel_service: ExcelSearchService) -> None:
        self.excel_service = excel_service

    def hospital_tool(
        self,
        area: str | None = None,
        city: str | None = None,
        pincode: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        return self.excel_service.search_hospitals(area=area, city=city, pincode=pincode, limit=limit)

    def garage_tool(
        self,
        area: str | None = None,
        city: str | None = None,
        pincode: str | None = None,
        vehicle_type: str | None = None,
        manufacturer: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        return self.excel_service.search_garages(
            area=area,
            city=city,
            pincode=pincode,
            vehicle_type=vehicle_type,
            manufacturer=manufacturer,
            limit=limit,
        )
