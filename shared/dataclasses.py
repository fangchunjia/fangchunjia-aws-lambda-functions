from dataclasses import dataclass


@dataclass
class About:
    text: dict


@dataclass
class ProjectMediaLayoutItem:
    key: str
    size: str = 'm'


@dataclass
class Project:
    id: str
    name: str
    description: str
    categoryId: str
    coverKey: str
    year: int
    link: str
    mediaLayout: list[ProjectMediaLayoutItem]


@dataclass
class ProjectInfo:
    id: str
    name: str
    categoryId: str
    coverKey: str
    year: int
    link: str


@dataclass
class MediaMetadata:
    key: str
    # seq: int
    # size: str