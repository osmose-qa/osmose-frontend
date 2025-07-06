import csv as csv_lib
import io
from typing import Tuple

from lxml import etree
from lxml.builder import E, ElementMaker  # type: ignore
from lxml.html import builder as H

from modules.dependencies import i18n
from modules.dependencies.commons_params import Params


def xml_header(
    params: Params, title: str, website: str, lang: str, query, _
) -> Tuple[str, str, str]:
    if params.users:
        users = ", ".join(params.users)
        title = f"Osmose - {users}"
        description = _("Statistics for user {}").format(users)
        url = f"{website}/{lang}/byuser/{users}"
    else:
        title = "Osmose - " + title
        description = None
        url = f"{website}/{lang}/issues/open?{query}"
    return title, description, url


def xml_issue(
    res,
    website: str,
    lang: str,
    query: str,
    main_website: str,
    remote_url_read: str,
    _: i18n.Translator,
) -> Tuple[float, float, str, str, str, str]:
    name = (res["menu"] or "") + " - " + (res["subtitle"] or res["title"] or "")

    lat = res["lat"]
    lon = res["lon"]

    if res["elems"]:
        for e in res["elems"]:
            if e["type"] == "R":
                # fmt: off
                e["object_josm_url"] = (
                    f"http://localhost:8111/import?url={remote_url_read}api/0.6/relation/{e['id']}/full"
                )
                # fmt: on
            else:
                # fmt: off
                e["object_josm_url"] = (
                    f"http://localhost:8111/load_object?objects={e['type'].lower()}{e['id']}"
                )
                # fmt: on

    map_url = (
        f"{website}/{lang}/map/"
        + f"#{query}&zoom=16&lat={lat}&lon={lon}&level={res['level']}&tags=&fixable=&issue_uuid={res['uuid']}"
    )

    issue_summary_string = f"{res['item']}({res['level']})/{res['class']} {res['uuid']}"

    html_desc = H.DIV(H.P(issue_summary_string))
    plain_desc = issue_summary_string

    if res["elems"]:
        for e in res["elems"]:
            html_desc.append(
                H.P(
                    H.A(
                        f"{e['type_long']} {e['id']}",
                        href=f"{main_website}{e['type_long']}/{e['id']}",
                    ),
                    " ",
                    H.A("Osmose", href=map_url),
                    " ",
                    H.A("JOSM", href=e["object_josm_url"]),
                    " ",
                    H.A(
                        "iD",
                        href=f"{main_website}edit?editor=id&{e['type_long']}={e['id']}",
                    ),
                    H.BR(),
                    H.A(
                        _("Mark issue as fixed"),
                        href=f"{website}/api/0.3/issue/{res['uuid']}/done",
                    ),
                    " ",
                    H.A(
                        _("Mark issue as false positive"),
                        href=f"{website}/api/0.3/issue/{res['uuid']}/false",
                    ),
                )
            )
            plain_desc += f"\nOsmose: {map_url}"
            if "tags" in e:
                html_desc.append(H.P(_("Tags:")))
                tags_ul = H.UL()
                plain_desc += "\nTags:"
                for k, v in e["tags"].items():
                    tags_ul.append(H.LI(f"{k}={v}"))
                    plain_desc += f"\n- {k}={v}"
                html_desc.append(tags_ul)
    else:
        fallback_url = "http://localhost:8111/load_and_zoom?left={}&bottom={}&right={}&top={}".format(
            float(lon) - 0.002,
            float(lat) - 0.002,
            float(lon) + 0.002,
            float(lat) + 0.002,
        )
        html_desc.append(H.A("Osmose", href=fallback_url))
        plain_desc += f"\n{fallback_url}"
    issue_reported_at = "{} {}".format(
        _("Issue reported on:"), res["timestamp"].strftime("%Y-%m-%d")
    )
    html_desc.append(H.P(issue_reported_at))
    plain_desc += f"\n{issue_reported_at}"

    return (
        lat,
        lon,
        name,
        plain_desc,
        map_url,
        etree.tostring(html_desc, encoding="unicode", xml_declaration=False),
    )


def gpx_issue(
    res,
    website: str,
    lang: str,
    query,
    main_website: str,
    remote_url_read: str,
    i18n: i18n.Translator,
):
    lat, lon, name, _, map_url, html_desc = xml_issue(
        res, website, lang, query, main_website, remote_url_read, i18n
    )
    return E.wpt(
        E.name(name),
        E.desc(html_desc),
        E.url(map_url),
        lat=str(lat),
        lon=str(lon),
    )


