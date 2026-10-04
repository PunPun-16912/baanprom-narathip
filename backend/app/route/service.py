"""Geo-index foundation for route work search: REQ-FN-002, REQ-OP-002, REQ-QA-002."""
from __future__ import annotations

from math import atan2, cos, radians, sin, sqrt
from typing import Iterable

from sqlalchemy.orm import Session

from app.config import ROUTE_RADIUS_KM
from app.db.models import ScrapRequest

EARTH_RADIUS_KM = 6371.0


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
    """Adapter สำหรับ Redis Geo-Spatial Index แบบง่ายที่ใช้ได้ทันทีโดยไม่ต้องติดตั้ง Redis."""

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
    """คืนรายชื่อคำขอขายที่อยู่ภายในรัศมีที่กำหนด โดยใช้ Haversine เพื่อให้ตรงกับ AC-04-01."""
    items = db.query(ScrapRequest).all()
    geo_index = GeoIndex(radius_km=radius_km)
    return geo_index.query(items, lat, lng)
