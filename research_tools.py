import html
import re
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool


HEADERS = {
    "User-Agent": (
        "ResearchMultiAgent/1.0 "
        "(educational research application)"
    )
}

TIMEOUT = 20


def clean_text(text: str, max_chars: int = 8000) -> str:
    text = html.unescape(text or "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()[:max_chars]


class NewsSearchTool(BaseTool):
    name: str = "News Search"
    description: str = (
        "Search current news and web headlines for a research topic. "
        "Returns titles, dates, publishers and URLs."
    )

    def _run(self, query: str) -> str:
        try:
            url = (
                "https://news.google.com/rss/search?"
                f"q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
            )

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=TIMEOUT,
            )
            response.raise_for_status()

            root = ET.fromstring(response.content)

            results = []

            for item in root.findall(".//item")[:8]:
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                pub_date = item.findtext("pubDate", "")
                source = item.findtext("source", "")

                results.append(
                    f"TITLE: {clean_text(title)}\n"
                    f"SOURCE: {clean_text(source)}\n"
                    f"DATE: {clean_text(pub_date)}\n"
                    f"URL: {link}\n"
                )

            if not results:
                return "No news results were found."

            return "\n---\n".join(results)

        except Exception as exc:
            return f"News search failed: {exc}"


class WikipediaSearchTool(BaseTool):
    name: str = "Wikipedia Search"
    description: str = (
        "Search Wikipedia for background information about a research topic."
    )

    def _run(self, query: str) -> str:
        try:
            url = "https://en.wikipedia.org/w/api.php"

            params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": 5,
            }

            response = requests.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=TIMEOUT,
            )
            response.raise_for_status()

            data = response.json()

            results = []

            for item in data.get("query", {}).get("search", []):
                title = item.get("title", "")
                snippet = BeautifulSoup(
                    item.get("snippet", ""),
                    "html.parser",
                ).get_text(" ")

                page_url = (
                    "https://en.wikipedia.org/wiki/"
                    + quote_plus(title.replace(" ", "_"))
                )

                results.append(
                    f"TITLE: {title}\n"
                    f"SUMMARY: {clean_text(snippet)}\n"
                    f"URL: {page_url}"
                )

            if not results:
                return "No Wikipedia results were found."

            return "\n---\n".join(results)

        except Exception as exc:
            return f"Wikipedia search failed: {exc}"


class WebpageFetchTool(BaseTool):
    name: str = "Webpage Fetcher"
    description: str = (
        "Fetch a webpage URL and extract readable text from it. "
        "Use this to inspect a source before making claims."
    )

    def _run(self, url: str) -> str:
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=TIMEOUT,
                allow_redirects=True,
            )
            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser",
            )

            for element in soup(
                [
                    "script",
                    "style",
                    "noscript",
                    "svg",
                    "nav",
                    "footer",
                    "header",
                ]
            ):
                element.decompose()

            text = soup.get_text(" ", strip=True)
            text = clean_text(text, max_chars=12000)

            if not text:
                return "The webpage contained no readable text."

            return (
                f"URL: {response.url}\n\n"
                f"CONTENT:\n{text}"
            )

        except Exception as exc:
            return f"Webpage fetch failed: {exc}"


class OpenAlexSearchTool(BaseTool):
    name: str = "OpenAlex Academic Search"
    description: str = (
        "Search OpenAlex for academic papers and scholarly literature."
    )

    def _run(self, query: str) -> str:
        try:
            url = "https://api.openalex.org/works"

            params = {
                "search": query,
                "per-page": 6,
                "sort": "relevance_score:desc",
            }

            response = requests.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=TIMEOUT,
            )
            response.raise_for_status()

            data = response.json()

            results = []

            for work in data.get("results", []):
                title = work.get("display_name", "Unknown")
                year = work.get("publication_year", "Unknown")
                doi = work.get("doi") or "No DOI"

                authors = []

                for author in work.get("authorships", [])[:5]:
                    name = (
                        author.get("author", {})
                        .get("display_name")
                    )

                    if name:
                        authors.append(name)

                results.append(
                    f"TITLE: {title}\n"
                    f"YEAR: {year}\n"
                    f"AUTHORS: {', '.join(authors)}\n"
                    f"DOI: {doi}"
                )

            if not results:
                return "No OpenAlex results were found."

            return "\n---\n".join(results)

        except Exception as exc:
            return f"OpenAlex search failed: {exc}"


class CrossrefSearchTool(BaseTool):
    name: str = "Crossref Academic Search"
    description: str = (
        "Search Crossref for scholarly publications and DOI metadata."
    )

    def _run(self, query: str) -> str:
        try:
            url = "https://api.crossref.org/works"

            params = {
                "query.bibliographic": query,
                "rows": 6,
            }

            response = requests.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=TIMEOUT,
            )
            response.raise_for_status()

            data = response.json()

            results = []

            for item in data.get("message", {}).get("items", []):
                title_list = item.get("title", [])
                title = title_list[0] if title_list else "Unknown"

                authors = []

                for author in item.get("author", [])[:5]:
                    given = author.get("given", "")
                    family = author.get("family", "")

                    full_name = f"{given} {family}".strip()

                    if full_name:
                        authors.append(full_name)

                published = (
                    item.get("published-print")
                    or item.get("published-online")
                    or {}
                )

                date_parts = published.get(
                    "date-parts",
                    [[]],
                )[0]

                year = date_parts[0] if date_parts else "Unknown"

                doi = item.get("DOI", "No DOI")

                results.append(
                    f"TITLE: {clean_text(title)}\n"
                    f"YEAR: {year}\n"
                    f"AUTHORS: {', '.join(authors)}\n"
                    f"DOI: https://doi.org/{doi}"
                )

            if not results:
                return "No Crossref results were found."

            return "\n---\n".join(results)

        except Exception as exc:
            return f"Crossref search failed: {exc}"


class ArxivSearchTool(BaseTool):
    name: str = "arXiv Search"
    description: str = (
        "Search arXiv for relevant research papers."
    )

    def _run(self, query: str) -> str:
        try:
            url = "https://export.arxiv.org/api/query"

            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": 6,
                "sortBy": "relevance",
            }

            response = requests.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=TIMEOUT,
            )
            response.raise_for_status()

            root = ET.fromstring(response.content)

            namespace = {
                "atom": "http://www.w3.org/2005/Atom"
            }

            results = []

            for entry in root.findall(
                "atom:entry",
                namespace,
            ):
                title = entry.findtext(
                    "atom:title",
                    "",
                    namespace,
                )

                summary = entry.findtext(
                    "atom:summary",
                    "",
                    namespace,
                )

                published = entry.findtext(
                    "atom:published",
                    "",
                    namespace,
                )

                paper_url = ""

                for link in entry.findall(
                    "atom:link",
                    namespace,
                ):
                    if link.attrib.get("rel") == "alternate":
                        paper_url = link.attrib.get("href", "")
                        break

                results.append(
                    f"TITLE: {clean_text(title)}\n"
                    f"PUBLISHED: {clean_text(published)}\n"
                    f"SUMMARY: {clean_text(summary, 1500)}\n"
                    f"URL: {paper_url}"
                )

            if not results:
                return "No arXiv results were found."

            return "\n---\n".join(results)

        except Exception as exc:
            return f"arXiv search failed: {exc}"
