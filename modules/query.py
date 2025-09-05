from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from asyncpg import Connection

from . import tiles
from .dependencies.commons_params import Params, UseDevItem


def _build_where_item(table: str, item: str) -> str:
    if item == "":
        where = "1=2"
    elif item is None or item == "xxxx":
        where = "1=1"
    else:
        where_list = []
        items = []
        for i in item.split(","):
            try:
                if "xxx" in i:
                    n = int(i[0])
                    where_list.append(
                        "(%s.item >= %s000 AND %s.item < %s000)"
                        % (table, n, table, n + 1)
                    )
                else:
                    items.append(str(int(i)))
            except Exception:
                pass
        if items != []:
            where_list.append("%s.item = ANY(ARRAY[%s])" % (table, ",".join(items)))
        if where_list != []:
            where = "(%s)" % " OR ".join(where_list)
        else:
            where = "1=1"
    return where


def _build_where_class(table: str, classs: List[int]) -> str:
    return "{0}.class IN ({1})".format(table, ",".join(map(str, classs)))


def _build_param(
    bbox: Optional[List[float]],
    sources: Optional[List[List[int]]],
    item: Optional[str],
    level: Optional[List[int]],
    users: Optional[List[str]],
    classs: Optional[List[int]],
    country: Optional[str],
    useDevItem: UseDevItem,
    status,  #: Optional[Status],
    tags: Optional[List[str]],
    fixable,  #: Optional[Fixable],
    forceTable: Iterable[str] = [],
    summary: bool = False,
    stats: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    last_update=None,
    tilex: Optional[int] = None,
    tiley: Optional[int] = None,
    zoom: Optional[int] = None,
    osm_type: Optional[str] = None,
    osm_id: Optional[int] = None,
) -> Tuple[str, str, List[Any]]:
    base_table = None
    join = ""
    where = ["1=1"]
    params = []

    if summary:
        base_table = "markers_counts"
        join += "markers_counts AS markers"
    elif stats:
        base_table = "stats"
        if item:
            join += """(
                SELECT stats.*, item
                FROM stats
                    JOIN markers_counts ON
                        markers_counts.source_id = stats.source_id AND
                        markers_counts.class = stats.class
            ) AS markers"""
        else:
            join += "stats AS markers"
    elif status in ("done", "false"):
        base_table = "markers_status"
        join += "markers_status AS markers"
        params.append(status)
        where.append(f"markers.status = ${len(params)}")
    else:
        base_table = "markers"
        join += "markers"

    if sources:
        source2 = []
        for source in sources:
            if len(source) == 1:
                params.append(source[0])
                source2.append(f"(markers.source_id=${len(params)})")
            else:
                params += [source[0], source[1]]
                source2.append(
                    f"(markers.source_id=${len(params) - 1} AND markers.class=${len(params)})"
                )
        where.append("(" + " OR ".join(source2) + ")")

    tables = list(forceTable)
    tablesLeft = []

    if (level and level != [1, 2, 3]) or tags:
        tables.append("class")
    if country is not None:
        tables.append("sources")
    if not stats or useDevItem in ("true", "false", "all"):
        tables.append("items")
        if useDevItem in ("true", "all"):
            tablesLeft.append("items")
    if last_update:
        tables.append("updates_last")

    if "markers_counts" in tables:
        join += """
        JOIN markers_counts ON
            markers.source_id = markers_counts.source_id AND
            markers.class = markers_counts.class"""

    if "class" in tables:
        join += """
        JOIN class ON
            markers.item = class.item AND
            markers.class = class.class"""

    if "sources" in tables:
        join += """
        JOIN sources ON
            markers.source_id = sources.id"""

    if "items" in tables:
        join += """
        %sJOIN items ON
            markers.item = items.item""" % (
            "LEFT " if "items" in tablesLeft else ""
        )

    if "updates_last" in tables:
        join += """
        JOIN updates_last ON
            updates_last.source_id = markers.source_id"""

    if item is not None:
        where.append(_build_where_item("markers", item))

    if level and level != [1, 2, 3]:
        params.append(level)
        where.append(f"class.level = ANY (${len(params)})")

    if classs:
        params.append(classs)
        where.append(f"markers.class = ANY (${len(params)})")

    if tilex and tiley and zoom:
        minlon, minlat = tiles.tile2lonlat(tilex, tiley, zoom)
        maxlon, maxlat = tiles.tile2lonlat(tilex + 1, tiley + 1, zoom)
        bbox = [minlon, minlat, maxlon, maxlat]

    if bbox:
        params += bbox
        where.append(
            f"""
            point(markers.lon, markers.lat) <@ box(
                point(${len(params)-3}, ((${len(params)-2})::numeric + 180) % 360 - 180),
                point(${len(params)-1}, ((${len(params)})::numeric + 180) % 360 - 180)
            )"""
        )

    if country is not None:
        if len(country) >= 1 and country[-1] == "*":
            country = country[:-1] + "%"
        params.append(country)
        where.append(f"sources.country LIKE ${len(params)}")

    if status not in ("done", "false") and useDevItem == "true":
        where.append("items.item IS NULL")

    if status not in ("done", "false") and users:
        params.append(users)
        where.append(f"${len(params)} && marker_usernames(markers.elems)")

    if stats:
        if start_date and end_date:
            params += [start_date, end_date]
            where.append(
                f"markers.timestamp_range && tsrange(${len(params)-1}, ${len(params)}, '[]')"
            )
        elif start_date:
            params.append(start_date)
            where.append(
                f"markers.timestamp_range && tsrange(${len(params)}, NULL, '[)')"
            )
        elif end_date:
            params.append(end_date)
            where.append(
                f"markers.timestamp_range && tsrange(NULL, ${len(params)}, '(]')"
            )
    elif status in ("done", "false"):
        if start_date:
            params.append(start_date)
            where.append(f"markers.date > ${len(params)}")
        if end_date:
            params.append(end_date)
            where.append(f"markers.date < ${len(params)}")

    if tags:
        params.append(tags)
        where.append(f"class.tags::text[] && ${len(params)}")

    if fixable == "online":
        where.append(
            "(SELECT bool_or(fix->>'id' != '0') FROM (SELECT jsonb_array_elements(unnest(fixes))) AS t(fix))"
        )
    elif fixable == "josm":
        where.append("fixes IS NOT NULL")

    if osm_type and osm_id and base_table == "markers":
        params.append(osm_id)
        where.append(
            f"ARRAY[${len(params)}::bigint] <@ marker_elem_ids(elems)"
        )  # Match the index
        params += [osm_type[0].upper(), osm_id]
        where.append(
            f"""(SELECT
                    bool_or(elem->>'type' = ${len(params)-1} AND
                    (elem->>'id')::bigint = ${len(params)})
                FROM (SELECT unnest(elems)) AS t(elem))"""
        )  # Recheck with type

    return (join, " AND\n        ".join(where), params)


