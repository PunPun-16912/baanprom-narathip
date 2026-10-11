from datetime import datetime

from app.auth.verification import get_verification_provider
from app.db.models import ScrapRequest
from app.main import app


class VerifiedProvider:
    def is_verified(self, saleng_id: int) -> bool:
        return saleng_id == 11


class UnverifiedProvider:
    def is_verified(self, saleng_id: int) -> bool:
        return False


def add_requests(db):
    nearby = ScrapRequest(
        status="open",
        geo_lat=13.7560,
        geo_lng=100.5340,
        area_label="แขวงตลาดน้อย",
        scrap_type="กระดาษ",
        estimated_price=120,
        created_at=datetime(2026, 10, 11),
    )
    outside = ScrapRequest(
        status="open",
        geo_lat=13.9000,
        geo_lng=100.7000,
        area_label="พื้นที่ไกล",
        scrap_type="พลาสติก",
        estimated_price=150,
        created_at=datetime(2026, 10, 11),
    )
    db.add_all([nearby, outside])
    db.commit()
    return nearby


def test_AC_04_03_search_returns_area_and_estimate_without_precise_coordinates(client, db):
    request = add_requests(db)

    response = client.get("/route/requests?lat=13.7563&lng=100.5350")

    assert response.status_code == 200
    body = response.json()
    assert [item["request_id"] for item in body["items"]] == [request.id]
    item = body["items"][0]
    assert item["area_label"] == "แขวงตลาดน้อย"
    assert item["scrap_type"] == "กระดาษ"
    assert item["estimated_price"] == 120
    assert item["distance_km"] <= 5
    assert "geo_lat" not in item and "geo_lng" not in item and "geo_point" not in item


def test_AC_04_08_accept_is_fail_closed_when_identity_provider_is_not_configured(
    client, db
):
    request = add_requests(db)

    response = client.post(
        f"/route/requests/{request.id}/accept",
        json={"saleng_id": 11},
    )

    assert response.status_code == 503
    assert "ยังไม่ได้เชื่อมต่อ" in response.json()["detail"]
    db.refresh(request)
    assert request.status == "open"
    assert request.accepted_by_saleng_id is None


def test_AC_04_08_only_verified_saleng_can_accept_and_then_see_precise_location(
    client, db
):
    request = add_requests(db)
    app.dependency_overrides[get_verification_provider] = lambda: VerifiedProvider()
    try:
        response = client.post(
            f"/route/requests/{request.id}/accept",
            json={"saleng_id": 11},
        )
    finally:
        app.dependency_overrides.pop(get_verification_provider, None)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "มีผู้รับงานแล้ว"
    assert body["geo_point"] == {"lat": request.geo_lat, "lng": request.geo_lng}
    db.refresh(request)
    assert request.status == "accepted"
    assert request.accepted_by_saleng_id == 11


def test_AC_04_08_unverified_saleng_cannot_accept(client, db):
    request = add_requests(db)
    app.dependency_overrides[get_verification_provider] = lambda: UnverifiedProvider()
    try:
        response = client.post(
            f"/route/requests/{request.id}/accept",
            json={"saleng_id": 12},
        )
    finally:
        app.dependency_overrides.pop(get_verification_provider, None)

    assert response.status_code == 403
    db.refresh(request)
    assert request.status == "open"
