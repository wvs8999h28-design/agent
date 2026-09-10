# Public review collection

Run the collector once for each product URL. It reads only server-rendered HTML and emits the input CSV used by `review-agent`.

```powershell
python scripts/collect_public_reviews.py `
  --url "https://example.com/product" `
  --output "C:\path\to\review-agent\data\raw\product-a.csv" `
  --product-id "A001" --product-name "产品名" --brand "品牌" --price 39.9
```

The script checks the site's `robots.txt`, rejects local/private network targets, requests one page, and keeps at most 100 de-identified reviews by default. It only extracts public JSON-LD or JSON review objects embedded in the returned HTML. It does not scroll, log in, call undocumented APIs, or follow review pagination.

If it reports zero reviews, use a permitted platform export (then use `src/convert_raw.py`) or obtain written authorization and a documented API. Do not use browser automation to evade the platform's controls.

After collection, from the `review-agent` folder run:

```powershell
python src/load_and_clean.py
python src/analyze.py --limit 20
python src/report.py
```

Use `python src/eval_export.py --n 60`, manually label the exported sample without viewing predictions, then run `python src/eval_score.py` before relying on the model's measurements.
