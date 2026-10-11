"""SQL-backed route search and atomic acceptance: REQ-FN-002, REQ-BR-002."""
from __future__ import annotations

from math import atan2, cos, radians, sin, sqrt
from datetime import datetime
from typing import Iterable

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.config import ROUTE_RADIUS_KM
from app.db.models import ScrapRequest

EARTH_RADIUS_KM = 6371.0
STATUS_OPEN = "open"
STATUS_ACCEPTED = "accepted"
STATUS_COMPLETED = "completed"


# REQ-FN-002, REQ-OP-002
def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """คำนวณระยะทางระหว่างพิกัดสองจุดแบบ Haversine เพื่อใช้กรองในเส้นทาง 5 กม."""
    lat1_r = radians(lat1)
    lat2_r = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lng = radians(lng2 - lng1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1_r) * cos(lat2_r) * sin(delta_lng / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return EARTH_RADIUS_KM * c


# REQ-FN-002, REQ-QA-002
class GeoIndex:
    """ค้นหาแบบ Haversine โดยไม่เรียก Maps API ตาม D-04-01."""

    def __init__(self, radius_km: float = ROUTE_RADIUS_KM):
        self.radius_km = radius_km

    def query(self, items: Iterable[ScrapRequest], lat: float, lng: float):
        matches = []
        for item in items:
            distance = haversine_km(lat, lng, item.geo_lat, item.geo_lng)
            if distance <= self.radius_km:
                matches.append((item, distance))
        matches.sort(key=lambda entry: entry[1])
        return matches


# REQ-FN-002
def find_scrap_requests_near(
    db: Session,
    *,
    lat: float,
    lng: float,
    radius_km: float = ROUTE_RADIUS_KM,
):
    """คืนคำขอที่ยังรอผู้รับงาน ภายในรัศมีไม่เกิน REQ-FN-002."""
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        raise ValueError("พิกัดผู้ค้นหาอยู่นอกช่วงที่ถูกต้อง")
    if not (0 < radius_km <= ROUTE_RADIUS_KM):
        raise ValueError(f"รัศมีต้องมากกว่า 0 และไม่เกิน {ROUTE_RADIUS_KM} กม.")
    items = db.query(ScrapRequest).filter(ScrapRequest.status == STATUS_OPEN).all()
    geo_index = GeoIndex(radius_km=radius_km)
    return geo_index.query(items, lat, lng)


def accept_scrap_request(
    db: Session,
    *,
    request_id: int,
    saleng_id: int,
    now: datetime,
) -> ScrapRequest | None:
    """รับงานได้คนเดียว โดยให้ conditional UPDATE เป็นจุดตัดสินผู้ชนะ (REQ-BR-002)."""
    result = db.execute(
        update(ScrapRequest)
        .where(
            ScrapRequest.id == request_id,
            ScrapRequest.status == STATUS_OPEN,
        )
        .values(
            status=STATUS_ACCEPTED,
            accepted_by_saleng_id=saleng_id,
            accepted_at=now,
        )
    )
    db.commit()
    if result.rowcount != 1:
        return None
    return db.get(ScrapRequest, request_id)
