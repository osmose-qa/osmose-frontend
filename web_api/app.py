import os
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

import requests
from authlib.integrations.starlette_client import OAuth  # type: ignore
from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

from modules import utils
from modules.dependencies import database, langs
from modules.utils import LangsNegociation

from . import byuser, editor, false_positive, issue, issues, map
from .tool.session import SESSION_SIGN_KEY, SessionData, backend, cookie, verifier

openapi_tags = [
    {
        "name": "Private API",
        "description": "Private API. For external use refer to public API.",
    },
]

app = FastAPI(openapi_tags=openapi_tags)


def custom_openapi() -> Dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Osmose-QA API",
        version="0.3",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore

app.add_middleware(SessionMiddleware, secret_key=SESSION_SIGN_KEY)

oauth = OAuth(
    Config(
        environ={
            "OSM_CLIENT_ID": os.getenv("OSM_CLIENT_ID", ""),
            "OSM_CLIENT_SECRET": os.getenv("OSM_CLIENT_SECRET", ""),
        }
    )
)
oauth.register(
    name="osm",
    server_metadata_url="https://www.openstreetmap.org/.well-known/oauth-authorization-server",
    client_kwargs={"scope": "read_prefs write_api write_notes"},
)


@app.get("/login")
async def login(
    request: Request,
    session_id: Optional[UUID] = Depends(cookie),
    langs: LangsNegociation = Depends(langs.langs),
) -> RedirectResponse:
    if session_id:
        await backend.delete(session_id)

    session = uuid4()
    await backend.create(session, SessionData())

    redirect_uri = utils.website + "/en/oauth2"
    response = await oauth.osm.authorize_redirect(request, redirect_uri)
    cookie.attach_to_response(response, session)
    return response


@app.get("/logout")
async def logout(
    response: Response, session_id: Optional[UUID] = Depends(cookie)
) -> RedirectResponse:
    if session_id:
        await backend.delete(session_id)
        cookie.delete_from_response(response)
    return RedirectResponse("map/")


@app.get("/oauth2")
async def oauth2(
    request: Request,
    session_id: UUID = Depends(cookie),
    session_data: Optional[SessionData] = Depends(verifier),
) -> RedirectResponse:
    if session_id and session_data:
        try:
            oauth2_token = await oauth.osm.authorize_access_token(request)
            session_data.oauth2_token = oauth2_token["access_token"]

            user_request = requests.get(
                utils.remote_url + "api/0.6/user/details.json",
                headers={"Authorization": f"Bearer {session_data.oauth2_token}"},
            )
            if user_request and user_request.status_code == 200:
                session_data.user = user_request.json()
            await backend.update(session_id, session_data)
        except Exception:
            pass
    return RedirectResponse("map/")


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

app.include_router(byuser.router)
app.include_router(editor.router)
app.include_router(false_positive.router)
app.include_router(issue.router)
app.include_router(issues.router)
app.include_router(map.router)


@app.get("/", tags=["vue"])
@app.get("/contact", tags=["vue"])
@app.get("/copyright", tags=["vue"])
@app.get("/translation", tags=["vue"])
@app.get("/map/", tags=["vue"])
@app.get("/issue/{uuid}", tags=["vue"])
@app.get("/false-positive/{uuid}", tags=["vue"])
@app.get("/issues/open", tags=["vue"])
@app.get("/issues/done", tags=["vue"])
@app.get("/issues/false-positive", tags=["vue"])
@app.get("/issues/matrix", tags=["vue"])
@app.get("/byuser/", tags=["vue"])
@app.get("/byuser/{username}", tags=["vue"])
@app.get("/control/update/{source}", tags=["vue"])
@app.get("/control/update_matrix", tags=["vue"])
@app.get("/control/update_summary", tags=["vue"])
@app.get("/control/update_summary_by_analyser", tags=["vue"])
def vue(
    uuid: Optional[UUID] = None,
    username: Optional[str] = None,
    source: Optional[str] = None,
) -> HTMLResponse:
    return HTMLResponse(content=open("web/public/assets/index.html").read())
