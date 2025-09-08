from collections import defaultdict
from typing import Any, Dict, List, Literal, Optional, Tuple

from asyncpg import Connection
from fastapi import APIRouter, Depends

from modules.dependencies import database

router = APIRouter()


@router.get("/update.json", tags=["insight"])
async def updates(
    db: Connection = Depends(database.db),
) -> Dict[Literal["list"], List[Dict[str, Any]]]:
    sql = """
SELECT
    sources.id,
    updates_last.timestamp,
    sources.country,
    sources.analyser
FROM
    sources
    LEFT JOIN updates_last ON
        sources.id = updates_last.source_id
ORDER BY
    updates_last.timestamp DESC
"""
    return dict(list=await db.fetch(sql))  # type: ignore


@router.get("/update_matrix.json", tags=["insight"])
async def update_matrix(
    db: Connection = Depends(database.db),
    remote: Optional[str] = None,
    country: Optional[str] = None,
) -> Dict[str, Any]:
    sql = """
SELECT DISTINCT ON (sources.id)
    sources.id,
    EXTRACT(EPOCH FROM ((now())-updates_last.timestamp)) AS age,
    country,
    analyser
FROM
    sources
    JOIN updates_last ON
        sources.id = updates_last.source_id
WHERE
"""

    params: List[str] = []
    if remote:
        params.append(remote)
        sql += f"remote_ip = ${len(params)} AND"

    if country:
        params.append(country.replace("*", "%"))
        sql += "sources.country LIKE ${len(params)} AND"

    sql += """
    true
ORDER BY
    sources.id ASC,
    updates_last.timestamp DESC
"""

    keys_count: Dict[str, int] = defaultdict(int)
    matrix: Dict[str, Dict[str, Tuple[float, str]]] = defaultdict(dict)
    stats_analyser: Dict[str, Tuple[float, float, float]] = {}
    stats_country: Dict[str, Tuple[float, float, float, int]] = {}
    for res in await db.fetch(sql, *params):
        (source, age, country, analyser) = (res[0], res[1], res[2], res[3])
        if analyser and country:
            keys_count[country] += 1
            matrix[analyser][country] = (age / 60 / 60 / 24, source)
    for analyser in matrix:
        min: Optional[float] = None
        max: Optional[float] = None
        sum = 0.0
        for country in matrix[analyser]:
            v = matrix[analyser][country][0]
            min = v if not min or v < min else min
            max = v if not max or v > max else max
            sum += v
            if country not in stats_country:
                min_c = v
                sum_c = v
                max_c = v
                n_c = 1
            else:
                (min_c, sum_c, max_c, n_c) = stats_country[country]
                min_c = v if v < min_c else min_c
                max_c = v if v > max_c else max_c
                sum_c += v
                n_c += 1
            stats_country[country] = (min_c, sum_c, max_c, n_c)
        if min is not None and max is not None:
            stats_analyser[analyser] = (min, sum / len(matrix[analyser]), max)
    for country in stats_country:
        stats_country[country] = (
            stats_country[country][0],
            stats_country[country][1] / stats_country[country][3],
            stats_country[country][2],
            stats_country[country][3],
        )

    keys = sorted(keys_count, key=lambda k: -stats_country[k][2])
    matrix_keys = sorted(matrix.keys(), key=lambda k: -stats_analyser[k][2])

    return dict(
        keys=keys,
        matrix=matrix,
        matrix_keys=matrix_keys,
        stats_analyser=stats_analyser,
        stats_country=stats_country,
    )


