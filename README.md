# AI Scraper

Batch a list of prompts through **Perplexity** or **ChatGPT** in a real Chrome window and save every answer together with the sources it cites. Useful for small AI-visibility checks: which sites get cited when people ask about your topic.

Built by [Frank Vitetta](https://frankvitetta.com/) and the [LLM Scout](https://llmscout.co) team. Project page: [frankvitetta.com/ai-scraper](https://frankvitetta.com/ai-scraper/).

## What it does

- Opens Perplexity or ChatGPT in Chrome with Selenium
- Types each prompt, waits until the answer stops changing, captures the text
- Collects the external links in the answer (and any URLs written in the text)
- Writes `results.csv` and optionally a JSONL file
- One prompt at a time with random pauses, so it stays polite to the service

It is a sampling tool, not a monitoring platform. For share of voice across many prompts and models over time, use [LLM Scout](https://llmscout.co).

## Requirements

- Python 3.9+
- Google Chrome (Selenium 4 downloads the matching driver automatically)

```bash
pip install -r requirements.txt
```

## Usage

```bash
# default example prompts on Perplexity
python scraper.py

# your own prompts, one per row in the first CSV column
python scraper.py --site perplexity --prompts-csv prompts.csv

# ChatGPT, JSONL as well, first 5 prompts only
python scraper.py --site chatgpt --prompts-csv prompts.csv --out-jsonl out.jsonl --limit 5
```

When a site asks you to sign in, log in in the browser window and press Enter in the terminal. No credentials are stored.

### Options

| Flag | Default | Meaning |
|---|---|---|
| `--site` | `perplexity` | `perplexity` or `chatgpt` |
| `--prompts-csv` | built-in examples | CSV, one prompt per row |
| `--limit` | all | Only run the first N prompts |
| `--out-csv` | `results.csv` | Output CSV |
| `--out-jsonl` | none | Optional JSONL output |
| `--answer-timeout` | `180` | Seconds to wait for an answer |
| `--stable-seconds` | `8` | Unchanged text for this long means the answer is complete |
| `--headless` | off | Run Chrome without a window (manual login will not work) |
| `-v` | off | Debug logging |

### Output columns

`idx`, `prompt`, `answer`, `citations` (semicolon separated URLs), `error` (empty on success).

## When it breaks

Both sites change their markup. If the script cannot find the input box or the answer, update the selectors in the `SITES` table at the top of `scraper.py`. A screenshot is saved as `debug_no_input_*.png` when the input box is not found.

## Terms of service

Check the terms of the site you are scraping and keep the volume low. This tool uses a visible browser, your own logged-in account and human-like pacing; it does not try to evade bot detection.

## Contributing

Pull requests welcome: selector updates, new sites (Claude, Gemini), tests. Keep the single-file layout and run `python -m pytest` before opening a PR.

## License

MIT, see [LICENSE](LICENSE).
