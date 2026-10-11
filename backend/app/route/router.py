"""HTTP surface for route search and scrap-request acceptance."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.verification import (
    SalengVerificationProvider,
    VerificationProviderUnavailable,
    get_verification_provider,
)
from app.clock import get_now
from app.config import ROUTE_RADIUS_KM
from app.db.models import ScrapRequest
from app.db.session import get_db
from app.privacy import get_logger
from app.route import service

router = APIRouter(prefix="/route", tags=["route"])
log = get_logger(__name__)


class AcceptRequest(BaseModel):
    saleng_id: int = Field(gt=0)


def _accepted_request_out(request: ScrapRequest, saleng_id: int) -> dict:
    return {
        "request_id": request.id,
        "status": "มีผู้รับงานแล้ว",
        "accepted_by_saleng_id": saleng_id,
        "geo_point": {"lat": request.geo_lat, "lng": request.geo_lng},
    }


@router.get("/requests")
def search_requests(
    lat: float = Query(ge=-90, le=90),
    lng: float = Query(ge=-180, le=180),
    db: Session = Depends(get_db),
):
    """REQ-FN-002: คืนเฉพาะป้ายพื้นที่ ไม่ส่งพิกัดจริงก่อนรับงาน (REQ-SEC-002)."""
    matches = service.find_scrap_requests_near(db, lat=lat, lng=lng)
    return {
        "radius_km": ROUTE_RADIUS_KM,
        "items": [
            {
                "request_id": item.id,
                "status": "รอผู้รับงาน",
                "area_label": item.area_label,
                "scrap_type": item.scrap_type,
                "estimated_price": item.estimated_price,
                "distance_km": round(distance, 3),
            }
            for item, distance in matches
        ],
    }


@router.post("/requests/{request_id}/accept")
def accept_request(
    request_id: int,
    body: AcceptRequest,
    db: Session = Depends(get_db),
    now: datetime = Depends(get_now),
    verification: SalengVerificationProvider = Depends(get_verification_provider),
):
    """รับงานหลังตรวจตัวตน; พิกัดจริงเปิดเผยเฉพาะผลรับงานสำเร็จ."""
    try:
        verified = verification.is_verified(body.saleng_id)
    except VerificationProviderUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    if not verified:
        raise HTTPException(status_code=403, detail="ซาเล้งยังไม่ได้ยืนยันตัวตน")

    request = service.accept_scrap_request(
        db,
        request_id=request_id,
        saleng_id=body.saleng_id,
        now=now,
    )
    if request is None:
        existing = db.get(ScrapRequest, request_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="ไม่พบคำขอรับซื้อ")
        raise HTTPException(status_code=409, detail="คำขอนี้มีผู้รับงานแล้ว")

    log.info("route request %s accepted by saleng %s", request.id, body.saleng_id)
    return _accepted_request_out(request, body.saleng_id)
