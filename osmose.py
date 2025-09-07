import os

from fastapi import Depends, FastAPI, HTTPException, Request, Response, responses

from api import app as api
from control import app as control
from modules import utils
from modules.dependencies import langs
from modules.utils import LangsNegociation
from web_api import app as web_api

app = FastAPI()


@app.on_event("startup")
async def startup():
    # Manual Event propagation
    await api.startup()


#
# API
#
app.mount("/api", api.app)
app.mount("/control/", control.app)

#
# Web
#
for lang in utils.allowed_languages:
    app.mount("/" + lang, web_api.app)


@app.get("/")
@app.get("/map")
@app.get("/map/")
def index(request: Request, langs: LangsNegociation = Depends(langs.langs)):
    lang = langs[0][0:2] if langs else "en"
    path = f"/{lang}"
    if request.url.path != "/":
        path += request.url.path
    if request.url.query:
        path += f"?{request.url.query}"
    return responses.RedirectResponse(url=path)


@app.get("/assets/sprites.css")
def sprites_css():
    file_path = "web_api/public/assets/sprites.css"
    if os.path.isfile(file_path):
        return Response(open(file_path, "rb").read())
    else:
        raise HTTPException(status_code=404)


@app.get("/assets/sprite.png")
def sprite_png():
    return Response(open("web_api/public/assets/sprite.png", "rb").read())


@app.get("/assets/marker-gl-sprite.json")
def sprite_png():
    return Response(open("web_api/public/assets/marker-gl-sprite.json", "rb").read())


@app.get("/assets/marker-gl-sprite.png")
def sprite_png():
    return Response(open("web_api/public/assets/marker-gl-sprite.png", "rb").read())


@app.get("/images/markers/{filename:path}.png")
def marker(filename):
    file_path = f"web_api/static/images/markers/{filename}.png"
    if not os.path.isfile(file_path):
        file_path = "web_api/static/images/markers/marker-b-0.png"
    return Response(open(file_path, "rb").read())


@app.get("/{path_name:path}")
async def catch_all(path_name: str):
    file_path = f"web/public/{path_name}"
    if os.path.isfile(file_path):
        return Response(open(file_path, "rb").read())
    else:
        raise HTTPException(status_code=404)
