# Cat Litter Review Insights

A Codex skill for collecting permitted public cat-litter product reviews and producing evidence-bounded competitor analysis.

## What it does

- Collects server-rendered, publicly accessible structured reviews from one product URL at a time.
- Checks `robots.txt`, limits collection to 100 reviews per URL, and does not retain reviewer identity.
- Routes the resulting CSV into a review-analysis workflow for cleaning, tagging, evaluation, and reporting.

## Install

Clone this repository into your Codex skills directory, using the skill name as the directory name:

```powershell
git clone https://github.com/wvs8999h28-design/agent.git "$env:USERPROFILE\.codex\skills\cat-litter-review-insights"
```

Restart Codex or start a new task, then invoke:

```text
$cat-litter-review-insights analyze these cat-litter product URLs: ...
```

## Collection boundaries

The collector only reads content visible without login in the returned HTML. It does not log in, bypass CAPTCHAs or anti-bot controls, call undocumented APIs, follow pagination, or collect usernames, IDs, or avatars. If a page is JavaScript-rendered, restricted, or disallowed by `robots.txt`, use a platform-permitted export or authorized API instead.

## Repository layout

```text
SKILL.md
agents/openai.yaml
scripts/collect_public_reviews.py
references/collection.md
```

## License

No license has been granted. Contact the repository owner before reusing or redistributing this project.
