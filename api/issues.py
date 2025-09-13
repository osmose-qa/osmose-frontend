import json
from itertools import groupby
from typing import Any, Dict, List, Literal, Tuple

from asyncpg import Connection
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from lxml import etree

from modules import query, query_meta, utils
from modules.dependencies import commons_params, database, i18n, langs
from modules.fastapi_utils import GeoJSONResponse
from modules.GeoJSONTypes import GeoJSONFeatureCollection
from modules.utils import LangsNegociation, i10n_select_auto, i10n_select_lang

from .issues_utils import csv, gpx, kml, rss

router = APIRouter()


class XMLResponse(Response):
    media_type = "text/xml; charset=utf-8"

    def render(self, content: Any) -> bytes:
        return etree.tostring(content, pretty_print=True)


class KMLResponse(XMLResponse):
    media_type = "application/vnd.google-earth.kml+xml"


class GPXResponse(XMLResponse):
    media_type = "application/gpx+xml"


class RSSResponse(XMLResponse):
    media_type = "application/rss+xml"


class CSVResponse(Response):
    media_type = "text/csv; charset=utf-8"


class NLJSONResponse(Response):
    media_type = "application/x-ndjson; charset=utf-8"

    def render(self, content: Any) -> bytes:
        return ("\x1e" + "\n\x1e".join([json.dumps(line) for line in content])).encode(
            "utf-8"
        )


@router.get("/0.3/issues", tags=["issues"])
@router.get("/0.3/issues.json", tags=["issues"])
async def issues(
    request: Request,
    db: Connection = Depends(database.db),
    langs: LangsNegociation = Depends(langs.langs),
    params=Depends(commons_params.params),
) -> Dict[Literal["issues"], List[Dict[str, Any]]]:
    params.limit = min(params.limit, 100000)
    results = await query._gets(db, params)

    out = []
    for res in results:
        i = {
            "lat": float(res["lat"]),
            "lon": float(res["lon"]),
            "id": res["uuid"],
            "item": str(res["item"]),
        }
        if params.full:
            i.update(
                {
                    "lat": float(res["lat"]),
                    "lon": float(res["lon"]),
                    "id": res["uuid"],
                    "item": str(res["item"]),
                    "source": res["source_id"],
                    "class": res["class"],
                    "subtitle": utils.i10n_select(res["subtitle"], langs),
                    "title": utils.i10n_select(res["title"], langs),
                    "level": res["level"],
                    "update": str(res["timestamp"]),
                    "usernames": list(
                        map(
                            lambda elem: "username" in elem and elem["username"] or "",
                            res["elems"] or [],
                        )
                    ),
                    "osm_ids": dict(
                        map(
                            lambda k_g: (
                                {"N": "nodes", "W": "ways", "R": "relations"}[k_g[0]],
                                list(map(lambda g: g["id"], k_g[1])),
                            ),
                            groupby(
                                sorted(res["elems"] or [], key=lambda e: e["type"]),
                                lambda e: e["type"],
                            ),
                        )
                    ),
                }
            )
        out.append(i)

    return {"issues": out}


@router.get("/0.3/issues.josm", tags=["issues"])
async def issues_josm(
    db: Connection = Depends(database.db),
    params=Depends(commons_params.params),
) -> RedirectResponse:
    params.full = True
    params.limit = min(params.limit, 100000)
    results = await query._gets(db, params)

    objects = set(
        sum(
            map(
                lambda error: list(
                    map(
                        lambda elem: elem["type"].lower() + str(elem["id"]),
                        error["elems"] or [],
                    )
                ),
                results,
            ),
            [],
        )
    )
    return RedirectResponse(
        url=f"http://localhost:8111/load_object?objects={','.join(objects)}"
    )


async def _issues(
    db: Connection,
    langs: LangsNegociation,
    params: commons_params.Params,
    _: i18n.Translator,
) -> Tuple[str, List[Any]]:
    if params.status == "false":
        title = _("False positives")
    elif params.status == "done":
        title = _("Fixed issues")
    else:
        title = _("Open issues")

    items = await query_meta._items_menu(db, langs)
    for res in items:
        if params.item == str(res["item"]):
            menu_auto = i10n_select_auto(res["menu"], langs)
            if menu_auto:
                title += " - " + menu_auto

    params.full = True
    params.limit = min(params.limit, 100000)
    issues = await query._gets(db, params)

    for issue in issues:
        issue["subtitle"] = i10n_select_auto(issue["subtitle"], langs)
        issue["title"] = i10n_select_auto(issue["title"], langs)
        issue["menu"] = i10n_select_auto(issue["menu"], langs)

    return (title, issues)


@router.get("/0.3/issues.rss", response_class=RSSResponse, tags=["issues"])
async def issues_rss(
    request: Request,
    db: Connection = Depends(database.db),
    langs: LangsNegociation = Depends(langs.langs),
    params=Depends(commons_params.params),
    i18n: i18n.Translator = Depends(i18n.i18n),
) -> RSSResponse:
    title, issues = await _issues(db, langs, params, i18n)
    return RSSResponse(
        rss(
            title=title,
            website=utils.website,
            lang=i10n_select_lang(langs),
            params=params,
            query=str(request.query_params),
            main_website=utils.main_website,
            remote_url_read=utils.remote_url_read,
            issues=issues,
            i18n=i18n,
        )
    )


