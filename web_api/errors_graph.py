import csv
import io
import json
from datetime import datetime
from typing import List, Tuple, Union

import matplotlib  # type: ignore
import matplotlib.dates  # type: ignore
import matplotlib.pyplot  # type: ignore
from asyncpg import Connection

from modules import query
from modules.dependencies.commons_params import Params


async def get_data(
    db: Connection,
    params: Params,
) -> List[Tuple[datetime, int]]:
    sqlbase = """
SELECT
    date,
    SUM(count)
FROM (
    SELECT
        date_trunc('day', timestamp) AS date,
        AVG(count) AS count
    FROM (
        SELECT
            markers.source_id,
            markers.class,
            markers.count,
            generate_series(
                lower(timestamp_range),
                coalesce(upper(timestamp_range) - '23 hour'::interval, now()),
                '1 day'::interval
            )::timestamp without time zone AS timestamp
        FROM
            %s
        WHERE
            %s
        ) AS t
    WHERE
        %s
    GROUP BY
        source_id,
        class,
        date_trunc('day', timestamp)
    ) AS t
GROUP BY
    date
ORDER BY
    date
"""

    join, where, sql_params = query._build_param(
        bbox=None,
        users=None,
        status=None,
        fixable=None,
        sources=params.source,
        item=params.item,
        level=params.level,
        classs=params.classs,
        country=params.country,
        useDevItem=params.useDevItem,
        tags=params.tags,
        stats=True,
        start_date=params.start_date,
        end_date=params.end_date,
    )
    where2 = ["1 = 1"]
    if params.start_date:
        sql_params.append(params.start_date)
        where2.append(f"timestamp >= ${len(sql_params)}")
    if params.end_date:
        sql_params.append(params.end_date)
        where2.append(f"timestamp < ${len(sql_params)}")
    sql = sqlbase % (join, where, " AND ".join(where2))

    result = []
    for r in await db.fetch(sql, *sql_params):
        result.append((r[0], r[1]))
    return result


async def get_text(
    db: Connection,
    params: Params,
) -> str:
    if (
        params.source
        and len(params.source) == 1
        and params.classs
        and len(params.classs) == 1
    ):
        return await db.fetchval(
            """
SELECT
    title->'en'
FROM
    markers_counts
    JOIN class ON
        class.item = markers_counts.item AND
        class.class = markers_counts.class
WHERE
    markers_counts.source_id=$1 AND
    class.class=$2
""",
            params.source[0][0],
            params.classs[0],
        )
    elif (
        params.item
        and len(params.item) == 1
        and params.classs
        and len(params.classs) == 1
    ):
        return await db.fetchval(
            """
SELECT
    title->'en'
FROM
    class
WHERE
    class=$1 AND
    item=$2
LIMIT 1
""",
            params.classs[0],
            int(params.item[0]),
        )
    elif params.item and len(params.item) == 1:
        return await db.fetchval(
            """
SELECT
    menu->'en'
FROM
    items
WHERE
    item=$1
LIMIT 1
""",
            int(params.item[0]),
        )
    else:
        return ""


async def get_src(db: Connection, params: Params) -> str:
    ret = []
    if params.item:
        r = await db.fetchval(
            "SELECT menu->'en' FROM items WHERE {0}".format(
                query._build_where_item("items", params.item)
            )
        )
        if r:
            ret.append(r)

    if params.item and params.classs:
        r = await db.fetchval(
            "SELECT title->'en' FROM class WHERE {0} AND {1};".format(
                query._build_where_item("class", params.item),
                query._build_where_class("class", params.classs),
            )
        )
        if r:
            ret.append(r)

    if params.source and len(params.source) == 1:
        r = await db.fetchrow(
            "SELECT country, analyser FROM sources WHERE id = $1;", params.source[0][0]
        )
        if r:
            ret.append(r[0])
            ret.append(r[1])

    if params.country:
        ret.append(str(params.country))

    return " - ".join(ret) if ret else "All"


def convIntsToStr(values: List[int]) -> str:
    """
    Convert integer list to string
    """
    return ", ".join([str(elt) for elt in values])


async def make_plt(db: Connection, params: Params, format: str) -> Union[str, bytes]:
    data = await get_data(db, params)
    text = await get_text(db, params)
    src = await get_src(db, params)
    return plot(data, text + " " + src, format)


def plot(data, title: str, format: str) -> Union[str, bytes]:
    if format == "json":
        jsonData = {}
        for d in data:
            jsonData[d[0].strftime("%Y-%m-%dT%H:%M:%SZ")] = int(d[1])

        return json.dumps({"title": title, "data": jsonData})
    elif format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        h = ["timestamp", "value"]
        writer.writerow(h)
        for d in data:
            writer.writerow([d[0].strftime("%Y-%m-%dT%H:%M:%SZ"), int(d[1])])
        return output.getvalue()
    else:
        dates = [q[0] for q in data]
        opens = [q[1] for q in data]
        fig = matplotlib.pyplot.figure()
        ax = fig.add_subplot(111)
        ax.plot(dates, opens, "-", color="r")
        ax.set_title(title)
        # format the ticks
        ax.relim()
        if len(opens) > 1:
            ytop = float(max(opens)) * 1.05 + 1
        else:
            ytop = None
        ax.set_ylim(bottom=0, top=ytop)
        ax.autoscale_view()
        # format the coords message box
        ax.fmt_ydata = lambda x: "$%1.2f" % x
        ax.grid(True)

        locator = matplotlib.dates.AutoDateLocator()
        formatter = matplotlib.dates.AutoDateFormatter(locator)
        formatter.scaled[30.0] = "%Y-%m"
        formatter.scaled[1.0] = "%Y-%m-%d"
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)

        fig.autofmt_xdate()

        buf = io.BytesIO()
        fig.savefig(buf, format=format)
        matplotlib.pyplot.close(fig)
        return buf.getvalue()
