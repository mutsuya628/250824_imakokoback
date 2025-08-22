import csv
from sqlmodel import Session, select
from backend.db_old import engine, init_db
from models import Space, PlanType, SpacePlan

PLAN_TYPES = [
    ("DAY","日単位",1),
    ("WEEK","週単位",7),
    ("MONTH","月単位",30),
    ("MONTH3","3カ月",90),
    ("MONTH6","6カ月",180),
    ("YEAR","年単位",365),
]

def run():
    init_db()
    with Session(engine) as s:
        # PlanType
        if s.exec(select(PlanType)).first() is None:
            for i,(code,name,days) in enumerate(PLAN_TYPES, start=1):
                s.add(PlanType(plan_type_id=i, code=code, name_ja=name, unit_days=days))
            s.commit()

        # Spaces
        with open("data/sample_spaces.csv", encoding="utf-8-sig") as f:
            rdr = csv.DictReader(f)
            for row in rdr:
                if s.get(Space, row["space_id"]) is None:
                    s.add(Space(
                        space_id=row["space_id"],
                        category=row["category"],
                        name=row["name"],
                        provider=row["provider"],
                        prefecture=row["prefecture"],
                        city=row["city"],
                        address=row["address"],
                        wifi_mbps=int(row["wifi_mbps"]),
                        capacity_total=int(row["capacity"]),
                        private_room=(row["private_room"].lower()=="true"),
                        noise=row["noise"],
                    ))
            s.commit()

        # SpacePlan
        with open("data/sample_space_plans.csv", encoding="utf-8-sig") as f:
            rdr = csv.DictReader(f)
            pts = {pt.code: pt.plan_type_id for pt in s.exec(select(PlanType)).all()}
            for row in rdr:
                s.add(SpacePlan(
                    space_id=row["space_id"],
                    plan_type_id=pts[row["plan_code"]],
                    price_tax_included=int(row["price_tax_included"]),
                    refundable=(row["refundable"].lower()=="true"),
                    min_units=int(row["min_units"]),
                    max_units=int(row["max_units"])
                ))
            s.commit()

if __name__ == "__main__":
    run()
