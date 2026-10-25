import gettext
from typing import Callable, Dict, List, Tuple

from fastapi import Depends, Request

from modules.dependencies import langs
from modules.utils import LangsNegociation, allowed_languages

domain = "osmose-frontend"
localedir = "web/po/mo"


Translator = Callable[..., str]


def get_languages(request: Request) -> Tuple[List[str], bool]:
    base_path = request.scope.get("root_path")
    if base_path and len(base_path) >= 3:
        # Handle longer languages like zh_TW
        if len(base_path) == 6 and base_path[3] == "_":
            tmp_lang = base_path[1:6]
            if tmp_lang in allowed_languages:
                return ([tmp_lang, allowed_languages[0]], False)

        if len(base_path) == 3:
            tmp_lang = base_path[1:3]
            if tmp_lang in allowed_languages:
                return ([tmp_lang, allowed_languages[0]], False)

    langs: List[str] = []
    accept_language = request.headers.get("Accept-Language")
    if accept_language:
        langs = accept_language.split(",")
        langs = [x.split(";")[0] for x in langs]
        langs = [x.split("-")[0] for x in langs]
        langs = [x for x in langs if x in allowed_languages]

    if langs:
        langs.append(allowed_languages[0])
        res = []
        for lang in langs:
            if lang not in res:
                res.append(lang)
        return (res, True)
    else:
        return (allowed_languages, True)


cache: Dict[str, Translator] = {}


async def i18n(
    request: Request,
    langs: LangsNegociation = Depends(langs.langs),
) -> Translator:
    languages, redirect = get_languages(request)

    k = ",".join(languages)
    if k in cache:
        gt = cache[k]
    else:
        gt = gettext.translation(
            domain, localedir=localedir, languages=languages
        ).gettext
        cache[k] = gt

    return gt