def gpx(
    website: str,
    lang: str,
    params: Params,
    query: str,
    main_website: str,
    remote_url_read: str,
    issues,
    title: str,
    i18n: i18n.Translator,
):
    content = []
    if len(issues) > 0:
        content.append(E.time(issues[0]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ")))
    content += list(
        map(
            lambda issue: gpx_issue(
                issue, website, lang, query, main_website, remote_url_read, i18n
            ),
            issues,
        )
    )

    title, _, url = xml_header(params, title, website, lang, query, i18n)
    return E.gpx(
        E.name(title),
        E.url(url),
        *content,
        version="1.0",
        creator="http://osmose.openstreetmap.fr",
        xmlns="http://www.topografix.com/GPX/1/0",
        # xmlns:xsi = 'http://www.w3.org/2001/XMLSchema-instance',
        # xsi:schemaLocation = 'http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd',
    )


def kml_issue(
    res,
    website: str,
    lang,
    query,
    main_website: str,
    remote_url_read: str,
    i18n: i18n.Translator,
):
    lat, lon, name, desc, map_url, _ = xml_issue(
        res, website, lang, query, main_website, remote_url_read, i18n
    )
    return E.Placemark(
        E.name(name),
        ElementMaker(namespace="http://www.w3.org/2005/Atom").link(href=map_url),
        E.description(desc),
        E.styleUrl("#placemark-purple"),
        E.Point(
            E.coordinates(f"{lon},{lat}"),
        ),
    )


def kml(
    website: str,
    lang: str,
    params: Params,
    query: str,
    main_website: str,
    remote_url_read: str,
    issues,
    title: str,
    i18n: i18n.Translator,
):
    content = map(
        lambda issue: kml_issue(
            issue, website, lang, query, main_website, remote_url_read, i18n
        ),
        issues,
    )

    title, _, url = xml_header(params, title, website, lang, query, i18n)
    if len(issues) > 0:
        title += " (" + issues[0]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ") + ")"
    return ElementMaker(
        nsmap={
            "atom": "http://www.w3.org/2005/Atom",
        }
    ).kml(
        E.Document(
            E.name(title),
            E.Style(
                E.IconStyle(
                    E.Icon(
                        E.href(
                            "https://osmose.openstreetmap.fr/images/markers/marker-b-1070.png"
                        )
                    ),
                ),
                id="placemark-purple",
            ),
            ElementMaker(namespace="http://www.w3.org/2005/Atom").link(href=url),
            *content,
        ),
        xmlns="http://www.opengis.net/kml/2.2",
    )


def rss_issue(
    res,
    website: str,
    lang: str,
    query: str,
    main_website: str,
    remote_url_read: str,
    i18n: i18n.Translator,
):
    _, _, name, _, map_url, html_desc = xml_issue(
        res, website, lang, query, main_website, remote_url_read, i18n
    )
    return E.item(
        E.title(name),
        E.description(html_desc),
        E.category(str(res["item"])),
        E.link(map_url),
        E.guid(str(res["uuid"]), isPermaLink="false"),
    )


def rss(
    website: str,
    lang: str,
    params: Params,
    query: str,
    main_website: str,
    remote_url_read: str,
    issues,
    title: str,
    i18n: i18n.Translator,
):
    content = map(
        lambda issue: rss_issue(
            issue, website, lang, query, main_website, remote_url_read, i18n
        ),
        issues,
    )

    lastBuildDate = []
    if len(issues) > 0:
        time = issues[0]["timestamp"]
        ctime = time.ctime()
        rfc822 = "{0}, {1:02d} {2}".format(
            ctime[0:3], time.day, ctime[4:7]
        ) + time.strftime(" %Y %H:%M:%S %z")
        lastBuildDate = [E.lastBuildDate(rfc822)]

    title, description, url = xml_header(params, title, website, lang, query, i18n)
    E_atom = ElementMaker(
        namespace="http://www.w3.org/2005/Atom",
        nsmap={"atom": "http://www.w3.org/2005/Atom"},
    )
    return E.rss(
        E.channel(
            E_atom.link(
                href=f"{website}/api/0.3/issues.rss?{query}",
                rel="self",
                type="application/rss+xml",
            ),
            E.title(title),
            E.description(description or query),
            *lastBuildDate,
            E.link(url),
            *content,
        ),
        version="2.0",
    )


def csv(
    website: str,
    lang: str,
    params: Params,
    query: str,
    main_website: str,
    remote_url_read: str,
    issues,
    title: str,
) -> str:
    output = io.StringIO()
    writer = csv_lib.writer(output)
    h = [
        "uuid",
        "source",
        "item",
        "class",
        "level",
        "title",
        "subtitle",
        "country",
        "analyser",
        "timestamp",
        "username",
        "lat",
        "lon",
        "elems",
    ]
    hh = {"source": "source_id"}
    writer.writerow(h)
    for res in issues:
        usernames = list(map(lambda elem: elem.get("username", ""), res["elems"] or []))
        elems = "_".join(
            map(
                lambda elem: {"N": "node", "W": "way", "R": "relation"}[elem["type"]]
                + str(elem["id"]),
                res["elems"] or [],
            )
        )
        writer.writerow(
            list(
                map(
                    lambda a: (
                        usernames
                        if a == "username"
                        else (elems if a == "elems" else res[a])
                    ),
                    map(lambda y: hh.get(y, y), h),
                )
            )
        )
    return output.getvalue()
