"""Publish a complete, validated public name snapshot; retain Pages on failure."""
import json
import os
import re
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

SOURCE = "https://flame-vip-service.dscrkn6cf8.chatgpt.site/api/names"
MAX_BYTES = 1_800_000


def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": "FlameNamesPublisher/1.0", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(request, timeout=15) as response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Feed exceeds supported capacity")
    return data.decode("utf-8", errors="strict")


def parse_feed(text):
    if not text.endswith("\n") or "\r" in text:
        raise ValueError("Invalid feed framing")
    lines = text[:-1].split("\n")
    if len(lines) < 2 or lines[0] != "FLAME_NAMES_V1" or not re.fullmatch(r"0|[1-9][0-9]{0,14}", lines[1]):
        raise ValueError("Invalid protocol or revision")
    names = lines[2:]
    if len(names) > 10000:
        raise ValueError("Too many names")
    seen = set()
    for name in names:
        if (not name or name != name.strip() or len(name.encode("utf-16-le")) // 2 > 64
                or any(c in name for c in "|<>")
                or any(unicodedata.category(c).startswith("C") for c in name)
                or re.search(r"https?://|discord\.gg/", name, re.I)):
            raise ValueError("Invalid name")
        key = name.lower()
        if key in seen:
            raise ValueError("Duplicate name")
        seen.add(key)
    return int(lines[1]), len(names)


def healthy(status, started):
    return (status.get("ready") is True and not status.get("sourceError")
            and status.get("syncingHistory") is False
            and status.get("messageContentEnabled") is True
            and status.get("commandsRegistered") is True
            and status.get("ownerConfigured") is True
            and isinstance(status.get("lastChecked"), int)
            and status["lastChecked"] >= started)


def snapshot():
    started = int(time.time() * 1000)
    deadline = time.monotonic() + 150
    while time.monotonic() < deadline:
        before = json.loads(get(SOURCE + "?status=1"))
        if healthy(before, started):
            feed = get(SOURCE)
            revision, count = parse_feed(feed)
            after = json.loads(get(SOURCE + "?status=1"))
            if (healthy(after, started) and before["revision"] == revision == after["revision"]
                    and before["names"] == count == after["names"]):
                return feed, revision, count
        time.sleep(2)
    raise RuntimeError("No fresh, complete source snapshot; existing Pages retained")


def main():
    feed, revision, count = snapshot()
    previous_url = os.environ.get("PUBLISHED_FEED_URL")
    unchanged = False
    if previous_url:
        try:
            previous = get(previous_url)
        except urllib.error.HTTPError as error:
            if error.code != 404:
                raise
        else:
            old_revision, _ = parse_feed(previous)
            if old_revision > revision:
                raise RuntimeError("Source revision went backwards; existing Pages retained")
            unchanged = previous == feed
    if not unchanged:
        destination = Path(os.environ.get("OUTPUT_DIRECTORY", "_site"))
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "flame-names.txt").write_text(feed, encoding="utf-8", newline="\n")
        (destination / ".nojekyll").write_text("", encoding="utf-8")
        (destination / "index.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Flame Community</title><h1>Flame Community</h1><p>Public names submitted to the Flame community channel.</p><a href="flame-names.txt">World names feed</a></html>\n', encoding="utf-8")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            output.write("changed=" + str(not unchanged).lower() + "\n")
    print(f"Validated {count} public names, revision {revision}; changed={not unchanged}")


if __name__ == "__main__":
    main()