def fixes_default(fixes: List[List[Dict[str, Any]]]) -> List[List[Dict[str, Any]]]:
    return list(
        map(
            lambda fix_elems: list(
                map(
                    lambda fix: dict(
                        fix,
                        type=fix.get("type", "N"),
                        id=fix.get("id", 0),
                        create=fix.get("create", {}),
                        modify=fix.get("modify", {}),
                        delete=fix.get("delete", []),
                    ),
                    fix_elems,
                )
            ),
            fixes,
        )
    )


async def _gets(
    db: Connection, params: Params, mvt: bool = False
) -> Union[List[Dict[str, Any]], bytes]:
    sqlbase = """
    SELECT
        uuid_to_bigint(uuid) as id,
        markers.uuid AS uuid,
        markers.item,
        markers.class,
        markers.lat::float,
        markers.lon::float,"""
    if params.full:
        sqlbase += """
        markers.source_id,
        markers.elems,
        markers.subtitle,
        sources.country,
        sources.analyser,
        class.title,
        class.level,
        updates_last.timestamp,
        items.menu"""
        if params.status not in ("done", "false"):
            sqlbase += """,
        markers.fixes,
        -1 AS date"""
        else:
            sqlbase += """,
        NULL AS fixes,
        markers.date,"""
    sqlbase = (
        sqlbase[0:-1]
        + """
    FROM
        %s
        JOIN updates_last ON
            markers.source_id = updates_last.source_id
    WHERE
        %s AND
        updates_last.timestamp > (now() - interval '3 months')
    """
    )

    if params.full:
        forceTable = ["class", "sources"]
    else:
        forceTable = []

    join, where, sql_params = _build_param(
        params.bbox,
        params.source,
        params.item,
        params.level,
        params.users,
        params.classs,
        params.country,
        params.useDevItem,
        params.status,
        params.tags,
        params.fixable,
        forceTable=forceTable,
        start_date=params.start_date,
        end_date=params.end_date,
        tilex=params.tilex,
        tiley=params.tiley,
        zoom=params.zoom,
        osm_type=params.osm_type,
        osm_id=params.osm_id,
    )

    if params.limit:
        sql_params.append(params.limit)
        sqlbase += f"""
    LIMIT
        ${len(sql_params)}"""

    sql = sqlbase % (join, where)

    if mvt:
        sql_params.extend([params.limit, params.zoom, params.tilex, params.tiley])
        sql = f"""
        WITH
        query AS ({sql}),
        issues AS (
            SELECT
                (id >> 32)::integer AS id, uuid, coalesce(item, 0) AS item, coalesce(class, 0) AS class,
                ST_AsMVTGeom(
                    ST_Transform(ST_SetSRID(ST_MakePoint(lon, lat), 4326), 3857),
                    ST_TileEnvelope(${len(sql_params)-2}, ${len(sql_params)-1}, ${len(sql_params)}),
                    4096, 0, false
                ) AS geom
            FROM query
        ),
        limit_ AS (
            SELECT
                ST_AsMVTGeom(
                    ST_Centroid(ST_TileEnvelope(${len(sql_params)-2}, ${len(sql_params)-1}, ${len(sql_params)})),
                    ST_TileEnvelope(${len(sql_params)-2}, ${len(sql_params)-1}, ${len(sql_params)}),
                    4096, 0, false
                ) AS geom
            WHERE (SELECT COUNT(*) FROM query) >= ${len(sql_params)-3}
        ),
        layers AS (
            SELECT ST_AsMVT(issues, 'issues', 4096, 'geom', 'id') AS layer FROM issues
            UNION ALL
            SELECT ST_AsMVT(limit_, 'limit', 4096, 'geom') AS layer FROM limit_
        )
        SELECT string_agg(layer, ''::bytea) FROM layers
        """
        return await db.fetchval(sql, *sql_params)

    results = list(await db.fetch(sql, *sql_params))
    return list(
        map(
            lambda res: {
                **res,
                **(
                    {
                        "elems": list(
                            map(
                                lambda elem: dict(
                                    elem,
                                    type_long={
                                        "N": "node",
                                        "W": "way",
                                        "R": "relation",
                                    }[elem["type"]],
                                ),
                                res["elems"],
                            )
                        )
                    }
                    if "elems" in res and res["elems"]
                    else {}
                ),
            },
            results,
        )
    )


