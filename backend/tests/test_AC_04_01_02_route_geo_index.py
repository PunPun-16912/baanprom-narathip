from datetime import datetime

from sqlalchemy.orm import sessionmaker

from app.db import session as db_session
from app.db.migrations.m001_init import upgrade
from app.db.models import ScrapRequest
from app.route.service import find_scrap_requests_near, haversine_km


def test_AC_04_01_find_scrap_requests_within_5_km():
    engine = db_session.make_engine("sqlite:///:memory:")
    upgrade(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = Session()

    nearby = ScrapRequest(
        customer_id=1,
        status="open",
        geo_lat=13.7560,
        geo_lng=100.5340,
        scrap_type="กระดาษ",
        estimated_price=120,
        created_at=datetime.utcnow(),
    )
    far = ScrapRequest(
        customer_id=2,
        status="open",
        geo_lat=13.8200,
        geo_lng=100.6000,
        scrap_type="พลาสติก",
        estimated_price=150,
        created_at=datetime.utcnow(),
    )
    db.add_all([nearby, far])
    db.commit()

    matches = find_scrap_requests_near(db, lat=13.7563, lng=100.5350, radius_km=5.0)

    assert len(matches) == 1
    assert matches[0][0].id == nearby.id
    assert matches[0][1] <= 5.0


def test_AC_04_02_route_distance_is_sorted_by_nearness():
    one = haversine_km(13.7560, 100.5350, 13.7560, 100.5400)
    two = haversine_km(13.7560, 100.5350, 13.7600, 100.5500)

    assert one < two
    assert one <= 0.8
    assert two <= 2.0
