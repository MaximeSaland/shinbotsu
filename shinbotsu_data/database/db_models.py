from typing import Optional
from sqlalchemy import ForeignKey, Text, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

import datetime


class Base(DeclarativeBase):
    metadata = MetaData(schema="data")


# JIKAN TABLES
class Anime(Base):
    __tablename__ = "anime"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_mal: Mapped[int] = mapped_column(unique=True)
    title: Mapped[str]
    title_jp: Mapped[str]
    type: Mapped[str]
    source: Mapped[str]
    episodes: Mapped[Optional[int]]
    status: Mapped[int]
    airing_from: Mapped[Optional[datetime.date]]
    airing_to: Mapped[Optional[datetime.date]]
    rating: Mapped[str]
    synopsis: Mapped[str] = mapped_column(Text)
    season: Mapped[Optional[str]]
    year: Mapped[Optional[int]]
    url_mal: Mapped[Optional[str]]
    url_img_jpg: Mapped[Optional[str]]
    url_img_jpg_small: Mapped[Optional[str]]
    url_img_jpg_large: Mapped[Optional[str]]
    url_img_webp: Mapped[Optional[str]]
    url_img_webp_small: Mapped[Optional[str]]
    url_img_webp_large: Mapped[Optional[str]]
    youtube_trailer_id: Mapped[Optional[str]]

    def __repr__(self) -> str:
        return f"{id:{self.id}, id_mal:{self.id_mal}, title:{self.title}, title_jp:{self.title_jp}, type:{self.type}, source:{self.source}, episodes:{self.episodes}, status:{self.status}, airing_from:{self.airing_from}, airing_to:{self.airing_to}, rating:{self.rating}, synopsis:{self.synopsis}, season:{self.season}, year:{self.year}, url_mal:{self.url_mal}, url_img_jpg:{self.url_img_jpg}, url_img_jpg_small:{self.url_img_jpg_small}, url_img_jpg_large:{self.url_img_jpg_large}, url_img_webp:{self.url_img_webp}, url_img_webp_small:{self.url_img_webp_small}, url_img_webp_large:{self.url_img_webp_large}, youtube_trailer_id:{self.youtube_trailer_id}, updated_at:{self.updated_at}}"


class Producer(Base):
    __tablename__ = "producer"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_mal: Mapped[int] = mapped_column(unique=True)
    title: Mapped[str]
    title_jp: Mapped[Optional[str]]
    url_mal: Mapped[str]
    url_img: Mapped[str]
    about: Mapped[Optional[str]] = mapped_column(Text)
    established: Mapped[Optional[datetime.date]]

    def __repr__(self) -> str:
        return f"{id:{self.id}, id_mal:{self.id_mal}, title:{self.title}, title_jp:{self.title_jp}, url_mal:{self.url_mal}, url_img:{self.url_img}, about:{self.about}}"


class AnimeProducer(Base):
    __tablename__ = "anime_producer"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_anime: Mapped[int] = mapped_column(ForeignKey("anime.id"))
    id_producer: Mapped[int] = mapped_column(ForeignKey("producer.id"))
    relation: Mapped[str]

    def __repr__(self) -> str:
        return f"{id:{self.id}, id_anime:{self.id_anime}, id_producer:{self.id_producer}, relation:{self.relation}}"


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_mal: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str]
    type: Mapped[str]

    def __repr__(self) -> str:
        return f"{id:{self.id}, id_mal:{self.id_mal}, label:{self.label}, type:{self.type}}"


class AnimeTag(Base):
    __tablename__ = "anime_tag"

    id_anime: Mapped[int] = mapped_column(ForeignKey("anime.id"), primary_key=True)
    id_tag: Mapped[int] = mapped_column(ForeignKey("tag.id"), primary_key=True)
    relation: Mapped[str]

    def __repr__(self) -> str:
        return f"{{id_anime:{self.id_anime}, id_tag:{self.id_tag}, relation:{self.relation}}}"


class Manga(Base):
    __tablename__ = "manga"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_mal: Mapped[int] = mapped_column(unique=True)
    title: Mapped[str]
    title_jp: Mapped[str]
    type: Mapped[str]
    chapters: Mapped[int]
    volumes: Mapped[int]
    status: Mapped[str]
    published_from: Mapped[datetime.date]
    published_to: Mapped[datetime.date]
    synopsis: Mapped[str] = mapped_column(Text)
    url_mal: Mapped[Optional[str]]
    url_img_jpg: Mapped[Optional[str]]
    url_img_jpg_small: Mapped[Optional[str]]
    url_img_jpg_large: Mapped[Optional[str]]
    url_img_webp: Mapped[Optional[str]]
    url_img_webp_small: Mapped[Optional[str]]
    url_img_webp_large: Mapped[Optional[str]]


class MangaTag(Base):
    __tablename__ = "manga_tag"

    id_manga: Mapped[int] = mapped_column(ForeignKey("manga.id"), primary_key=True)
    id_tag: Mapped[int] = mapped_column(ForeignKey("tag.id"), primary_key=True)
    relation: Mapped[str]


class People(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_mal: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str]
    given_name: Mapped[Optional[str]]
    family_name: Mapped[Optional[str]]
    url_mal: Mapped[str]
    url_img: Mapped[Optional[str]]


class MangaPeople(Base):
    __tablename__ = "manga_people"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_manga: Mapped[int]
    id_people: Mapped[int]
    relation: Mapped[str]


class Magazine(Base):
    __tablename__ = "magazine"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_mal: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str]
    url_mal: Mapped[str]


class MangaMagazine(Base):
    __tablename__ = "manga_magazine"

    id_manga: Mapped[int] = mapped_column(ForeignKey("manga.id"), primary_key=True)
    id_magazine: Mapped[int] = mapped_column(
        ForeignKey("magazine.id"), primary_key=True
    )
