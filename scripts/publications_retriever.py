#!/usr/bin/env python3
"""
Script to retrieve the labs publication from Crossref/Scholar
"""

import requests
from requests import auth
from requests.auth import AuthBase
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
            date = item.get("created", {}).get("date-parts")[0]
            date_str = f"{date[0]}-{date[1]}-{date[2]}"
            authors = item.get("author", [])
            journal = item.get("container-title", [""])[0]
            issue = item.get("issue", "")
            print(f"journal: {journal}")
            author_list = [
                f"{a.get('family', '')} {a.get('given', '')[0]}." for a in authors
            ]
            print("-----------------------------------------------------")
            print(f"{title} ({year}) {author_list} https://doi.org/{doi}")
            print("-----------------------------------------------------")
            print("Abstract:")
            url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,abstract,authors,year,url"
            abstract = requests.get(url).json().get("abstract")
            if abstract is None:
                abstract = item.get("abstract", "")
            print("-----------------------------------------------------")
            url = f"https://api.crossref.org/works/{doi}/transform/application/x-bibtex"
            bibtex = requests.get(url).text
            print(bibtex)
            with open(f"../files/{doi.replace('/','-')}.bib", "w") as bib_file:
                bib_file.write(bibtex)

            filename = f"{doi.replace('/','-')}.md"

            markdown_string = f'---\ntitle: "{title}"\ncollection: publications\ncategory: manuscripts\n'
            markdown_string += f"permalink: /publications/{doi.replace('/','-')}\n"
            markdown_string += f'date: {date_str}\nvenue: "{journal}"\n'
            markdown_string += f'paperurl: "https://dx.doi.org/{doi}"\n'
            # markdown_string += f'citation: "{author_list} ({year}) &quot;{title}.&quot; <i>{journal}</i>, {issue}"\n'
            markdown_string += f"excerpt: By {", ".join(author_list)}.\n"
            markdown_string += f"bibtexurl: http://navier-geotechnique.github.io/files/{doi.replace('/','-')}.bib\n---\n"
            markdown_string += abstract
            with open(f"../_publications/{filename}", "w") as md_file:
                md_file.write(markdown_string)
