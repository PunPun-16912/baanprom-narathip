from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Barrier

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.migrations.m001_init import upgrade
from app.db.models import ScrapRequest
from app.route.service import accept_scrap_request


def test_AC_04_05_only_one_concurrent_saleng_accepts_request(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'route-race.db'}",
        connect_args={"check_same_thread": False, "timeout": 30},
    )
    upgrade(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with Session() as db:
        request = ScrapRequest(
            status="open",
            geo_lat=13.756,
            geo_lng=100.534,
            scrap_type="กระดาษ",
            estimated_price=120,
            created_at=datetime(2026, 10, 11),
        )
        db.add(request)
        db.commit()
        request_id = request.id

    start = Barrier(2)

    def attempt(saleng_id):
        with Session() as db:
            start.wait()
            accepted = accept_scrap_request(
                db,
                request_id=request_id,
                saleng_id=saleng_id,
                now=datetime(2026, 10, 11, 8, 0),
            )
            return accepted is not None

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, (11, 12)))

    assert sum(results) == 1
    with Session() as db:
        request = db.get(ScrapRequest, request_id)
        assert request.status == "accepted"
        assert request.accepted_by_saleng_id in (11, 12)
