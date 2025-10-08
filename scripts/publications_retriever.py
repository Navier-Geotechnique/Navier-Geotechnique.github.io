#!/usr/bin/env python3
"""
Script to retrieve the labs publication from Crossref/Scholar
"""

import requests
import yaml
from html.parser import HTMLParser


class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []

    def handle_data(self, data):
        self.result.append(data)

    def get_data(self):
        return "".join(self.result)


def strip_html_tags(text):
    parser = HTMLStripper()
    parser.feed(text)
    return parser.get_data()


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
            title = strip_html_tags(
                item.get("title", [""])[0]
            )  # Sometimes weird HTML tags in titles (2 of CO2)
            doi = item.get("DOI", "")
            year = item.get("created", {}).get("date-parts", [[None]])[0][0]
            date = item.get("created", {}).get("date-parts")[0]
            date_str = f"{date[0]}-{date[1]}-{date[2]}"
            authors = item.get("author", [])
            journal = item.get("container-title", [""])[0]
            volume = item.get("volume")
            issue = item.get("issue")
            pages = item.get("pages")
            article_number = item.get("article-number")
            author_list = [
                f"{a.get('given', '')} {a.get('family', '')}" for a in authors
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
            markdown_string += (
                (f"excerpt: By {", ".join(author_list[:-1])} and {author_list[-1]}.\n")
                if len(author_list) > 1
                else f"excerpt: By {author_list[0]}.\n"
            )
            markdown_string += f"bibtexurl: http://navier-geotechnique.github.io/files/{doi.replace('/','-')}.bib\n---\n"
            markdown_string += abstract
            with open(f"../_publications/{filename}", "w") as md_file:
                md_file.write(markdown_string)
