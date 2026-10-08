import os, json, sys, time, subprocess, concurrent.futures

PROXY = os.environ.get("QG_PROXY", "")
QUERIES = [
    "Ghost of Yotei", "Ghost of Yotei guide", "Ghost of Yotei tips",
    "Ghost of Yotei DLC", "Ghost of Yotei Most Wanted", "Ghost of Yotei combat",
    "Ghost of Yotei armor", "Ghost of Yotei walkthrough", "Ghost of Yotei Legends",
    "Ghost of Yotei review", "Ghost of Yotei weapons", "Ghost of Yotei beginner",
]

def search_ids():
    seen = {}
    for q in QUERIES:
        cmd = [sys.executable, "-m", "yt_dlp", "ytsearch20:" + q,
               "--flat-playlist", "--skip-download", "--no-warnings",
               "--print", "%(id)s\t%(title)s"]
        if PROXY:
            cmd += ["--proxy", PROXY]
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        except Exception as e:
            print("search fail:", q, e)
            continue
        for line in p.stdout.splitlines():
            if "\t" in line:
                vid, title = line.split("\t", 1)
                seen.setdefault(vid, title)
    return seen

def fetch(vid):
    from youtube_transcript_api import YouTubeTranscriptApi
    for _ in range(3):
        try:
            t = YouTubeTranscriptApi().fetch(vid, languages=["en", "zh-Hans", "zh"])
            text = " ".join(s.text for s in t)
            if text.strip():
                return text
        except Exception as e:
            m = str(e).lower()
            if ("block" in m) or ("proxy" in m) or ("timeout" in m):
                time.sleep(2)
                continue
            return ""
    return ""

def main():
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        os.environ[k] = PROXY
    seen = search_ids()
    print("found videos:", len(seen))
    out = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        jobs = {ex.submit(fetch, v): v for v in seen}
        for i, f in enumerate(concurrent.futures.as_completed(jobs), 1):
            vid = jobs[f]
            text = f.result()
            if text:
                out.append({"id": vid, "title": seen[vid],
                            "url": "https://www.youtube.com/watch?v=" + vid,
                            "transcript": text})
                print("[%d/%d] OK %s (%d)" % (i, len(seen), vid, len(text)))
            else:
                print("[%d/%d] skip %s" % (i, len(seen), vid))
    with open("transcripts.json", "w", encoding="utf-8") as fp:
        json.dump({"count": len(out), "videos": out}, fp, ensure_ascii=False, indent=2)
    print("done count =", len(out))

main()
