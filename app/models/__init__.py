from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from os.path import isfile

Base = declarative_base()


def check_database(data_dir):
    if isfile(data_dir+"/database.db"):
        engine = create_engine('sqlite:///'+data_dir+'/database.db')
        Session = sessionmaker(bind=engine)
        db = Session()
        return db
    else:
        engine = create_engine('sqlite:///'+data_dir+'/database.db')
        Session = sessionmaker(bind=engine)
        db = Session()
        Base.metadata.create_all(engine)
        return db


class Filters(Base):
    __tablename__ = "filters"

    id = Column(Integer, primary_key=True)
    doujinshi = Column(Integer)
    manga = Column(Integer)
    artistcg = Column(Integer)
    gamecg = Column(Integer)
    western = Column(Integer)
    imageset = Column(Integer)
    cosplay = Column(Integer)
    asianporn = Column(Integer)
    misc = Column(Integer)
    nonh = Column(Integer)


class Search(Base):
    __tablename__ = "search"

    id = Column(Integer, primary_key=True)
    searchterm = Column(String)

    def __str__(self):
        return "{}".format(self.searchterm)

    def __repr__(self):
        return "{}".format(self.searchterm)


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    logging = Column(Integer)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    cookies = Column(String)


class Gallery(Base):
    __tablename__ = "galleries"

    id = Column(Integer, primary_key=True)
    gallery_id = Column(String)
    gallery_token = Column(String)
    # pagelinks = Column(String)
    pagecount = Column(Integer)
    gallery_name = Column(String)
    gallery_thumb = Column(String)
    filesize = Column(Integer)


class Favourites(Base):
    __tablename__ = "favourites"

    id = Column(Integer, primary_key=True)
    gallery_id = Column(String)
    gallery_token = Column(String)
    pagecount = Column(Integer)
    gallery_name = Column(String)
    gallery_thumb = Column(String)
    filesize = Column(Integer)


class GalleryTags(Base):
    __tablename__ = "gallerytags"

    id = Column(Integer, primary_key=True)
    galleryid = Column(Integer, ForeignKey("galleries.id"))
    galleries = relationship("Gallery")
    tag = Column(String)


class Pagelink(Base):
    __tablename__ = "pagelinks"

    id = Column(Integer, primary_key=True)
    galleryid = Column(Integer, ForeignKey("galleries.id"))
    galleries = relationship("Gallery")
    pagelink = Column(String)
    mainpage = Column(String)
    current = Column(Integer)
