# https://raw.githubusercontent.com/JOSM/tag2link/master/index.json

import json
from typing import Dict, List


class tag2link:
    def __init__(self, rulesFiles: str):
        rules_json = json.load(open(rulesFiles, "r", encoding="utf-8"))
        self.rules: Dict[str, str] = {}
        for rule in rules_json:
            key = rule["key"]
            if not key.startswith("Key:"):
                continue
            key = key[4:]

            if key in self.rules:
                continue

            self.rules[key] = rule["url"]

    def addLinks(self, tags: Dict[str, str]) -> List[Dict[str, str]]:
        links = []
        for key, value in tags.items():
            links.append({"k": key, "v": value})
            if key in self.rules:
                links[-1]["vlink"] = self.rules[key].replace("$1", tags[key])
        return links


if __name__ == "__main__":
    t2l = tag2link("api/tool/tag2link_sources.json")

    print(t2l.addLinks({"website": "a"}))
    assert t2l.addLinks({"website": "a"}) == [{"k": "website", "v": "a", "vlink": "a"}]
    print(t2l.addLinks({"wikimedia_commons": "a"}))
    assert t2l.addLinks({"wikimedia_commons": "a"}) == [
        {
            "k": "wikimedia_commons",
            "v": "a",
            "vlink": "https://commons.wikimedia.org/wiki/a",
        }
    ]

    print(t2l.addLinks({"oneway": "yes"}))
    print(t2l.addLinks({"url": "plop.com"}))
    print(t2l.addLinks({"url": "http://plop.com"}))
    print(t2l.addLinks({"ref:UAI": "123"}))
    print(
        t2l.addLinks(
            {"man_made": "survey_point", "source": "©IGN 2012", "ref": "1234567 - A"}
        )
    )
    print(
        t2l.addLinks(
            {
                "url": "span://bad",
                "man_made": "survey_point",
                "source": "©IGN 2012",
                "ref": "1234567 - A",
            }
        )
    )
    print(t2l.addLinks({"wikipedia:fr": "toto"}))
    print(t2l.addLinks({"wikipedia": "fr:toto"}))
    print(t2l.addLinks({"wikipedia": "toto"}))
    print(t2l.addLinks({"source": "source", "source:url": "http://example.com"}))
