"""reddit-argument-map: read-only collection of arguments from public Reddit threads.

Personal, non-commercial use. Only read requests are made.
"""
import argparse
import datetime as dt
import os
import pathlib

import praw
from dotenv import load_dotenv

VERSION = "0.1.0"


def reddit_client() -> praw.Reddit:
    load_dotenv()
    user = os.environ["REDDIT_USERNAME"]
    return praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent=f"script:reddit-argument-map:v{VERSION} (by /u/{user})",
        check_for_async=False,
    )


def find_threads(reddit, query, subreddits, time_filter, limit):
    sub = reddit.subreddit("+".join(subreddits)) if subreddits else reddit.subreddit("all")
    posts = list(sub.search(query, sort="relevance", time_filter=time_filter, limit=limit * 2))
    posts.sort(key=lambda p: p.num_comments, reverse=True)
    return posts[:limit]


def collect_comments(submission, per_sort):
    seen, rows = set(), []
    for sort in ("top", "controversial"):
        submission.comment_sort = sort
        submission.comments.replace_more(limit=0)
        for c in submission.comments.list()[:per_sort]:
            if c.id in seen or c.body in ("[deleted]", "[removed]"):
                continue
            seen.add(c.id)
            rows.append({
                "sort": sort,
                "depth": c.depth,
                "score": c.score,
                "date": dt.datetime.utcfromtimestamp(c.created_utc).date().isoformat(),
                "text": " ".join(c.body.split())[:300],
                "link": f"https://www.reddit.com{c.permalink}",
            })
    return rows


def write_markdown(topic, threads, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{dt.date.today():%Y-%m}-{topic.replace(' ', '-')[:40]}.md"
    lines = [f"# Reddit: {topic}", f"Stand: {dt.date.today()}", ""]
    for sub, comments in threads:
        lines += [f"## {sub.title}", f"r/{sub.subreddit} · {sub.num_comments} comments · "
                  f"https://www.reddit.com{sub.permalink}", "",
                  "| Sort | Depth | Score | Date | Excerpt (working copy, delete after evaluation) | Link |",
                  "|---|---|---|---|---|---|"]
        for r in comments:
            text = r["text"].replace("|", "/")
            lines.append(f"| {r['sort']} | {r['depth']} | {r['score']} | {r['date']} | {text} | [link]({r['link']}) |")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("topic")
    ap.add_argument("--subreddits", nargs="*", default=[])
    ap.add_argument("--time", default="year", choices=["month", "year", "all"])
    ap.add_argument("--threads", type=int, default=15)
    ap.add_argument("--comments", type=int, default=40, help="comments per sort and thread")
    ap.add_argument("--out", default="output")
    a = ap.parse_args()

    reddit = reddit_client()
    threads = [(s, collect_comments(s, a.comments))
               for s in find_threads(reddit, a.topic, a.subreddits, a.time, a.threads)]
    print(write_markdown(a.topic, threads, pathlib.Path(a.out)))


if __name__ == "__main__":
    main()
