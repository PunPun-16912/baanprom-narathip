from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from math import ceil
from time import perf_counter

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.migrations.m001_init import upgrade
from app.db.models import ScrapRequest
from app.route.service import find_scrap_requests_near


def test_AC_04_07_search_p95_under_3_seconds_for_200_requests(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'route-load.db'}",
        connect_args={"check_same_thread": False},
    )
    upgrade(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with Session() as db:
        db.add_all(
            [
                ScrapRequest(
                    status="open",
                    geo_lat=13.756 + index / 100000,
                    geo_lng=100.534 + index / 100000,
                    area_label="แขวงตลาดน้อย",
                    scrap_type="กระดาษ",
                    estimated_price=120,
                    created_at=datetime(2026, 10, 11),
                )
                for index in range(250)
            ]
        )
        db.commit()

    def search_once(_):
        started = perf_counter()
        with Session() as db:
            matches = find_scrap_requests_near(db, lat=13.756, lng=100.534)
            assert len(matches) == 250
        return perf_counter() - started

    with ThreadPoolExecutor(max_workers=200) as pool:
        elapsed_seconds = list(pool.map(search_once, range(200)))
    p95 = sorted(elapsed_seconds)[ceil(0.95 * len(elapsed_seconds)) - 1]

    assert p95 <= 3.0
