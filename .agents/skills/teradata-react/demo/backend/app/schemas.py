from datetime import datetime
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    database: str


class Overview(BaseModel):
    database_count: int
    table_count: int
    user_count: int
    total_perm_bytes: float


class DatabaseRow(BaseModel):
    databasename: str
    ownername: str | None = None
    permspace: float
    spoolspace: float
    tempspace: float


class TableRow(BaseModel):
    databasename: str
    tablename: str
    tablekind: str
    createtimestamp: datetime | None = None


class UserRow(BaseModel):
    username: str
    createtimestamp: datetime | None = None
    lastaltertimestamp: datetime | None = None
    ownername: str | None = None


class SpaceByDatabase(BaseModel):
    databasename: str
    currentperm: float
    maxperm: float
