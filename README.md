# reddit-argument-map

Personal, non-commercial, **read-only** research tool.

It searches public Reddit threads on a topic, reads the comment trees
(sorted by *top* and *controversial*) and produces a local summary of the
main arguments and counter-arguments with links back to the original threads.

## What it does
- Search public posts in selected subreddits, limited to a recent time window
- Fetch comment trees of the selected threads
- Write a Markdown table: argument · pro/contra · score · date · subreddit · link

## What it does **not** do
- No posting, voting, messaging or any other write action
- No user profiling, no collection of private data
- No long-term storage of raw Reddit data (only short summaries with links)
- No redistribution, resale or use for training AI/ML models

## Compliance
- OAuth "script" app on a single account, descriptive user agent as required
  by Reddit's Data API wiki
- Stays well below the free tier limit of 100 QPM (PRAW handles rate limits)
- Respects deleted content and deleted accounts (no raw data retained)
- Follows the Reddit Data API Terms and the Responsible Builder Policy

## Usage
```bash
pip install -r requirements.txt
cp .env.example .env   # fill in credentials of your own script app
python src/argument_map.py "induction hob reliability" \
  --subreddits Appliances Cooking de --time year --threads 15
```

## License
MIT
