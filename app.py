from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from datetime import timedelta
from dotenv import load_dotenv
# 修正 by M. Tanabe - lifespanコンテキストマネージャー導入
from contextlib import asynccontextmanager
load_dotenv()
import os
print("USE_AZURE_DB =", os.getenv("USE_AZURE_DB"))

if os.getenv("USE_AZURE_DB") == "1":
    from db_azure import init_db, get_session
else:
    from db_local import init_db, get_session

from models import Space, PlanType, SpacePlan, Reservation, SearchParams, ReservationCreate

# 修正 by M. Tanabe - 非推奨の@app.on_event("startup")をlifespanに変更
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時の処理
    init_db()
    yield
    # 終了時の処理（必要に応じて）

app = FastAPI(title="Shimanami Workspace API", lifespan=lifespan)

# 修正 by M. Tanabe - CORS設定にポート3001追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://127.0.0.1:3000","http://localhost:3001","http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/plan-types")
def get_plan_types(session: Session = Depends(get_session)):
    return session.exec(select(PlanType)).all()

@app.post("/api/search")
def search_spaces(params: SearchParams, session: Session = Depends(get_session)):
    pt = session.exec(select(PlanType).where(PlanType.code==params.plan_code)).first()
    if not pt:
        return []
    q = session.exec(select(Space, SpacePlan)
                     .where(Space.space_id == SpacePlan.space_id)
                     .where(SpacePlan.plan_type_id == pt.plan_type_id)
                     .where(Space.is_active == True))
    results = []
    for sp, sppl in q:
        if params.category and sp.category != params.category: continue
        if params.min_wifi_mbps and sp.wifi_mbps < params.min_wifi_mbps: continue
        if params.private_room_required and not sp.private_room: continue
        price_total = sppl.price_tax_included * params.units
        if params.max_price_total and price_total > params.max_price_total: continue
        end_date = params.start_date + timedelta(days=pt.unit_days * params.units)
        results.append({
            "space_id": sp.space_id,
            "name": sp.name,
            "category": sp.category,
            "city": sp.city,
            "address": sp.address,
            "wifi_mbps": sp.wifi_mbps,
            "private_room": sp.private_room,
            "plan": {
                "plan_code": pt.code, "plan_name": pt.name_ja,
                "unit_days": pt.unit_days, "units": params.units,
                "price_total": price_total,
                "start_date": str(params.start_date),
                "end_date": str(end_date),
            }
        })
    return results

@app.get("/api/spaces/{space_id}")
def get_space(space_id: str, session: Session = Depends(get_session)):
    sp = session.get(Space, space_id)
    if not sp: return {"error":"not_found"}
    pts = session.exec(select(PlanType)).all()
    plans = session.exec(select(SpacePlan).where(SpacePlan.space_id==space_id)).all()
    plan_map = {p.plan_type_id: p for p in plans}
    enriched = []
    for pt in pts:
        if pt.plan_type_id in plan_map:
            p = plan_map[pt.plan_type_id]
            enriched.append({
                "plan_code": pt.code, "plan_name": pt.name_ja, "unit_days": pt.unit_days,
                "price_tax_included": p.price_tax_included, "refundable": p.refundable,
                "min_units": p.min_units, "max_units": p.max_units
            })
    return {"space": sp, "plans": enriched}

@app.post("/api/reservations")
def create_reservation(payload: ReservationCreate, session: Session = Depends(get_session)):
    pt = session.exec(select(PlanType).where(PlanType.code==payload.plan_code)).first()
    if not pt: return {"error":"invalid_plan"}
    sppl = session.exec(
        select(SpacePlan)
        .where(SpacePlan.space_id==payload.space_id)
        .where(SpacePlan.plan_type_id==pt.plan_type_id)
    ).first()
    if not sppl: return {"error":"plan_not_available_for_space"}

    from datetime import timedelta
    end_date = payload.start_date + timedelta(days=pt.unit_days * payload.units)
    price_total = sppl.price_tax_included * payload.units
    res = Reservation(
        user_name=payload.user_name,
        user_email=payload.user_email,
        space_id=payload.space_id,
        plan_type_id=pt.plan_type_id,
        start_date=payload.start_date,
        units=payload.units,
        end_date=end_date,
        price_total=price_total,
        status="confirmed",
    )
    session.add(res)
    session.commit()
    session.refresh(res)
    return res
