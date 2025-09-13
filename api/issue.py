import copy
import io
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, Request

from modules import OsmSax, utils
from modules.dependencies import database, langs
from modules.fastapi_utils import XMLResponse
from modules.query import fixes_default
from modules.utils import LangsNegociation

from .issue_utils import _get, _keys, t2l

router = APIRouter()

Status = Literal["done", "false"]


async def _remove_bug_uuid(db: Connection, uuid: UUID, status: Status) -> int:
    # find source
    source_id = None
    sql = "SELECT source_id,class FROM markers WHERE uuid = $1"
    for res in await db.fetch(sql, uuid):
        source_id = res["source_id"]
        class_id = res["class"]

    if not source_id:
        return -1

    async with db.transaction():
        await db.execute("DELETE FROM markers_status WHERE uuid=$1", uuid)

        await db.execute(
            """INSERT INTO markers_status
                            (source_id,item,class,elems,date,status,lat,lon,subtitle,uuid)
                        SELECT source_id,item,class,elems,NOW(),$1,
                                lat,lon,subtitle,uuid
                        FROM markers
                        WHERE uuid = $2
                        ON CONFLICT DO NOTHING""",
            status,
            uuid,
        )

        await db.execute("DELETE FROM markers WHERE uuid = $1", uuid)
        await db.execute(
            "UPDATE markers_counts SET count = count - 1 WHERE source_id = $1 AND class = $2",
            source_id,
            class_id,
        )

    return 0


@router.get("/0.3/issue/{uuid}/fresh_elems", tags=["issues"])
async def fresh_elems_uuid(
    request: Request,
    uuid: UUID,
    db: Connection = Depends(database.db),
) -> Dict[str, Any]:
    return await fresh_elems_uuid_num(request, uuid=uuid, db=db)


@router.get("/0.3/issue/{uuid}/fresh_elems/{fix_num}", tags=["issues"])
async def fresh_elems_uuid_num(
    request: Request,
    uuid: UUID,
    fix_num: Optional[int] = None,
    db: Connection = Depends(database.db),
) -> Dict[str, Any]:
    data_type = {"N": "node", "W": "way", "R": "relation", "I": "infos"}

    marker = await _get(db, uuid=uuid)
    if not marker:
        raise HTTPException(status_code=410, detail="Id is not present in database.")

    def expand_tags(tags):
        t = []
        for k, v in tags.items():
            t.append({"k": k, "v": v})
        return t

    elems = {}
    for elem in marker["elems"]:
        if elem["type"]:
            fresh_elem = utils.fetch_osm_elem(data_type[elem["type"]], elem["id"])

            if fresh_elem and len(fresh_elem) > 0:
                tmp_elem = {
                    data_type[elem["type"]]: True,
                    "type": data_type[elem["type"]],
                    "id": elem["id"],
                    "version": fresh_elem["version"],
                    "tags": fresh_elem["tag"],
                }
                elems[data_type[elem["type"]] + str(elem["id"])] = tmp_elem

    ret: Dict[str, Any] = {
        "uuid": uuid,
        "elems": list(elems.values()),
    }

    if fix_num is not None:
        ret["fix"] = {}
        for res in marker["fixes"][fix_num]:
            tid = data_type[res["type"]] + str(res["id"])
            if tid in elems:
                fix_elem_tags = copy.copy(elems[tid]["tags"])
                for k in res["delete"]:
                    if k in fix_elem_tags:
                        del fix_elem_tags[k]
                for k, v in res["create"].items():
                    fix_elem_tags[k] = v
                for k, v in res["modify"].items():
                    fix_elem_tags[k] = v

                ret["fix"][tid] = fix_elem_tags

    for elem in ret["elems"]:
        elem["tags"] = expand_tags(elem["tags"])

    return ret


@router.get("/0.3/issue/{uuid}", tags=["issues"])
async def error_uuid(
    uuid: UUID,
    db: Connection = Depends(database.db),
    langs: LangsNegociation = Depends(langs.langs),
) -> Dict[str, Any]:
    return _error(
        3,
        db,
        langs,
        uuid,
        await _get(db, uuid=uuid),
    )


