from typing import Optional
from sqlalchemy import ForeignKey, Text, MetaData, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

import datetime


class Base(DeclarativeBase):
    metadata = MetaData(schema="data")


# JIKAN TABLES
class Anime(Base):
    __tablename__ = "anime"

    # id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_mal: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    title_jp: Mapped[str]
    type: Mapped[str]
    source: Mapped[str]
    episodes: Mapped[Optional[int]]
    status: Mapped[str]
    aired_from: Mapped[Optional[datetime.date]]
    aired_to: Mapped[Optional[datetime.date]]
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

    anime_tag: Mapped[list["AnimeTag"]] = relationship(
        back_populates="anime", cascade="all, delete-orphan"
    )
    anime_producer: Mapped[list["AnimeProducer"]] = relationship(
        back_populates="anime", cascade="all, delete-orphan"
    )


class Tag(Base):
    __tablename__ = "tag"

    id_mal: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    tag_anime: Mapped[list["AnimeTag"]] = relationship(
        back_populates="tag", cascade="all, delete-orphan"
    )


class AnimeTag(Base):
    __tablename__ = "anime_tag_association"

    id_anime: Mapped[int] = mapped_column(
        ForeignKey("anime.id_mal", ondelete="CASCADE"), primary_key=True
    )
    id_tag: Mapped[int] = mapped_column(
        ForeignKey("tag.id_mal", ondelete="CASCADE"), primary_key=True
    )
    relation: Mapped[str]
    tag: Mapped["Tag"] = relationship(back_populates="tag_anime")
    anime: Mapped["Anime"] = relationship(back_populates="anime_tag")


class Producer(Base):
    __tablename__ = "producer"

    id_mal: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    title_jp: Mapped[Optional[str]]
    url_mal: Mapped[str]
    url_img: Mapped[str]
    about: Mapped[Optional[str]] = mapped_column(Text)
    established: Mapped[Optional[datetime.date]]
    producer_anime: Mapped[list["AnimeProducer"]] = relationship(
        back_populates="producer", cascade="all, delete-orphan"
    )


class AnimeProducer(Base):
    __tablename__ = "anime_producer"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_anime: Mapped[int] = mapped_column(
        ForeignKey("anime.id_mal", ondelete="CASCADE")
    )
    id_producer: Mapped[int] = mapped_column(
        ForeignKey("producer.id_mal", ondelete="CASCADE")
    )
    relation: Mapped[str]
    anime: Mapped["Anime"] = relationship(back_populates="anime_producer")
    producer: Mapped["Producer"] = relationship(back_populates="producer_anime")

    __table_args__ = (
        UniqueConstraint(
            "id_anime", "id_producer", "relation", name="unique_anime_producer_relation"
        ),
    )


class Manga(Base):
    __tablename__ = "manga"

    # id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_mal: Mapped[int] = mapped_column(primary_key=True)
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

    id_manga: Mapped[int] = mapped_column(ForeignKey("manga.id_mal"), primary_key=True)
    id_tag: Mapped[int] = mapped_column(ForeignKey("tag.id_mal"), primary_key=True)
    relation: Mapped[str]


class People(Base):
    __tablename__ = "people"

    id_mal: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    given_name: Mapped[Optional[str]]
    family_name: Mapped[Optional[str]]
    url_mal: Mapped[str]
    url_img: Mapped[Optional[str]]


class MangaPeople(Base):
    __tablename__ = "manga_people"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_manga: Mapped[int] = mapped_column(ForeignKey("manga.id_mal"))
    id_people: Mapped[int] = mapped_column(ForeignKey("people.id_mal"))
    relation: Mapped[str]


class Magazine(Base):
    __tablename__ = "magazine"

    id_mal: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    url_mal: Mapped[str]


class MangaMagazine(Base):
    __tablename__ = "manga_magazine"

    id_manga: Mapped[int] = mapped_column(ForeignKey("manga.id_mal"), primary_key=True)
    id_magazine: Mapped[int] = mapped_column(
        ForeignKey("magazine.id_mal"), primary_key=True
    )
