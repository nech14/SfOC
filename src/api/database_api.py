import datetime

from fastapi import Depends, APIRouter

from src.api.api_tags import ApiTags
from src.api.base_api import rout_root
from src.database.database import Session
from src.database.models.models import Frames

router = APIRouter(prefix="/database", tags=[ApiTags.Database])

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


# 1️⃣ Вывод всех строк из таблицы frames
@router.get(f"{rout_root}/frames/", tags=[ApiTags.Database])
def get_frames(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Frames).offset(skip).limit(limit).all()


# 2️⃣ Фильтр по интервалу дат
@router.get(f"{rout_root}/frames/by_date/", tags=[ApiTags.Database])
def get_frames_by_date(
    date_from: datetime.datetime,
    date_to: datetime.datetime,
    db: Session = Depends(get_db)
):
    return (
        db.query(Frames)
        .filter(Frames.dt_beg >= date_from, Frames.dt_end <= date_to)
        .all()
    )


# 3️⃣ Количество строк в таблице frames
@router.get(f"{rout_root}/frames/count", tags=[ApiTags.Database])
def get_frames_count(db: Session = Depends(get_db)):
    return {"count": db.query(Frames).count()}

