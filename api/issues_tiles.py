import math
from typing import Any, Dict, List, Optional

import mapbox_vector_tile  # type: ignore
from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from shapely.geometry import Point, Polygon  # type: ignore

from modules import query, tiles
from modules.dependencies import commons_params, database
from modules.fastapi_utils import GeoJSONResponse
from modules.GeoJSONTypes import GeoJSONFeature, GeoJSONFeatureCollection

router = APIRouter()


class MVTResponse(Response):
    media_type = "application/vnd.mapbox-vector-tile"

    def render(self, content: Any) -> bytes:
        return mapbox_vector_tile.encode(
            content["content"],
            extents=content.get("extents", 2048),
            quantize_bounds=content.get("quantize_bounds"),
        )


def mvtResponse(content) -> Response:
    if not content or not content["content"]:
        return Response(status_code=204)
    else:
        return MVTResponse(content, media_type="application/vnd.mapbox-vector-tile")


def _errors_mvt(
    results: List[Dict[str, Any]],
    z: int,
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    limit: int,
) -> Optional[Dict[str, Any]]:
    if not results or len(results) == 0:
        return None
    else:
        limit_feature = []
        if len(results) == limit and z < 18:
            limit_feature = [
                {
                    "name": "limit",
                    "features": [
                        {
                            "geometry": Point(
                                (min_lon + max_lon) / 2, (min_lat + max_lat) / 2
                            )
                        }
                    ],
                }
            ]

        issues_features = []
        for res in sorted(results, key=lambda res: -res["lat"]):
            issues_features.append(
                {
                    "id": res["id"],
                    "geometry": Point(res["lon"], res["lat"]),
                    "properties": {
                        "uuid": str(res["uuid"]),
                        "item": res["item"] or 0,
                        "class": res["class"] or 0,
                    },
                }
            )

        return {
            "content": [{"name": "issues", "features": issues_features}]
            + limit_feature,
            "quantize_bounds": (min_lon, min_lat, max_lon, max_lat),
        }


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
    COUNT(*),
    (
        (lon-${len(sql_params)-4}) * ${len(sql_params)} /
            (${len(sql_params)-2}-${len(sql_params)-4}) + 0.5
    )::int AS latn,
    (
        (lat-${len(sql_params)-3}) * ${len(sql_params)} /
            (${len(sql_params)-1}-${len(sql_params)-3}) + 0.5
    )::int AS lonn,
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
    latn,
    lonn
"""
    )

    features = []
    for row in await db.fetch(sql, *sql_params):
        count, x, y, color = row
        count = max(
            int(
                math.log(count)
                / math.log(limit / ((z - 4 + 1 + math.sqrt(COUNT)) ** 2))
                * 255
            ),
            1 if count > 0 else 0,
        )
        if count > 0:
            count = 255 if count > 255 else count
            features.append(
                {
                    "geometry": Polygon(
                        [(x, y), (x - 1, y), (x - 1, y - 1), (x, y - 1)]
                    ),
                    "properties": {"color": int(color[1:], 16), "count": count},
                }
            )

    return mvtResponse(
        {
            "content": [{"name": "issues", "features": features}],
            "extents": COUNT,
        }
    )


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

    results = await query._gets(db, params)
    lon1, lat2 = tiles.tile2lonlat(x, y, z)
    lon2, lat1 = tiles.tile2lonlat(x + 1, y + 1, z)
    return mvtResponse(_errors_mvt(results, z, lon1, lat1, lon2, lat2, params.limit))


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
