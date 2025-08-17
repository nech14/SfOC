import datetime

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy import text

from config import rout_root
from src.api.api_tags import ApiTags
from src.database.database import Session
from src.database.models.models import Frames, User, Camera, Coefs, Filters, FindStarsCoefs, Keograms, Location, Paths, \
    Nights, Background, BackgroundsAll

router = APIRouter(prefix="/database", tags=[ApiTags.Database])

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()



@router.get(f"{rout_root}/ping", tags=[ApiTags.Database])
def ping_db(db: Session = Depends(get_db)):
    try:
        # Выполняем простейший запрос
        db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "Database connection is alive"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")




@router.get(f"{rout_root}/frames/", tags=[ApiTags.Database])
def get_frames(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Frames).offset(skip).limit(limit).all()


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


@router.get(f"{rout_root}/frames/count", tags=[ApiTags.Database])
def get_frames_count(db: Session = Depends(get_db)):
    return {"count": db.query(Frames).count()}




@router.get(f"{rout_root}/users/", tags=[ApiTags.Database])
def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()


@router.get(f"{rout_root}/users/count", tags=[ApiTags.Database])
def get_users_count(db: Session = Depends(get_db)):
    return {"count": db.query(User).count()}



@router.get(f"{rout_root}/cameras/", tags=[ApiTags.Database])
def get_cameras(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Camera).offset(skip).limit(limit).all()


@router.get(f"{rout_root}/cameras/count", tags=[ApiTags.Database])
def get_cameras_count(db: Session = Depends(get_db)):
    return {"count": db.query(Camera).count()}



@router.get(f"{rout_root}/coefs/", tags=[ApiTags.Database])
def get_coefs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Coefs).offset(skip).limit(limit).all()


@router.get(f"{rout_root}/coefs/count", tags=[ApiTags.Database])
def get_coefs_count(db: Session = Depends(get_db)):
    return {"count": db.query(Coefs).count()}



@router.get(f"{rout_root}/filters/", tags=[ApiTags.Database])
def get_filters(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Filters).offset(skip).limit(limit).all()


@router.get(f"{rout_root}/filters/count", tags=[ApiTags.Database])
def get_filters_count(db: Session = Depends(get_db)):
    return {"count": db.query(Filters).count()}



@router.get(f"{rout_root}/find_stars_coefs/", tags=[ApiTags.Database])
def get_find_stars_coefs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(FindStarsCoefs).offset(skip).limit(limit).all()


@router.get(f"{rout_root}/find_stars_coefs/count", tags=[ApiTags.Database])
def get_find_stars_coefs_count(db: Session = Depends(get_db)):
    return {"count": db.query(FindStarsCoefs).count()}



@router.get(f"{rout_root}/keograms/", tags=[ApiTags.Database])
def get_keograms(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Keograms).offset(skip).limit(limit).all()

@router.get(f"{rout_root}/keograms/by_date/", tags=[ApiTags.Database])
def get_keograms_by_date(
    date_from: datetime.datetime,
    date_to: datetime.datetime,
    db: Session = Depends(get_db)
):
    format = "%Y%m%d%H"
    return (
        db.query(Keograms)
        .filter(Keograms.id_night >= date_from.strftime(format), Keograms.id_night <= date_to.strftime(format))
        .all()
    )

@router.get(f"{rout_root}/keograms/by_id_night/", tags=[ApiTags.Database])
def get_keograms_by_id_night(
    id_night_from: int,
    id_night_to: int,
    db: Session = Depends(get_db)
):
    return (
        db.query(Keograms)
        .filter(Keograms.id_night >= id_night_from, Keograms.id_night <= id_night_to)
        .all()
    )

@router.get(f"{rout_root}/keograms/count", tags=[ApiTags.Database])
def get_keograms_count(db: Session = Depends(get_db)):
    return {"count": db.query(Keograms).count()}



@router.get(f"{rout_root}/location/", tags=[ApiTags.Database])
def get_locations(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Location).offset(skip).limit(limit).all()


@router.get(f"{rout_root}/location/count", tags=[ApiTags.Database])
def get_locations_count(db: Session = Depends(get_db)):
    return {"count": db.query(Location).count()}



@router.get(f"{rout_root}/paths/", tags=[ApiTags.Database])
def get_paths(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Paths).offset(skip).limit(limit).all()


@router.get(f"{rout_root}/paths/count", tags=[ApiTags.Database])
def get_paths_count(db: Session = Depends(get_db)):
    return {"count": db.query(Paths).count()}




@router.get(f"{rout_root}/nights/", tags=[ApiTags.Database])
def get_nights(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Nights).offset(skip).limit(limit).all()


@router.get(f"{rout_root}/nights/by_dt_end/", tags=[ApiTags.Database])
def get_nights_by_dt_end(
    date_from: datetime.datetime,
    date_to: datetime.datetime,
    db: Session = Depends(get_db)
):
    return (
        db.query(Nights)
        .filter(Nights.dt_end >= date_from, Nights.dt_end <= date_to)
        .all()
    )


@router.get(f"{rout_root}/nights/count", tags=[ApiTags.Database])
def get_nights_count(db: Session = Depends(get_db)):
    return {"count": db.query(Nights).count()}



@router.get(f"{rout_root}/backgrounds/", tags=[ApiTags.Database])
def get_backgrounds(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Background).offset(skip).limit(limit).all()

@router.get(f"{rout_root}/backgrounds/by_date/", tags=[ApiTags.Database])
def get_backgrounds_by_date(
    date_from: datetime.datetime,
    date_to: datetime.datetime,
    db: Session = Depends(get_db)
):
    format = "%Y%m%d%H"
    return (
        db.query(Background)
        .filter(Background.id_night >= date_from.strftime(format), Background.id_night <= date_to.strftime(format))
        .all()
    )

@router.get(f"{rout_root}/backgrounds/by_id_night/", tags=[ApiTags.Database])
def get_backgrounds_by_id_night(
    id_night_from: int,
    id_night_to: int,
    db: Session = Depends(get_db)
):
    return (
        db.query(Background)
        .filter(Background.id_night >= id_night_from, Background.id_night <= id_night_to)
        .all()
    )

@router.get(f"{rout_root}/backgrounds/count", tags=[ApiTags.Database])
def get_backgrounds_count(db: Session = Depends(get_db)):
    return {"count": db.query(Background).count()}



@router.get(f"{rout_root}/backgrounds_all/", tags=[ApiTags.Database])
def get_backgrounds_all(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(BackgroundsAll).offset(skip).limit(limit).all()

@router.get(f"{rout_root}/backgrounds_all/by_date/", tags=[ApiTags.Database])
def get_backgrounds_all_by_date(
    date_from: datetime.datetime,
    date_to: datetime.datetime,
    db: Session = Depends(get_db)
):
    return (
        db.query(BackgroundsAll)
        .filter(BackgroundsAll.dt >= date_from, BackgroundsAll.dt <= date_to)
        .all()
    )

@router.get(f"{rout_root}/backgrounds_all/by_id_night/", tags=[ApiTags.Database])
def get_backgrounds_all_by_id_night(
    id_night_from: int,
    id_night_to: int,
    db: Session = Depends(get_db)
):
    return (
        db.query(BackgroundsAll)
        .filter(BackgroundsAll.id_night >= id_night_from, BackgroundsAll.id_night <= id_night_to)
        .all()
    )

@router.get(f"{rout_root}/backgrounds_all/count", tags=[ApiTags.Database])
def get_backgrounds_all_count(db: Session = Depends(get_db)):
    return {"count": db.query(BackgroundsAll).count()}