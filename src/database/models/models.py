

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger, SmallInteger, String, Float, DateTime, Double

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(20), nullable=False)
    rname = Column(String(50), nullable=False)
    passw = Column("pass", String(128), nullable=False)
    isAuth = Column(Integer, nullable=False)


class Camera(Base):
    __tablename__ = 'camera'
    id = Column(SmallInteger, primary_key=True, autoincrement=True)
    name = Column(String(10), nullable=False)
    serial_number = Column(String(20), nullable=False)
    file_prefix = Column(String(10), nullable=False)
    id_location = Column(SmallInteger, nullable=False)


class Background(Base):
    __tablename__ = 'backgrounds'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    id_night = Column(Integer, nullable=False)
    id_filter = Column(SmallInteger, nullable=False)
    dest = Column(String(500), nullable=False)
    dt = Column(DateTime, nullable=False)


class BackgroundsAll(Base):
    __tablename__ = 'backgrounds_all'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_night = Column(SmallInteger, nullable=False)
    id_camera = Column(SmallInteger, nullable=False)
    dt = Column(DateTime, nullable=False)
    id_filter = Column(SmallInteger, nullable=False)
    dest = Column(String(500), nullable=False)
    id_bg = Column(BigInteger, nullable=False)


class Coefs(Base):
    __tablename__ = 'coefs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_filter = Column(SmallInteger, nullable=False)
    readoutrate = Column(SmallInteger, nullable=False)
    preamp = Column(SmallInteger, nullable=False)
    coef = Column(Float, nullable=False)


class Filters(Base):
    __tablename__ = 'filters'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_camera = Column(SmallInteger, nullable=False)
    name = Column(String(50), nullable=False)
    file_prefix = Column(String(10), nullable=False)
    part_num = Column(String(20), nullable=False)
    ucf = Column(String(500), nullable=False)
    f_band = Column(String(500), nullable=False)
    coef = Column(Float, nullable=False)
    color = Column(String(10), nullable=False)


class FindStarsCoefs(Base):
    __tablename__ = "find_stars_coefs"
    id = Column(Integer, primary_key=True)
    id_filtr = Column(SmallInteger, nullable=False)
    binning = Column(SmallInteger, nullable=False)
    exp = Column(Integer, nullable=False)  # mediumint → Integer
    size_reg = Column(SmallInteger, nullable=False)
    porog = Column(Float, nullable=False)
    n_star_min = Column(SmallInteger, nullable=False)
    n_star_max = Column(SmallInteger, nullable=False)
    ecc_star = Column(Float, nullable=False)
    ecc_track = Column(Float, nullable=False)
    n_blur = Column(SmallInteger, nullable=False)


class Frames(Base):
    __tablename__ = "frames"
    id = Column(Integer, primary_key=True)
    id_night = Column(Integer, nullable=False)
    id_filtr = Column(SmallInteger, nullable=False)
    dt_beg = Column(DateTime, nullable=False)
    dt_end = Column(DateTime, nullable=False)
    exp = Column(Integer, nullable=False)
    dest = Column(String(500), nullable=False)
    mean_frame = Column(Float, nullable=True)
    id_proc = Column(SmallInteger, default=0)


class Keograms(Base):
    __tablename__ = "keograms"
    id = Column(Integer, primary_key=True)
    id_night = Column(Integer, nullable=False)
    id_filtr = Column(SmallInteger, nullable=False)
    path = Column(String(200), nullable=False)


class Location(Base):
    __tablename__ = "location"
    id = Column(SmallInteger, primary_key=True)
    name = Column(String(50), nullable=False)
    lat = Column(Double, nullable=False)
    lon = Column(Double, nullable=False)
    height = Column(SmallInteger, nullable=False)


class Nights(Base):
    __tablename__ = "nights"
    id = Column(Integer, primary_key=True)
    id_camera = Column(SmallInteger, nullable=False)
    year = Column(String(4), nullable=False)
    month = Column(String(2), nullable=False)
    day = Column(String(2), nullable=False)
    dt_beg = Column(DateTime, nullable=False)
    dt_end = Column(DateTime, nullable=False)
    binning = Column(SmallInteger, nullable=True)
    readout = Column(SmallInteger, nullable=True)
    preamp = Column(SmallInteger, nullable=True)
    keogram_path = Column(String(200), nullable=True)
    mean_frame = Column(Float, nullable=True)
    id_proc = Column(SmallInteger, default=0, nullable=False)


class Paths(Base):
    __tablename__ = "paths"
    id = Column(SmallInteger, primary_key=True)
    id_camera = Column(SmallInteger, nullable=False)
    scripts = Column(String(500), nullable=False)
    ucf = Column(String(500), nullable=False)
    bandpass = Column(String(500), nullable=True)
    source = Column(String(500), nullable=False)
    dest = Column(String(500), nullable=False)
    view = Column(String(500), nullable=False)
    log = Column(String(500), nullable=False)
    lock_file = Column(String(500), nullable=False)