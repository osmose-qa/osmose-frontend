import os
import pwd
import urllib.request
from collections import OrderedDict
from datetime import datetime
from io import StringIO
from typing import Dict, List, Literal, Optional

from . import OsmSax

################################################################################

languages_name: Dict[str, Dict[Literal["name", "direction"], str]] = OrderedDict()
languages_name["en"] = {"name": "English"}

# language names from http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
# _direction_rtl = ['fa', 'ar', 'he', 'ff', 'yi', 'ur', 'rgh', 'man', 'syc', 'mid', 'dv']
languages_name["ar"] = {"name": "اَلْعَرَبِيَّةُ", "direction": "rtl"}
languages_name["ca"] = {"name": "Català"}
languages_name["cs"] = {"name": "Čeština"}
languages_name["da"] = {"name": "Dansk"}
languages_name["de"] = {"name": "Deutsch"}
languages_name["el"] = {"name": "Ελληνικά"}
languages_name["es"] = {"name": "Español"}
languages_name["eu"] = {"name": "Euskara"}
languages_name["fa"] = {"name": "فارسی", "direction": "rtl"}
languages_name["fi"] = {"name": "Suomi"}
languages_name["fr"] = {"name": "Français"}
languages_name["gl"] = {"name": "Galego"}
languages_name["he"] = {"name": "עברית‎", "direction": "rtl"}
languages_name["hu"] = {"name": "Magyar"}
languages_name["it"] = {"name": "Italiano"}
languages_name["ja"] = {"name": "日本語"}
languages_name["ko"] = {"name": "한국어"}
languages_name["lt"] = {"name": "Lietuvių"}
languages_name["nb_NO"] = {"name": "Norsk bokmål"}
languages_name["nl"] = {"name": "Nederlands"}
languages_name["pl"] = {"name": "Polski"}
languages_name["pt"] = {"name": "Português"}
languages_name["pt_BR"] = {"name": "Português (Brasil)"}
languages_name["ro"] = {"name": "Română"}
languages_name["ru"] = {"name": "Русский"}
languages_name["sv"] = {"name": "Svenska"}
languages_name["uk"] = {"name": "Українська"}
languages_name["vi"] = {"name": "Tiếng Việt"}
languages_name["zh_CN"] = {"name": "中文 (简体)"}
languages_name["zh_TW"] = {"name": "中文 (繁體)"}


allowed_languages: List[str] = list(languages_name.keys())
pg_host = os.environ.get("DB_HOST", "")  # Use socket by default
pg_port = os.environ.get("DB_PORT", "5432")
pg_user = os.environ.get("DB_USER", "osmose")
pg_pass = os.environ.get("DB_PASS", "clostAdtoi")
pg_base = os.environ.get("DB_NAME", "osmose_frontend")
db_string = "host='%s' port='%s' dbname='%s' user='%s' password='%s'" % (
    pg_host,
    pg_port,
    pg_base,
    pg_user,
    pg_pass,
)
if pg_host:
    db_dsn = f"postgres://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_base}"
else:
    db_dsn = f"postgres://{pg_user}:{pg_pass}@/{pg_base}"
website = os.environ.get("URL_FRONTEND") or "https://osmose.openstreetmap.fr"

main_project = "OpenStreetMap"
main_website = "https://www.openstreetmap.org/"
remote_url = "https://www.openstreetmap.org/"
remote_url_read = "https://www.openstreetmap.org/"
remote_url_write = "https://www.openstreetmap.org/"

# main_project      = "OpenGeoFiction"
# main_website      = "http://opengeofiction.net/"
# remote_url        = "http://opengeofiction.net/"
# remote_url_read   = "http://opengeofiction.net/"
# remote_url_write  = "http://opengeofiction.net/"
# main_website      = "http://opengeofiction.net/"

username = pwd.getpwuid(os.getuid())[0]
dir_results = "/data/work/%s/results" % (username)


def show(s) -> None:
    print(s.encode("utf8"))


def str_to_datetime(s) -> datetime:
    patterns = ["%Y-%m-%d", "%Y-%m", "%Y"]
    for p in patterns:
        try:
            return datetime.strptime(s, p)
        except ValueError:
            pass

    raise ValueError


#
# Translation
#

LangsNegociation = Optional[List[str]]


def i10n_select(
    translations: Optional[Dict[str, str]], langs: LangsNegociation
) -> Optional[Dict[str, str]]:
    if not translations:
        return None
    elif langs is None:
        return translations
    else:
        for lang in langs:
            if lang in translations:
                return {"auto": translations[lang]}
        if "en" in translations:
            return {"auto": translations["en"]}
        else:
            return {"auto": list(translations.values())[0]}


def i10n_select_auto(
    translations: Optional[Dict[str, str]], langs: LangsNegociation
) -> Optional[str]:
    trans = i10n_select(translations, langs)
    return trans["auto"] if trans else None


def i10n_select_lang(langs: LangsNegociation) -> str:
    if langs:
        for lang in langs:
            if lang in languages_name:
                return lang
        for lang in langs:
            if lang.split("-")[0] in languages_name:
                return lang
    return "en"


#
# API
#


def fetch_osm_data(type: str, id: int, full=True) -> Optional[OsmSax.OsmSaxReader]:
    elem_url = os.path.join(remote_url_read + "api/0.6/", type, str(id))
    if type == "way" and full:
        elem_url = os.path.join(elem_url, "full")
    try:
        elem_io = StringIO(urllib.request.urlopen(elem_url).read().decode("utf-8"))
        osm_read = OsmSax.OsmSaxReader(elem_io)
        return osm_read
    except Exception:
        return None


def fetch_osm_elem(type: str, id: int) -> Optional[Dict[str, str]]:
    osmdw = OsmSax.OsmDictWriter()
    osm_read = fetch_osm_data(type, id, full=False)
    if osm_read:
        osm_read.CopyTo(osmdw)
        elem = osmdw.data[type]
        if len(elem) > 0:
            return elem[0]
    return None
