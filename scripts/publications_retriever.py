#!/usr/bin/env python3
"""
Script to retrieve the labs publication from Crossref/Scholar
"""

import requests
import yaml

with open("lab_list.yml", "r") as f:
    researchers: list[dict[str, str]] = list(
        yaml.load_all(f, Loader=yaml.loader.SafeLoader)
    )

for researcher in researchers:
    if "orcid" in researcher:
        request_parameters = {"filter": "orcid:" + researcher["orcid"], "rows": 100}
        r = requests.get("https://api.crossref.org/works", request_parameters)
        data = r.json()
        for item in data["message"]["items"]:
            title = item.get("title", [""])[0]
            doi = item.get("DOI", "")
            year = item.get("created", {}).get("date-parts", [[None]])[0][0]
            authors = item.get("author", [])
            author_list = [
                f"{a.get('given', '')} {a.get('family', '')}" for a in authors
            ]
            print("-----------------------------------------------------")
            print(f"{title} ({year}) {author_list} https://doi.org/{doi}")
            print("-----------------------------------------------------")
            print("Abstract:")
            url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,abstract,authors,year,url"
            abstract = requests.get(url).json().get("abstract")
            abstract2 = item.get("abstract", "")
            if abstract is not None:
                print(abstract)
            else:
                print(abstract2)
            print("-----------------------------------------------------")
            url = f"https://api.crossref.org/works/{doi}/transform/application/x-bibtex"
            bibtex = requests.get(url).text
            print(bibtex)

# Store all the data in a yaml file, then render .md files. Script updates the database, then re-renders, so database is always true and no duplication. Rendering layout can change.
