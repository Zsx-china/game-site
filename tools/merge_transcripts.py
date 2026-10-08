#!/usr/bin/env python3
"""Merge cloud-collected YouTube transcripts into the seoscout collected JSON.

Usage:
    python tools/merge_transcripts.py [transcripts.json] [collected.json]

transcripts.json shape (from the cloud collector):
    {"count": N, "videos": [{"id","title","url","transcript"}, ...]}
or a bare list of such dicts.

Collected target shape (seoscout/collect.py):
    {keyword, category, collected_at,
     sources: {youtube: {count, videos: []}, web: {count, pages: []}},
     total_sources}
"""
import json
import os
import sys

DEFAULT_TARGET = "output/ghost-of-yotei-wiki/out/collected/game-guide/ghost_of_ytei.json"


def load_videos(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        videos = data.get("videos", [])
    elif isinstance(data, list):
        videos = data
    else:
        raise SystemExit("unrecognised transcripts file: " + path)
    out = []
    for v in videos:
        if not isinstance(v, dict):
            continue
        vid = v.get("id") or v.get("video_id") or ""
        url = v.get("url") or ("https://www.youtube.com/watch?v=" + vid if vid else "")
        text = v.get("transcript") or v.get("content") or ""
        if not text.strip():
            continue
        out.append({
            "type": "youtube",
            "video_id": vid,
            "title": v.get("title", ""),
            "url": url,
            "content": text,
        })
    return out


def main():
    transcripts_path = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Desktop/transcripts.json")
    target = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TARGET

    videos = load_videos(transcripts_path)
    with open(target, encoding="utf-8") as f:
        collected = json.load(f)

    sources = collected.setdefault("sources", {})
    sources.setdefault("youtube", {})
    sources["youtube"]["videos"] = videos
    sources["youtube"]["count"] = len(videos)

    web_count = sources.get("web", {}).get("count", 0)
    collected["total_sources"] = len(videos) + web_count

    with open(target, "w", encoding="utf-8") as f:
        json.dump(collected, f, ensure_ascii=False, indent=2)

    print("merged youtube videos:", len(videos))
    print("total_sources:", collected["total_sources"])
    print("written:", target)


if __name__ == "__main__":
    main()