@router.get("/0.3/issues.gpx", response_class=GPXResponse, tags=["issues"])
async def issues_gpx(
    request: Request,
    db: Connection = Depends(database.db),
    langs: LangsNegociation = Depends(langs.langs),
    params=Depends(commons_params.params),
    i18n: i18n.Translator = Depends(i18n.i18n),
) -> GPXResponse:
    title, issues = await _issues(db, langs, params, i18n)
    return GPXResponse(
        gpx(
            title=title,
            website=utils.website,
            lang=i10n_select_lang(langs),
            params=params,
            query=str(request.query_params),
            main_website=utils.main_website,
            remote_url_read=utils.remote_url_read,
            issues=issues,
            i18n=i18n,
        )
    )


@router.get("/0.3/issues.kml", response_class=KMLResponse, tags=["issues"])
async def issues_kml(
    request: Request,
    db: Connection = Depends(database.db),
    langs: LangsNegociation = Depends(langs.langs),
    params=Depends(commons_params.params),
    i18n: i18n.Translator = Depends(i18n.i18n),
) -> KMLResponse:
    title, issues = await _issues(db, langs, params, i18n)
    return KMLResponse(
        kml(
            title=title,
            website=utils.website,
            lang=i10n_select_lang(langs),
            params=params,
            query=str(request.query_params),
            main_website=utils.main_website,
            remote_url_read=utils.remote_url_read,
            issues=issues,
            i18n=i18n,
        )
    )


@router.get("/0.3/issues.csv", response_class=CSVResponse, tags=["issues"])
async def issues_csv(
    request: Request,
    db: Connection = Depends(database.db),
    langs: LangsNegociation = Depends(langs.langs),
    params=Depends(commons_params.params),
    i18n: i18n.Translator = Depends(i18n.i18n),
) -> str:
    title, issues = await _issues(db, langs, params, i18n)
    return csv(
        title=title,
        website=utils.website,
        lang=i10n_select_lang(langs),
        params=params,
        query=str(request.query_params),
        main_website=utils.main_website,
        remote_url_read=utils.remote_url_read,
        issues=issues,
    )


@router.get("/0.3/issues.geojson", response_class=GeoJSONResponse, tags=["issues"])
async def issues_geojson(
    request: Request,
    db: Connection = Depends(database.db),
    langs: LangsNegociation = Depends(langs.langs),
    params=Depends(commons_params.params),
    i18n: i18n.Translator = Depends(i18n.i18n),
) -> GeoJSONFeatureCollection:
    title, issues = await _issues(db, langs, params, i18n)
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        properties["lon"],
                        properties["lat"],
                    ],
                },
                "properties": {
                    k: v for k, v in properties.items() if k not in ("id", "lon", "lat")
                },
            }
            for properties in issues
        ],
    }


@router.get(
    "/0.3/issues.maproulette.geojson", response_class=NLJSONResponse, tags=["issues"]
)
async def issues_maproulette_jsonl(
    request: Request,
    db: Connection = Depends(database.db),
    langs: LangsNegociation = Depends(langs.langs),
    params=Depends(commons_params.params),
    i18n: i18n.Translator = Depends(i18n.i18n),
) -> List[Any]:
    params.limit = 100000
    title, issues = await _issues(db, langs, params, i18n)
    type_map = {"N": "node", "W": "way", "R": "relation"}
    return [
        {
            k: v
            for k, v in {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                properties["lon"],
                                properties["lat"],
                            ],
                        },
                        "properties": {
                            k: v
                            for k, v in properties.items()
                            if k in ("title", "subtitle", "timestamp") and v != ""
                        },
                    },
                ],
                "cooperativeWork": (
                    {
                        "meta": {"version": 2, "type": 1},
                        "operations": [
                            {
                                "operationType": "modifyElement",
                                "data": {
                                    "id": f"{type_map[obj['type']]}/{obj['id']}",
                                    "operations": list(
                                        filter(
                                            lambda a: a is not None,
                                            [
                                                (
                                                    {
                                                        "operation": "setTags",
                                                        "data": {
                                                            k: v
                                                            for k, v in {
                                                                **obj.get("create", {}),
                                                                **obj.get("modify", {}),
                                                            }.items()
                                                        },
                                                    }
                                                    if len(obj.get("create", {}))
                                                    + len(obj.get("modify", {}))
                                                    >= 1
                                                    else None
                                                ),
                                                (
                                                    {
                                                        "operation": "unsetTags",
                                                        "data": [
                                                            k for k in obj["delete"]
                                                        ],
                                                    }
                                                    if "delete" in obj
                                                    else None
                                                ),
                                            ],
                                        )
                                    ),
                                },
                            }
                            for obj in properties["fixes"][0]
                        ],
                    }
                    if "fixes" in properties
                    and properties["fixes"] is not None
                    and len(properties["fixes"]) == 1
                    and properties["fixes"][0][0].get("id") is not None
                    else None
                ),
            }.items()
            if v is not None
        }
        for properties in issues
    ]
