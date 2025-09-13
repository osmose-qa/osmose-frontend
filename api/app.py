import os

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from modules.dependencies import database

from . import false_positive, issue, issues, issues_tiles, meta_0_3, user

openapi_tags = [
    {
        "name": "0.2",
        "description": "The 0.2 part of the API is deprecated.",
    },
]

app = FastAPI(openapi_tags=openapi_tags)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Osmose-QA API",
        version="0.3",
        description="""
Generally the API returns JSON.

# Common parameters
Most of the endpoints have a common set query parameters.
But not all parameter have effect on every endpoints.

| Param | Type | Default | Comment |
|-------|------|---------|---------|
| lat | float | | \
    Latitude. |
| lon | float | | \
    Longitude. |
| bbox | lon1,lat1,lon2,lat2 | | \
    Restriction area. |
| item | 1000,1010,1020,2xxx | All | \
    Returned items list, a number followed by "xxx" for complete category. \
    See the list at http://osmose.openstreetmap.fr/api/0.3/items |
| source | integer | | \
    Number of the source, see the source list at http://osmose.openstreetmap.fr/fr/control/update |
| class | integer | | \
    Classes of item, one or many classes separated with commas, a class is a sub part of an item. \
    Make sense only with a unique item. |
| username | | | \
    OSM username, returns issues for objects when user is the last editor. |
| level | list of 1, 2 or 3 | 1,2,3 | \
    Level of issues. List of number 1, 2 and/or 3 in this order. |
| zoom | integer | 10 | \
    Zoom level. |
| limit | integer | 100 | \
    Returned issues, 500 max. |
| country | | | \
    Issues for an area. The wildcard "*" is allowed as part of the parameter, eg "france*" for all regions at once. \
    See the list at http://osmose.openstreetmap.fr/api/0.3/countries |
| useDevItem | true, false, all | false | \
    Returns issues only for items that are not active, not active are dev or buggy items. |
| status | open, done, false | open | \
    Issues status, "open", "done" for issues reported as corrected and "false" for issues reported as false positive. |
| start_date | date | | \
    Issues generated after this date. For statistics begins on this date. Date format "Y[-m[-d]]". |
| end_date | date | | \
    Issues generated before this date. For statistics ended on this date. Date format "Y[-m[-d]]". |
| tags | t1,t2,t3 | | \
    Filter issues on that tags list via their items. \
    Tags are topic of analysis, not OSM tags. \
    The list of tags http://osmose.openstreetmap.fr/api/0.3/tags |
| fixables | online or josm | | \
    Returns issues with proposed correction usable with the Osmose online editor or with JOSM. |

# Translations
Translation are returned according to the `Accept-Language` HTTP header.
The automatic translated content is on a `auto` field in the JSON object: `{"auto": "foo bar"}`.
""",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore


# CORS middleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
)


@app.on_event("startup")
async def startup() -> None:
    await database.startup()


# Add routes

app.include_router(meta_0_3.router)
app.include_router(user.router)
app.include_router(issue.router)
app.include_router(issues.router)
app.include_router(issues_tiles.router)
app.include_router(false_positive.router)


@app.get("/0.3/assets/sprites.css")
def sprites_css():
    file_path = "api/assets/sprites.css"
    if os.path.isfile(file_path):
        return Response(open(file_path, "rb").read())
    else:
        raise HTTPException(status_code=404)


@app.get("/0.3/assets/sprite.png")
def sprite_png():
    return Response(open("api/assets/sprite.png", "rb").read())


@app.get("/0.3/assets/marker-gl-sprite.json")
def marker_gl_sprite_json():
    return Response(open("api/assets/marker-gl-sprite.json", "rb").read())


@app.get("/0.3/assets/marker-gl-sprite.png")
def marker_gl_sprite_png():
    return Response(open("api/assets/marker-gl-sprite.png", "rb").read())


@app.get("/0.3/assets/markers/{filename:path}.png")
def marker(filename):
    file_path = f"api/markers/{filename}.png"
    if not os.path.isfile(file_path):
        file_path = "api/markers/marker-b-0.png"
    return Response(open(file_path, "rb").read())
