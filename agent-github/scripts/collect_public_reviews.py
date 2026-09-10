#!/usr/bin/env python3
"""Collect public, server-rendered product reviews into review-agent CSV format.

This deliberately supports one URL only: it checks robots.txt, makes one request,
and extracts review objects already embedded in the returned HTML. It neither logs
in nor discovers hidden endpoints, scrolls, paginates, or stores reviewer identity.
"""

import argparse
import csv
import html
import ipaddress
import json
import socket
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

FIELDS = ["product_id", "product_name", "brand", "price", "rating", "content", "review_date"]
USER_AGENT = "review-agent-public-collector/1.0"


class ScriptReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self._type = ""
        self._parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self._type = dict(attrs).get("type", "").lower()
            self._parts = []

    def handle_data(self, data):
        if self._parts is not None:
            self._parts.append(data)

    def handle_endtag(self, tag):
        if tag == "script":
            text = "".join(self._parts).strip()
            if text and ("json" in self._type or text.startswith("{") or text.startswith("[")):
                self.scripts.append(text)
            self._parts = []
            self._type = ""


def public_http_url(value):
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("URL 必须是带域名的 http 或 https 地址")
    host = parsed.hostname
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, None)}
    except socket.gaierror as exc:
        raise ValueError(f"无法解析域名: {host}") from exc
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise ValueError("不采集本机、内网或保留地址")
    return parsed


def robots_allowed(parsed):
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    parser = RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
    except (HTTPError, URLError, OSError) as exc:
        if isinstance(exc, HTTPError) and exc.code == 404:
            return True
        raise RuntimeError(f"无法读取 robots.txt，停止采集: {exc}") from exc
    return parser.can_fetch(USER_AGENT, parsed.geturl())


def get_page(url):
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
    try:
        with urlopen(request, timeout=25) as response:
            content_type = response.headers.get_content_type()
            if content_type not in {"text/html", "application/xhtml+xml"}:
                raise RuntimeError(f"目标不是 HTML 页面（{content_type}）")
            return response.read(3_000_000).decode(response.headers.get_content_charset() or "utf-8", errors="replace")
    except (HTTPError, URLError, OSError) as exc:
        raise RuntimeError(f"无法读取公开页面: {exc}") from exc


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def first_text(value):
    if isinstance(value, list):
        return " ".join(str(x) for x in value)
    return str(value or "").strip()


def review_from(obj):
    kind = obj.get("@type", obj.get("type", ""))
    kinds = {str(x).lower() for x in (kind if isinstance(kind, list) else [kind])}
    body = first_text(obj.get("reviewBody") or obj.get("review_body") or obj.get("content"))
    if "review" not in kinds and not (body and ("ratingValue" in obj or "reviewRating" in obj)):
        return None
    body = html.unescape(body).replace("\r", " ").replace("\n", " ").strip()
    if not body:
        return None
    rating = obj.get("ratingValue") or (obj.get("reviewRating") or {}).get("ratingValue")
    published = first_text(obj.get("datePublished") or obj.get("date") or obj.get("review_date"))[:10]
    return {"content": body, "rating": str(rating or ""), "review_date": published}


def extract_reviews(page, limit):
    parser = ScriptReader()
    parser.feed(page)
    found, seen = [], set()
    for raw in parser.scripts:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for obj in walk(payload):
            if not isinstance(obj, dict):
                continue
            review = review_from(obj)
            if review and review["content"] not in seen:
                found.append(review)
                seen.add(review["content"])
                if len(found) >= limit:
                    return found
    return found


def main():
    ap = argparse.ArgumentParser(description="采集单个公开 HTML 页面中的结构化评论")
    ap.add_argument("--url", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--product-id", required=True)
    ap.add_argument("--product-name", required=True)
    ap.add_argument("--brand", default="")
    ap.add_argument("--price", default="")
    ap.add_argument("--max", type=int, default=100)
    args = ap.parse_args()
    if not 1 <= args.max <= 100:
        ap.error("--max 必须在 1 到 100 之间")

    parsed = public_http_url(args.url)
    if not robots_allowed(parsed):
        raise SystemExit("robots.txt 不允许此采集器访问该页面，未发起页面请求。")
    reviews = extract_reviews(get_page(args.url), args.max)
    if not reviews:
        raise SystemExit("页面中没有可用的公开结构化评论。请使用平台允许的导出数据。")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        for review in reviews:
            writer.writerow({"product_id": args.product_id, "product_name": args.product_name,
                             "brand": args.brand, "price": args.price, **review})
    print(f"已保存 {len(reviews)} 条公开结构化评论到 {output}")


if __name__ == "__main__":
    main()
