from collections import defaultdict
from typing import Any, Dict, List, Optional

try:
    # for python < 3.12
    from typing_extensions import TypedDict
except ImportError:
    from typing import TypedDict

from asyncpg import Connection

from .utils import LangsNegociation, i10n_select


class ItemMenu(TypedDict):
    item: int
    menu: Optional[Dict[str, str]]


async def _items_menu(db: Connection, langs: LangsNegociation) -> List[ItemMenu]:
    sql = """
    SELECT
        item,
        menu
    FROM
        items
    ORDER BY
        item
    """
    return list(
        map(
            lambda x: {"item": x["item"], "menu": i10n_select(x["menu"], langs)},
            await db.fetch(sql),
        )
    )


async def _countries(db: Connection) -> List[str]:
    sql = """
    SELECT DISTINCT
        country
    FROM
        sources
    ORDER BY
        country
    """
    return list(map(lambda x: x[0], await db.fetch(sql)))


async def _items(
    db: Connection,
    item: Optional[int] = None,
    classs: Optional[int] = None,
    langs: LangsNegociation = None,
) -> List[Dict[str, Any]]:
    sql_params = [item] if item is not None else []

    sql = (
        """
    SELECT
        id,
        menu AS title
    FROM
        categories
    WHERE
        1 = 1 """
        + (
            """AND id = CASE
            WHEN $1 < 1000 THEN 10
            ELSE ($1 / 1000)::int * 10
         END"""
            if item is not None
            else ""
        )
        + """
    ORDER BY
        id
    """
    )
    categs = await db.fetch(sql, *sql_params)

    sql = (
        """
    SELECT
        item,
        categorie_id,
        marker_color AS color,
        marker_flag AS flag,
        menu AS title,
        levels,
        number,
        tags
    FROM
        items
    WHERE
        1 = 1 """
        + ("AND item = $1" if item is not None else "")
        + """
    ORDER BY
        item
    """
    )
    items = await db.fetch(sql, *sql_params)
    items = list(
        map(
            lambda r: dict(  # type: ignore
                r,
                title=i10n_select(r["title"], langs),
                levels=r["number"]
                and list(
                    map(
                        lambda l_n: {"level": l_n[0], "count": l_n[1]},
                        zip(r["levels"], r["number"]),
                    )
                )
                or list(map(lambda i: {"level": i, "count": 0}, [1, 2, 3])),
            ),
            items,
        )
    )
    items_categ = defaultdict(list)
    for i in items:
        items_categ[i["categorie_id"]].append(i)

    sql = """
    SELECT
        item,
        class,
        title,
        level,
        tags,
        detail,
        fix,
        trap,
        example,
        source,
        resource
    FROM
        class
    WHERE
        1 = 1 """
    params = 0
    if item is not None:
        params += 1
        sql += f"AND item = ${params} "
    if classs is not None:
        params += 1
        sql += f"AND class = ${params}"
        sql_params.append(classs)
    sql += """
    ORDER BY
        item,
        class
    """
    classses = await db.fetch(sql, *sql_params)
    classses = list(
        map(
            lambda c: dict(  # type: ignore
                dict(c),
                title=i10n_select(c["title"], langs),
                detail=i10n_select(c["detail"], langs),
                fix=i10n_select(c["fix"], langs),
                trap=i10n_select(c["trap"], langs),
                example=i10n_select(c["example"], langs),
            ),
            classses,
        )
    )
    class_item = defaultdict(list)
    for c in classses:
        class_item[c["item"]].append(c)

    return list(
        map(
            lambda categ: dict(
                categ,
                items=list(
                    map(
                        lambda item: dict(item, **{"class": class_item[item["item"]]}),
                        items_categ[categ["id"]],
                    )
                ),
            ),
            map(
                lambda categ: {
                    "id": categ["id"],
                    "title": i10n_select(categ["title"], langs),
                },
                categs,
            ),
        )
    )


async def _tags(db: Connection) -> List[str]:
    sql = """
    SELECT DISTINCT
        tag
    FROM
        (
        SELECT
            unnest(tags) AS tag
        FROM
            class
        ) AS t
    WHERE
        tag != ''
    ORDER BY
        tag
    """
    return list(map(lambda x: x[0], await db.fetch(sql)))


async def _sources(db: Connection) -> Dict[int, Dict[str, Any]]:
    config: Dict[int, Dict[str, Any]] = {}
    for res in await db.fetch(
        "SELECT id, password, country, analyser FROM sources JOIN sources_password ON sources.id = source_id"
    ):
        src: Dict[str, Any] = {}
        src["id"] = str(res["id"])
        src["password"] = set([res["password"]])
        src["country"] = res["country"]
        src["analyser"] = res["analyser"]
        src["comment"] = res["analyser"] + "-" + res["country"]
        if (
            src["id"] in config
            and config[src["id"]]["country"] == src["country"]
            and config[src["id"]]["analyser"] == src["analyser"]
        ):
            config[src["id"]]["password"].update(src["password"])
        else:
            config[src["id"]] = src
    return config
