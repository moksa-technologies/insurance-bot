from pathlib import Path

import pandas as pd

from app.infrastructure.external.excel_search_service import ExcelSearchService


def test_excel_search_hospital_and_garage(tmp_path: Path) -> None:
    hospital_file = tmp_path / "hospitals.xlsx"
    garage_file = tmp_path / "garages.xlsx"

    pd.DataFrame(
        [
            {"pincode": "500001", "name": "Alpha Hospital", "address": "Area A, Hyderabad", "phone": "9000000000"},
            {"pincode": "500002", "name": "Beta Hospital", "address": "Area B, Hyderabad", "phone": "9000000001"},
        ]
    ).to_excel(hospital_file, index=False)

    pd.DataFrame(
        [
            {
                "garage_name": "Garage A",
                "address": "Area A",
                "city": "Hyderabad",
                "pincode": "500001",
                "product": "Car",
                "manufacturer": "TATA",
                "mobile_no": "8111111111",
            }
        ]
    ).to_excel(garage_file, index=False)

    service = ExcelSearchService(hospital_file, garage_file)

    hospitals = service.search_hospitals(pincode="500001")
    assert len(hospitals) == 1
    assert hospitals[0]["name"] == "Alpha Hospital"

    garages = service.search_garages(city="Hyderabad", pincode="500001")
    assert len(garages) == 1
    assert garages[0]["garage_name"] == "Garage A"


def test_hospital_search_returns_when_two_fields_match(tmp_path: Path) -> None:
    hospital_file = tmp_path / "hospitals.xlsx"
    garage_file = tmp_path / "garages.xlsx"

    pd.DataFrame(
        [
            {"pincode": "500003", "name": "Alpha", "address": "SP Road, Secunderabad", "phone": "111"},
            {"pincode": "500072", "name": "Beta", "address": "Kukatpally, Hyderabad", "phone": "222"},
        ]
    ).to_excel(hospital_file, index=False)
    pd.DataFrame([]).to_excel(garage_file, index=False)

    service = ExcelSearchService(hospital_file, garage_file)

    # area + city match should return even without pincode.
    out = service.search_hospitals(area="kukatpally", city="hyderabad", pincode="999999")
    assert len(out) == 1
    assert out[0]["name"] == "Beta"


def test_hospital_search_city_pincode_two_match(tmp_path: Path) -> None:
    hospital_file = tmp_path / "hospitals.xlsx"
    garage_file = tmp_path / "garages.xlsx"

    pd.DataFrame(
        [
            {"pincode": "560001", "name": "Gamma", "address": "MG Road, Bangalore", "phone": "333"},
            {"pincode": "560002", "name": "Delta", "address": "Majestic, Bangalore", "phone": "444"},
        ]
    ).to_excel(hospital_file, index=False)
    pd.DataFrame([]).to_excel(garage_file, index=False)

    service = ExcelSearchService(hospital_file, garage_file)

    # city + pincode two-field match should return.
    out = service.search_hospitals(area="unknown", city="bangalore", pincode="560001")
    assert len(out) == 1
    assert out[0]["name"] == "Gamma"
