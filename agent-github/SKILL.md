---
name: cat-litter-review-insights
description: Collect publicly accessible cat-litter product reviews and turn them into an evidence-bounded competitive analysis. Use for cat-litter review scraping, competitor comparison, pain-point analysis, or product-selection insights; do not use for private, login-gated, or anti-bot-protected data.
metadata:
  short-description: Collect and analyze public cat-litter reviews
---

# Cat-litter Review Insights

Collect public review data into a standard CSV, then use the existing `review-agent` pipeline to clean, analyze, evaluate, and report it. Preserve the user's requested products, market, and decision question; ask only for missing inputs that determine scope.

## Scope and consent

- Collect only content visible without login from user-provided public URLs. Check and follow `robots.txt`, use the collector's low default cap, and do not bypass rate limits, CAPTCHAs, access controls, or platform restrictions.
- Do not retain usernames, profile images, user IDs, or other personal data. The collector saves only review text, rating, and publication date when publicly present.
- A static-page collector cannot retrieve JavaScript-rendered reviews or pagination APIs. If it finds no structured reviews, say so and ask the user for a platform export or an authorized data source; do not improvise a workaround.

## Workflow

1. Establish the comparison brief: product URLs, target market/platform, decision to support, and whether price means listing price or normalized price per kg/L. For comparable cat litter, normalize package price per kg/L before drawing price conclusions.
2. For each eligible URL, run `scripts/collect_public_reviews.py` with an explicit product ID, name, brand, price, and output path under the analysis project's `data/raw/`. Read [collection details](references/collection.md) when collecting or troubleshooting.
3. Inspect the collector summary before importing. Do not mix samples, duplicated product URLs, different markets, or unknown price units into the same comparison.
4. Run the project's conversion/import, analysis, and report scripts. Before presenting a recommendation, use the project's evaluation export and scoring flow on an independently labelled sample when the result is intended for a consequential decision.
5. Report evidence, not just rankings: coverage, sample counts, review dates, product-level pain rates, uncertainty, and representative de-identified quotes. Keep service/logistics complaints separate from product problems.

## Deliverable standard

The final report must distinguish observed findings from recommendations. Do not claim a category-wide opportunity from a product with fewer than the configured sample threshold, and treat the `其他` tag as a prompt for qualitative review rather than a conclusion.
