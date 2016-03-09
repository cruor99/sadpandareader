from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine('sqlite:///./databse.db')
Session = sessionmaker(bind=engine)
db = Session()


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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    cookies = Column(String)


class Gallery(Base):
    __tablename__ = "galleries"

    id = Column(Integer, primary_key=True)
    gallery_id = Column(String)
    # pagelinks = Column(String)
    pagecount = Column(Integer)
    gallery_name = Column(String)


class Pagelink(Base):
    __tablename__ = "pagelinks"

    id = Column(Integer, primary_key=True)
    galleryid = Column(Integer, ForeignKey("galleries.id"))
    galleries = relationship("Gallery")
    pagelink = Column(String)


if __name__ == "__main__":
    Base.metadata.create_all(engine)
