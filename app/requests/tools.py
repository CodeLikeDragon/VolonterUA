from app.requests.requests.models import Request


def req_to_dict(r: Request):
    return {
        "id": str(r.id),
        "title": r.title,
        "description": r.description,
        "city_id": str(r.city_id) if r.city_id else None,
        "address": r.address,
        "status": r.status.value,
        "created_by": r.created_by,
        "assignee_id": r.assignee_id,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        "items": [
            {"id": str(i.id), "name": i.name, "qty": float(i.qty) if i.qty is not None else None, "unit": i.unit, "notes": i.notes}
            for i in (r.items or [])
        ]
    }