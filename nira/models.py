from datetime import datetime, date, timedelta
from nira import db


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    confirmation_code = db.Column(db.String(64), unique=True, index=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    mother_full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    district = db.Column(db.String(120), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    national_id = db.Column(db.String(60))
    preferred_time = db.Column(db.String(60))
    visit_reason = db.Column(db.String(180))
    visit_date = db.Column(db.Date, nullable=False, index=True)
    notes = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def slots_taken(cls, visit_date: date) -> int:
        return (
            cls.query.filter_by(visit_date=visit_date)
            .with_entities(db.func.count(cls.id))
            .scalar()
        )

    @classmethod
    def availability(cls, start: date, days: int, daily_limit: int, include_full: bool = False):
        """Return a list of dates with remaining slots for the window."""
        end_date = start + timedelta(days=days)
        counts = (
            cls.query.with_entities(cls.visit_date, db.func.count(cls.id))
            .filter(cls.visit_date >= start, cls.visit_date <= end_date)
            .group_by(cls.visit_date)
            .all()
        )
        count_lookup = {c[0]: c[1] for c in counts}

        available = []
        for offset in range(days + 1):
            visit_day = start + timedelta(days=offset)
            taken = count_lookup.get(visit_day, 0)
            remaining = max(daily_limit - taken, 0)
            if include_full or remaining > 0:
                available.append({"date": visit_day, "remaining": remaining})
        return available
