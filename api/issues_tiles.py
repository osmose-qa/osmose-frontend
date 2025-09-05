from typing import Any, Dict, List, Optional

from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, Request, Response

from modules import query, tiles
from modules.dependencies import commons_params, database
from modules.fastapi_utils import GeoJSONResponse
from modules.GeoJSONTypes import GeoJSONFeature, GeoJSONFeatureCollection

router = APIRouter()


class MVTResponse(Response):
    media_type = "application/vnd.mapbox-vector-tile"


def _errors_geojson(
    results: List[Dict[str, Any]],
    z: int,
    limit: int,
) -> GeoJSONFeatureCollection:
    if not results or len(results) == 0:
        return {
            "type": "FeatureCollection",
            "features": [],
        }
    else:
        issues_features: List[GeoJSONFeature] = []
        for res in sorted(results, key=lambda res: -res["lat"]):
            issues_features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(res["lon"]), float(res["lat"])],
                    },
                    "properties": {
                        "uuid": res["uuid"],
                        "item": res["item"] or 0,
                        "class": res["class"] or 0,
                    },
                }
            )

        features_collection: GeoJSONFeatureCollection = {
            "type": "FeatureCollection",
            "features": issues_features,
        }

        return features_collection


@router.get(
    "/0.3/issues/{z}/{x}/{y}.heat.mvt",
    response_class=MVTResponse,
    response_model=None,
    tags=["tiles"],
)
async def heat(
    request: Request,
    z: int,
    x: int,
    y: int,
    db: Connection = Depends(database.db),
    params=Depends(commons_params.params),
) -> Optional[Response]:
    COUNT = 32

    lon1, lat2 = tiles.tile2lonlat(x, y, z)
    lon2, lat1 = tiles.tile2lonlat(x + 1, y + 1, z)

    items = query._build_where_item(params.item, "items")
    params.tilex = x
    params.tiley = y
    params.zoom = z

    if params.zoom > 18:
        return None

    limit = await db.fetchrow(
        """
SELECT
    SUM((SELECT SUM(t) FROM UNNEST(number) t))
FROM
    items
WHERE
"""
        + items
    )
    if limit and limit[0]:
        limit = float(limit[0])
    else:
        raise HTTPException(status_code=404)

    join, where, sql_params = query._build_param(
        None,
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
        tilex=params.tilex,
        tiley=params.tiley,
        zoom=params.zoom,
    )

    sql_params += [lon1, lat1, lon2, lat2, COUNT]
    sql = (
        f"""
SELECT
    COUNT(*) AS count,
    (
        (lon-${len(sql_params)-4}) * ${len(sql_params)} /
            (${len(sql_params)-2}-${len(sql_params)-4}) - 0.5
    )::int AS x,
    (
        (lat-${len(sql_params)-3}) * ${len(sql_params)} /
            (${len(sql_params)-1}-${len(sql_params)-3}) + 0.5
    )::int AS y,
    mode() WITHIN GROUP (ORDER BY items.marker_color) AS color
FROM
"""
        + join
        + """
WHERE
"""
        + where
        + """
GROUP BY
    x, y
"""
    )

    sql_params += [params.limit, params.zoom]
    sql = f"""
    WITH
    grid AS ({sql}),
    grid_count AS (
        SELECT
            greatest(
                (
                    log(count)
                    / log(${len(sql_params)-1} / ((${len(sql_params)} - 4 + 1 + sqrt(${len(sql_params)-2})) ^ 2))
                    * 255
                )::int,
                CASE WHEN count > 0 THEN 1 ELSE 0 END
            ) AS count,
            x AS x, ${len(sql_params)-2} - y AS y, color
        FROM
            grid
    ),
    a AS (
        SELECT
            least(count, 255) AS count,
            ('0x' || substring(color, 2))::int AS color,
            ST_MakeEnvelope(x, y, x+1, y+1) AS geom
        FROM
            grid_count
        WHERE
            count > 0
    )
    SELECT ST_AsMVT(a, 'issues', ${len(sql_params)-2}::int, 'geom') FROM a
    """
    results = await db.fetchval(sql, *sql_params)
    if results is None or len(results) == 0:
        return Response(status_code=204)
    else:
        return MVTResponse(results)


def _issues_params(
    z: int,
    x: int,
    y: int,
    db: Connection,
    params: commons_params.Params,
) -> commons_params.Params:
    params.limit = min(params.limit, 50 if z > 18 else 10000)
    params.tilex = x
    params.tiley = y
    params.zoom = z
    params.full = False

    return params


async def _issues(
    z: int,
    x: int,
    y: int,
    db: Connection,
    params: commons_params.Params,
) -> List[Dict[str, Any]]:
    params = _issues_params(z, x, y, db, params)

    if params.zoom > 18 or params.zoom < 7:
        return []

    return await query._gets(db, params)


@router.get("/0.3/issues/{z}/{x}/{y}.mvt", response_class=MVTResponse, tags=["tiles"])
async def issues_mvt(
    z: int,
    x: int,
    y: int,
    db: Connection = Depends(database.db),
    params: commons_params.Params = Depends(commons_params.params),
) -> Response:
    params = _issues_params(z, x, y, db, params)

    if params.zoom > 18 or params.zoom < 7:
        return Response(status_code=204)

    results = await query._gets(db, params, mvt=True)
    if results is None or len(results) == 0:
        return Response(status_code=204)
    else:
        return MVTResponse(results)


@router.get(
    "/0.3/issues/{z}/{x}/{y}.geojson", response_class=GeoJSONResponse, tags=["tiles"]
)
async def issues_geojson(
    z: int,
    x: int,
    y: int,
    db: Connection = Depends(database.db),
    params: commons_params.Params = Depends(commons_params.params),
) -> GeoJSONFeatureCollection:
    params = _issues_params(z, x, y, db, params)

    if params.zoom > 18 or params.zoom < 7:
        return Response(status_code=204)

    results = await query._gets(db, params)
    return _errors_geojson(results, z, params.limit)
