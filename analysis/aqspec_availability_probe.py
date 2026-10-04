#!/usr/bin/env python3
"""Snapshot a bounded AQ-SPEC availability probe; this does not ingest measurements.

Run with a new directory outside git. Requires curl and pdftotext. Downloaded
reports/pages stay there; only the source inventory belongs in the repository.
"""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

SOURCES = {
    "evaluations": "https://www.aqmd.gov/aq-spec/evaluations",
    "summary": "https://www.aqmd.gov/aq-spec/evaluations/summary-table",
    "field": "https://www.aqmd.gov/aq-spec/evaluations/criteria-pollutants/field",
    "sensors": "https://www.aqmd.gov/aq-spec/sensors",
    "airsensor": "https://www.aqmd.gov/aq-spec/special-projects/airsensor",
    "aqy_network": "https://www.aqmd.gov/aq-spec/special-projects/aeroqual-aqy-deployments",
    "library_news": "https://www.aqmd.gov/home/research/pubs-docs-reports/newsletters/may-jun-jul-2026/empowering-communities--air-quality-sensor-library-and-new-dashboard",
    "legacy_viewer": "http://tools.mazamascience.com:6709/asdv/test/",
    "terms": "https://www.aqmd.gov/privacy/terms-of-use",
    "pa_ii_2026": "https://www.aqmd.gov/docs/default-source/aq-spec/field-evaluations/purpleair-pa-ii---field-evaluation_2026.pdf?sfvrsn=ea8b667e_3",
    "field_protocol": "https://www.aqmd.gov/docs/default-source/aq-spec/protocols/sensors-field-testing-protocol.pdf?sfvrsn=5824c061_0",
    "viewer_guide": "https://www.aqmd.gov/docs/default-source/aq-spec/research-projects/airsensor-dataviewer-user-guide.pdf?sfvrsn=e2cd861_8",
}

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = set()

    def handle_starttag(self, tag, attrs):
        href = dict(attrs).get("href")
        if tag == "a" and href:
            self.hrefs.add(href)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    args.directory.mkdir(parents=True, exist_ok=False)
    inventory = []
    for name, url in SOURCES.items():
        suffix = ".pdf" if urlparse(url).path.endswith(".pdf") else ".html"
        target = args.directory / (name + suffix)
        request = subprocess.run(
            ["curl", "-fLSs", "--max-time", "30", "-o", str(target),
             "-w", "%{http_code}\n%{url_effective}\n%{content_type}", url],
            capture_output=True, text=True,
        )
        row = dict(id=name, url=url, retrieved_utc=datetime.now(timezone.utc).isoformat(),
                   curl_exit=request.returncode, response=request.stdout.splitlines(),
                   error=request.stderr.strip(), local_file=target.name)
        if request.returncode == 0:
            raw = target.read_bytes()
            row.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
            if suffix == ".pdf":
                text_path = target.with_suffix(".txt")
                subprocess.run(["pdftotext", "-layout", str(target), str(text_path)], check=True)
                row["extracted_text_characters"] = len(text_path.read_text())
            else:
                links = Links()
                links.feed(raw.decode("utf-8"))
                urls = sorted({urljoin(url, h) for h in links.hrefs})
                row["tabular_file_links"] = [u for u in urls if urlparse(u).path.lower().endswith(
                    (".csv", ".tsv", ".xlsx", ".xls", ".json", ".zip"))]
                row["selected_report_links"] = [u for u in urls if u in SOURCES.values() and urlparse(u).path.lower().endswith(".pdf")]
        inventory.append(row)
    result = dict(scope="Listed pages and linked selected PDFs; not an exhaustive archive search. "
                        "Static anchor scan does not resolve JavaScript exports or APIs.",
                  attribution="South Coast Air Quality Management District, AQ-SPEC",
                  data_licence="No explicit licence for paired temperature data established; "
                               "see terms snapshot and human review in aqspec_feasibility.md.",
                  sources=inventory)
    out = args.directory / "source_inventory.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(out)
    for row in inventory:
        print(row["id"], "curl_exit=", row["curl_exit"], "bytes=", row.get("bytes"),
              "tabular_links=", len(row.get("tabular_file_links", [])))


if __name__ == "__main__":
    main()
