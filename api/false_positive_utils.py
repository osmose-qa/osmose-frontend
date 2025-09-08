from typing import Any, Dict, List, Literal, Optional, Tuple
from uuid import UUID

from asyncpg import Connection

Status = Literal["false"]


async def _get(
    db: Connection,
    status: Status,
    err_id: Optional[int] = None,
    uuid: Optional[UUID] = None,
) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    columns = [
        "markers_status.item",
        "source_id",
        "markers_status.class",
        "lat::float",
        "lon::float",
        "title",
        "subtitle",
        "date AS timestamp",
    ]

    if err_id:
        sql = (
            "SELECT "
            + ",".join(columns)
            + """
        FROM
            markers_status
            JOIN class ON
                class.item = markers_status.item AND
                class.class = markers_status.class
        WHERE
            status = $1 AND
            uuid_to_bigint(uuid) = $2
        """
        )
        marker = await db.fetchrow(sql, status, err_id)
    else:
        sql = (
            "SELECT "
            + ",".join(columns)
            + """
        FROM
            markers_status
        JOIN class ON
            class.item = markers_status.item AND
            class.class = markers_status.class
        WHERE
            status = $1 AND
            uuid = $2
        """
        )
        marker = await db.fetchrow(sql, status, uuid)

    return (
        dict(marker) if marker is not None else None,
        columns,
    )