async def _count(
    db: Connection,
    params: Params,
    by: List[str],
    extraFrom: List[str] = [],
    extraFields=[],
    orderBy=False,
) -> List[Dict[str, Any]]:
    params.full = False

    if params.bbox or params.users or (params.status in ("done", "false")):
        summary = False
        countField = ["count(*) AS count"]
    else:
        summary = True
        countField = ["SUM(markers.count) AS count"]

    byTable = set(list(map(lambda x: x.split(".")[0], by)) + extraFrom)
    sqlbase = """
    SELECT
        %s
    FROM
        %s
    WHERE
        %s
    GROUP BY
        %s
    ORDER BY
        %s
    """

    select = ",\n        ".join(by + extraFields + countField)
    groupBy = ",\n        ".join(map(lambda b: b.split(" AS ")[0], by))
    if orderBy:
        order = groupBy
    else:
        order = "count DESC"
    last_update = False
    if "updates_last" in byTable:
        last_update = True

    join, where, sql_params = _build_param(
        params.bbox,
        params.source,
        params.item,
        params.level,
        params.users,
        params.classs,
        params.country,
        params.useDevItem,
        params.status,
        params.tags,
        params.fixable,
        summary=summary,
        forceTable=byTable,
        start_date=params.start_date,
        end_date=params.end_date,
        last_update=last_update,
        tilex=params.tilex,
        tiley=params.tiley,
        zoom=params.zoom,
        osm_type=params.osm_type,
        osm_id=params.osm_id,
    )

    if params.limit:
        sql_params.append(params.limit)
        sqlbase += f" LIMIT ${len(sql_params)}"

    sql = sqlbase % (select, join, where, groupBy, order)

    return list(map(dict, await db.fetch(sql, *sql_params)))