@router.get("/update_summary.json", tags=["insight"])
async def update_summary(
    db: Connection = Depends(database.db),
) -> Dict[str, Any]:
    sql = """
SELECT
    backends.hostname AS hostname,
    updates_last.remote_ip AS remote,
    country,
    MAX(EXTRACT(EPOCH FROM ((now())-updates_last.timestamp))) AS max_age,
    MIN(EXTRACT(EPOCH FROM ((now())-updates_last.timestamp))) AS min_age,
    MAX(updates_last.version) AS max_version,
    MIN(updates_last.version) AS min_version,
    count(*) AS count
FROM
    sources
    JOIN updates_last ON
        sources.id = updates_last.source_id
    LEFT JOIN backends ON
        updates_last.remote_ip = backends.ip
GROUP BY
    hostname,
    remote_ip,
    country
ORDER BY
    min_age ASC
"""

    summary: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    hostnames: Dict[str, List[str]] = defaultdict(list)
    max_versions: Dict[str, List[str]] = defaultdict(list)
    min_versions: Dict[str, List[str]] = defaultdict(list)
    max_count = 0
    for res in await db.fetch(sql):
        (
            hostname,
            remote,
            country,
            max_age,
            min_age,
            max_version,
            min_version,
            count,
        ) = res
        max_count = max(max_count, count)
        summary[remote].append(
            {
                "hostname": hostname,
                "country": country,
                "max_age": max_age / 60 / 60 / 24,
                "min_age": min_age / 60 / 60 / 24,
                "count": count,
            }
        )
        hostnames[remote].append(hostname)
        if max_version:
            max_versions[remote].append(max_version)
        if min_version:
            min_versions[remote].append(min_version)

    remotes: Dict[str, str] = {}
    max_versions_max: Dict[str, Optional[str]] = {}
    max_versions_min: Dict[str, Optional[str]] = {}
    for remote in summary.keys():
        remotes[remote] = hostnames[remote][0]
        m = max(max_versions[remote]) if max_versions[remote] else None
        if m is not None and "-" in m:
            m = "-".join(m.split("-")[1:5])
        max_versions_max[remote] = m

        m = min(min_versions[remote]) if min_versions[remote] else None
        if m is not None and "-" in m:
            m = "-".join(m.split("-")[1:5])
        max_versions_min[remote] = m

    remote_keys = sorted(summary.keys(), key=lambda remote: remotes[remote] or "")
    return dict(
        summary=summary,
        hostnames=remotes,
        max_versions=max_versions_max,
        min_versions=max_versions_min,
        remote_keys=remote_keys,
        max_count=max_count,
    )


@router.get("/update_summary_by_analyser.json", tags=["insight"])
async def update_summary_by_analyser(
    db: Connection = Depends(database.db),
) -> Dict[str, Any]:
    sql = """
SELECT
    analyser,
    COUNT(*),
    MIN(EXTRACT(EPOCH FROM ((now())-updates_last.timestamp)))/60/60/24 AS min_age,
    MAX(EXTRACT(EPOCH FROM ((now())-updates_last.timestamp)))/60/60/24 AS max_age,
    MIN(updates_last.version) AS min_version,
    MAX(updates_last.version) AS max_version
FROM
    sources
    JOIN updates_last ON
        sources.id = updates_last.source_id
WHERE
    updates_last.version IS NOT NULL AND
    updates_last.version NOT IN ('(None)', '(unknown)')
GROUP BY
    analyser
ORDER BY
    analyser
"""

    summary: Dict[str, Dict[str, Any]] = {}
    max_versions = None
    for res in await db.fetch(sql):
        (analyser, count, min_age, max_age, min_version, max_version) = res
        max_versions = (
            max_version
            if max_versions is None or max_version > max_versions
            else max_versions
        )
        summary[analyser] = {
            "count": count,
            "min_age": min_age,
            "max_age": max_age,
            "max_version": "-".join((max_version or "").split("-")[1:5]),
            "min_version": "-".join((min_version or "").split("-")[1:5]),
        }

    max_versions = "-".join((max_versions or "").split("-")[1:5])

    return dict(summary=summary, max_versions=max_versions)


@router.get("/update/{source}.json", tags=["insight"])
async def update(
    source: int,
    db: Connection = Depends(database.db),
) -> Dict[Literal["list"], List[Dict[str, Any]]]:
    sql = """
SELECT
    source_id,
    timestamp,
    remote_url,
    remote_ip,
    version
FROM
    updates
WHERE
    source_id = $1
ORDER BY
    timestamp DESC
"""
    return dict(list=await db.fetch(sql, source))  # type: ignore
