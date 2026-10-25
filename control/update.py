import os
import sys
import tempfile
from typing import Any, Dict, List, Literal, Optional

from asyncpg import Connection
from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from fastapi.responses import PlainTextResponse

from modules.dependencies import database

from . import update_utils

router = APIRouter()


@router.post("/send-update", response_class=PlainTextResponse, tags=["upload"])
async def user(
    content: UploadFile,
    request: Request,
    analyser: str = Form(),
    country: str = Form(),
    code: str = Form(),
    db: Connection = Depends(database.db_rw),
) -> Literal["OK"]:
    source_id = await db.fetchval(
        """
SELECT
    id
FROM
    sources
    JOIN sources_password ON
        sources.id = source_id
WHERE
    analyser = $1 AND
    country = $2 AND
    password = $3
LIMIT 1
""",
        analyser,
        country,
        code,
    )

    if not source_id and not os.environ.get("OSMOSE_UNLOCKED_UPDATE"):
        raise HTTPException(status_code=403, detail="AUTH FAIL")
    elif not source_id and os.environ.get("OSMOSE_UNLOCKED_UPDATE"):
        source_id = await db.fetchval(
            "SELECT COALESCE(MAX(id), 0) + 1 AS id FROM sources"
        )
        await db.execute(
            "INSERT INTO sources(id, country, analyser) VALUES ($1, $2, $3)",
            source_id,
            country,
            analyser,
        )
        await db.execute(
            "INSERT INTO sources_password(source_id, password) VALUES($1, $2)",
            source_id,
            code,
        )

    remote_ip = request.client.host if request.client else None

    if not content.filename:
        raise HTTPException(status_code=406, detail="FAIL: Filename required.")
    try:
        name, ext = os.path.splitext(content.filename)
        if ext not in (".bz2", ".gz", ".xml"):
            raise HTTPException(
                status_code=406, detail="FAIL: File extension not allowed."
            )

        with tempfile.NamedTemporaryFile(mode="wb", suffix=ext) as f:
            f.write(await content.read())
            f.flush()
            await update_utils.update(db, source_id, f.name, remote_ip=remote_ip)

    except update_utils.OsmoseUpdateAlreadyDone:
        raise HTTPException(status_code=400, detail="FAIL: Already up to date")

    except Exception:
        import traceback
        from io import StringIO

        s = StringIO()
        sys.stderr = s
        traceback.print_exc()
        sys.stderr = sys.__stderr__
        trace = s.getvalue()
        print(trace)
        raise HTTPException(status_code=500, detail=trace.rstrip())

    return "OK"


async def _status_object(db: Connection, type: str, source: int) -> Optional[List[int]]:
    s = await db.fetchval(
        """
SELECT
    string_agg(elem->>'id', ',')
FROM
    (SELECT unnest(elems) AS elem FROM markers WHERE source_id=$1) AS t
WHERE
    elem->>'type' = $2
""",
        source,
        type,
    )
    if s:
        return list(map(int, s.split(",")))
    else:
        return None


@router.get("/status/{country}/{analyser}", tags=["upload"])
async def status(
    country: str,
    analyser: str,
    objects: bool = False,
    db: Connection = Depends(database.db),
) -> Dict[str, Any]:
    r = await db.fetchrow(
        """
SELECT
    timestamp, source_id, analyser_version
FROM
    updates_last
WHERE
    source_id = (SELECT id FROM sources WHERE analyser = $1 AND country = $2)
""",
        analyser,
        country,
    )
    if r and r["timestamp"]:
        return {
            "version": 1,
            "timestamp": str(r["timestamp"].replace(tzinfo=None)),
            "analyser_version": str(r["analyser_version"] or ""),
            "nodes": (
                await _status_object(db, "N", r["source_id"])
                if objects is not False
                else None
            ),
            "ways": (
                await _status_object(db, "W", r["source_id"])
                if objects is not False
                else None
            ),
            "relations": (
                await _status_object(db, "R", r["source_id"])
                if objects is not False
                else None
            ),
        }
    else:
        raise HTTPException(status_code=404)