def _error(
    version,
    db: Connection,
    langs: LangsNegociation,
    uuid: Optional[UUID],
    marker: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    if not marker:
        raise HTTPException(status_code=410, detail="Id is not present in database.")

    data_type = {"N": "node", "W": "way", "R": "relation", "I": "infos"}

    lat = str(marker["lat"])
    lon = str(marker["lon"])
    title = utils.i10n_select(marker["title"], langs)
    subtitle = utils.i10n_select(marker["subtitle"], langs)
    b_date = marker["timestamp"]
    item = marker["item"] or 0
    classs = marker["class"] or 0

    elems = []
    for elem in marker["elems"] or []:
        if elem["type"]:
            tags = elem.get("tags", {})
            tmp_elem = {
                data_type[elem["type"]]: True,
                "type": data_type[elem["type"]],
                "id": elem["id"],
                "tags": t2l.addLinks(tags),
                "fixes": [],
            }
            for fix_index, fix_group in enumerate(marker["fixes"] or []):
                for fix in fix_group:
                    if (
                        fix["type"]
                        and fix["type"] == elem["type"]
                        and fix["id"] == elem["id"]
                    ):
                        tmp_elem["fixes"].append(
                            {
                                "num": fix_index,
                                "add": t2l.addLinks(fix["create"]),
                                "mod": t2l.addLinks(fix["modify"]),
                                "del": _keys(fix["delete"]),
                            }
                        )
            elems.append(tmp_elem)

    new_elems = []
    for fix_index, fix_group in enumerate(marker["fixes"] or []):
        for fix in fix_group:
            if fix["type"]:
                found = False
                for e in elems:
                    if e["type"] == data_type[fix["type"]] and e["id"] == fix["id"]:
                        found = True
                        break
                if not found:
                    new_elems.append(
                        {
                            "num": fix_index,
                            "add": t2l.addLinks(fix["create"]),
                            "mod": t2l.addLinks(fix["modify"]),
                            "del": _keys(fix["delete"]),
                        }
                    )

    if version == 2:
        return {
            "lat": lat,
            "lon": lon,
            "minlat": float(lat) - 0.002,
            "maxlat": float(lat) + 0.002,
            "minlon": float(lon) - 0.002,
            "maxlon": float(lon) + 0.002,
            "error_id": marker["id"],
            "title": title and title["auto"],
            "subtitle": subtitle and subtitle["auto"],
            "b_date": b_date.strftime("%Y-%m-%d"),
            "item": item,
            "class": classs,
            "elems": elems,
            "new_elems": new_elems,
            "elems_id": ",".join(
                map(lambda elem: elem["type_long"] + str(elem["id"]), marker["elems"])
            ),
            "url_help": "",  # Keep for retro compatibility
        }
    else:
        return {
            "lat": lat,
            "lon": lon,
            "minlat": float(lat) - 0.002,
            "maxlat": float(lat) + 0.002,
            "minlon": float(lon) - 0.002,
            "maxlon": float(lon) + 0.002,
            "uuid": uuid,
            "title": title,
            "subtitle": subtitle,
            "b_date": b_date.strftime("%Y-%m-%d"),
            "item": item,
            "class": classs,
            "elems": elems,
            "new_elems": new_elems,
        }


@router.get("/0.3/issue/{uuid}/{status}", tags=["issues"])
async def status_uuid(
    request: Request,
    uuid: UUID,
    status: Status,
    db: Connection = Depends(database.db_rw),
) -> None:
    if await _remove_bug_uuid(db, uuid, status) == 0:
        return None
    else:
        raise HTTPException(status_code=410, detail="FAIL")


async def _get_fix(
    db: Connection,
    fix_num: int,
    err_id: Optional[int] = None,
    uuid: Optional[UUID] = None,
) -> List[Dict[str, Any]]:
    if err_id:
        sql = "SELECT fixes FROM markers WHERE id = $1"
        fix = await db.fetchrow(sql, err_id)
    else:
        sql = "SELECT fixes FROM markers WHERE uuid = $1"
        fix = await db.fetchrow(sql, uuid)

    if not fix:
        raise HTTPException(status_code=410, detail="Fix is not present in database.")

    return fixes_default(fix[0])[fix_num]


@router.get(
    "/0.3/issue/{uuid}/fix/{fix_num}", response_class=XMLResponse, tags=["issues"]
)
async def fix_uuid_num(
    uuid: UUID, fix_num: int = 0, db: Connection = Depends(database.db)
) -> str:
    fix = await _get_fix(db, fix_num, uuid=uuid)
    if fix:
        for res in fix:
            if "id" in res and res["id"]:
                out = io.StringIO()
                o = OsmSaxFixWriter(
                    out,
                    "UTF-8",
                    res["type"],
                    res["id"],
                    res["create"],
                    res["modify"],
                    res["delete"],
                )
                o.startDocument()

                data_type = {"N": "node", "W": "way", "R": "relation"}
                osm_read = utils.fetch_osm_data(data_type[res["type"]], res["id"])
                if osm_read:
                    osm_read.CopyTo(o)

                return out.getvalue()

            else:
                # create new object
                res2 = await db.fetchrow(
                    "SELECT lat, lon FROM markers WHERE uuid = $1", uuid
                )
                if res2:
                    data: Dict[str, Any] = {}
                    data["id"] = -1
                    data["tag"] = {}
                    for k, v in res["create"].items():
                        data["tag"][k] = v
                    data["lat"] = res2["lat"]
                    data["lon"] = res2["lon"]
                    data["action"] = "modify"  # Even for creation action is 'modify'

                    if "type" not in res or res["type"] == "N":
                        return OsmSax.NodeToXml(data, full=True)
                    elif res["type"] == "W":
                        return OsmSax.WayToXml(data, full=True)
                    elif res["type"] == "R":
                        return OsmSax.RelationToXml(data, full=True)

    raise HTTPException(status_code=412, detail="Precondition Failed")


class OsmSaxFixWriter(OsmSax.OsmSaxWriter):
    def __init__(
        self, out, enc, elem_type, elem_id, tags_create, tags_modify, tags_delete
    ):
        OsmSax.OsmSaxWriter.__init__(self, out, enc)

        self.elem_type = elem_type
        self.elem_id = elem_id
        self.tags_create = tags_create
        self.tags_modify = tags_modify
        self.tags_delete = tags_delete

    def fix_tags(self, data):
        for k in self.tags_delete:
            if k in data["tag"]:
                del data["tag"][k]
        for k, v in self.tags_create.items():
            data["tag"][k] = v
        for k, v in self.tags_modify.items():
            data["tag"][k] = v
        data["action"] = "modify"
        return data

    def NodeCreate(self, data):
        if self.elem_type == "N" and self.elem_id == data["id"]:
            data = self.fix_tags(data)
        OsmSax.OsmSaxWriter.NodeCreate(self, data)

    def WayCreate(self, data):
        if self.elem_type == "W" and self.elem_id == data["id"]:
            data = self.fix_tags(data)
        OsmSax.OsmSaxWriter.WayCreate(self, data)

    def RelationCreate(self, data):
        if self.elem_type == "R" and self.elem_id == data["id"]:
            data = self.fix_tags(data)
        OsmSax.OsmSaxWriter.RelationCreate(self, data)
