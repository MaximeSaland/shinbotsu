from typing import Optional
from sqlalchemy import ForeignKey, Text, MetaData, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

import datetime


class Base(DeclarativeBase):
    metadata = MetaData(schema="data")


class ScraperState(Base):
    __tablename__ = "scraper_state"

    endpoint: Mapped[str] = mapped_column(primary_key=True)
    offset: Mapped[int]
    last_updated: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now(datetime.timezone.utc)
    )


# JIKAN TABLES
class Anime(Base):
    __tablename__ = "anime"

    id_mal: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    title_jp: Mapped[Optional[str]]
    type: Mapped[Optional[str]]
    source: Mapped[Optional[str]]
    episodes: Mapped[Optional[int]]
    status: Mapped[Optional[str]]
    aired_from: Mapped[Optional[datetime.date]]
    aired_to: Mapped[Optional[datetime.date]]
    rating: Mapped[Optional[str]]
    synopsis: Mapped[Optional[str]] = mapped_column(Text)
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

    id: Mapped[str] = mapped_column(primary_key=True)
    title: str
    title_jp: Mapped[Optional[str]]
    synopsis: Mapped[Optional[str]]
    synopsis_jp: Mapped[Optional[str]]
    last_volume: Mapped[Optional[int]]
    last_chapter: Mapped[Optional[int]]
    demographic: Mapped[Optional[str]]
    status: Mapped[Optional[str]]
    publication_year: Mapped[Optional[int]]
    rating: Mapped[Optional[str]]
    id_anilist: Mapped[Optional[int]]
    id_amazon: Mapped[Optional[int]]
    id_bookwalker: Mapped[Optional[str]]
    id_mal: Mapped[Optional[int]]


class Author(Base):
    __tablename__ = "author"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]


class MangaAuthor(Base):
    __tablename__ = "manga_author"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_manga: Mapped[str] = mapped_column(ForeignKey("manga.id", ondelete="CASCADE"))
    id_author: Mapped[str] = mapped_column(ForeignKey("author.id", ondelete="CASCADE"))
    relation: Mapped[str]

    __table_args__ = UniqueConstraint(
        "id_manga", "id_author", "relation", name="unique_manga_author_relation"
    )


class MangaRelation(Base):
    __tablename__ = "manga_relation"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_manga: Mapped[str] = mapped_column(ForeignKey("manga.id", ondelete="CASCADE"))
    id_manga_related: Mapped[str] = mapped_column(
        ForeignKey("manga.id", ondelete="CASCADE")
    )
    relation: Mapped[str]

    __table_args__ = UniqueConstraint(
        "id_manga", "id_manga_related", name="unique_manga_manga_related"
    )


class TagMangadex(Base):
    __tablename__ = "tag_mangadex"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    type: Mapped[str]


class MangaTag(Base):
    id_manga: Mapped[str] = mapped_column(
        ForeignKey("manga.id", ondelete="CASCADE"), primary_key=True
    )
    id_tag: Mapped[str] = mapped_column(
        ForeignKey("tag_mangadex.id", ondelete="CASCADE"), primary_key=True
    )
