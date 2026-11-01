import json
import os
import pathlib
import secrets
from typing import Any, Dict, Generic, Optional, TypeVar, Union
from uuid import UUID

from fastapi import HTTPException, Request
from fastapi_sessions.backends.session_backend import (  # type: ignore
    BackendError,
    SessionBackend,
)
from fastapi_sessions.frontends.implementations import (  # type: ignore
    CookieParameters,
    SessionCookie,
)
from fastapi_sessions.frontends.session_frontend import FrontendError  # type: ignore
from fastapi_sessions.session_verifier import SessionVerifier  # type: ignore
from itsdangerous import BadSignature, SignatureExpired
from pydantic import BaseModel


# Session cookie signing key. Production sets COOKIE_SIGN_KEY (see
# docker/.env.template and docker-compose.yml); without it, a random
# per-process key is used, so no repo-readable key ever signs cookies.
SESSION_SIGN_KEY = os.getenv("COOKIE_SIGN_KEY") or secrets.token_hex(32)


class SessionData(BaseModel):
    oauth2_token: Optional[str] = None
    user: Optional[Dict[str, Any]] = None
    changeset: Optional[Any] = None


class EternalCookieParameters(CookieParameters):
    max_age: Optional[int] = None
    expires: Optional[int] = 2147483647  # 03:14:07 UTC on 19 January 2038


class OptionalSessionCookie(SessionCookie):
    def __call__(self, request: Request) -> Union[UUID, FrontendError]:
        # Get the signed session id from the session cookie

        signed_session_id = request.cookies.get(self.model.name)

        if not signed_session_id:
            return None
            # if self.auto_error:
            #     raise HTTPException(status_code=403, detail="No session provided")

            # error = FrontendError("No session cookie attached to request")
            # super().attach_id_state(request, error)
            # return error

        # Verify and timestamp the signed session id
        try:
            session_id = UUID(
                self.signer.loads(
                    signed_session_id,
                    max_age=self.cookie_params.max_age,
                    return_timestamp=False,
                )
            )
        except (SignatureExpired, BadSignature):
            if self.auto_error:
                raise HTTPException(status_code=401, detail="Invalid session provided")
            error = FrontendError("Session cookie has invalid signature")
            super().attach_id_state(request, error)
            return error

        super().attach_id_state(request, session_id)
        return session_id


cookie = OptionalSessionCookie(
    cookie_name="cookie",
    identifier="general_verifier",
    auto_error=True,
    secret_key=SESSION_SIGN_KEY,
    # cookie_params=CookieParameters(),
    cookie_params=EternalCookieParameters(),
)

ID = TypeVar("ID")
SessionModel = TypeVar("SessionModel", bound=BaseModel)


class InFileBackend(Generic[ID, SessionModel], SessionBackend[ID, SessionModel]):
    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir
        pathlib.Path(data_dir).mkdir(parents=True, exist_ok=True)

    async def create(self, session_id: ID, data: SessionModel) -> None:
        with open(f"{self.data_dir}/#{session_id}", "w") as f:
            f.write(data.json())

    async def read(self, session_id: ID) -> Optional[SessionModel]:
        path = f"{self.data_dir}/#{session_id}"
        if pathlib.Path(path).exists():
            with open(path, "r") as f:
                data = json.loads(f.read())
                return self.__orig_class__.__args__[1](**data)  # SessionModel(**data)
        return None

    async def update(self, session_id: ID, data: SessionModel) -> None:
        await self.create(session_id, data)

    async def delete(self, session_id: ID) -> None:
        pathlib.Path(f"{self.data_dir}/#{session_id}").unlink(missing_ok=True)


backend = InFileBackend[UUID, SessionData]("./web_api/session/")


class BasicVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InFileBackend[UUID, SessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def backend(self) -> InFileBackend[UUID, SessionData]:
        return self._backend

    @property
    def auto_error(self) -> bool:
        return self._auto_error

    @property
    def auth_http_exception(self) -> HTTPException:
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        return True

    # Overwrite method to make session optional
    async def __call__(self, request: Request) -> Optional[SessionData]:
        if not hasattr(request.state, "session_ids"):
            return None

        try:
            session_id: Union[UUID, FrontendError] = request.state.session_ids[
                self.identifier
            ]
        except Exception:
            if self.auto_error:
                raise HTTPException(
                    status_code=500, detail="internal failure of session verification"
                )
            else:
                return BackendError(
                    "failed to extract the {} session from state", self.identifier
                )

        if isinstance(session_id, FrontendError):
            if self.auto_error:
                raise self.auth_http_exception
            return None

        session_data = await self.backend.read(session_id)
        # if not session_data or not self.verify_session(session_data):
        #     if self.auto_error:
        #         raise self.auth_http_exception
        #     return

        return session_data


verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)
