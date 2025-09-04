# AI Scraper

A production-ready Python scraper for **Perplexity AI** and **ChatGPT** that can batch process prompts and extract answers with citations. Built with Selenium for reliability and includes advanced anti-bot detection features.

> **Developed by the helpful folks at [llmscout.co](https://llmscout.co)** - Your AI tool discovery platform

---

**💡 Discover more AI tools and resources at [llmscout.co](https://llmscout.co)**

---

## 🎯 What This Scraper Does

- **Perplexity AI**: Extracts answers with external citations, filters internal links
- **ChatGPT**: Extracts answers with embedded source citations from text
- **Smart Bot Detection**: Uses fake prompts, strategic delays, and human-like behavior
- **Citation Intelligence**: Captures URLs, company names, and source patterns
- **Batch Processing**: Handle multiple prompts from CSV files
- **Session Management**: Save and reuse login sessions

## ⚠️ Important Notice

**Please ensure Perplexity's Terms of Service allow automated access for your use case.** This scraper is designed to be respectful with low-rate, polite requests, but may break if the site changes its markup or policies.

## Features

- **Batch Processing**: Handle multiple prompts from a CSV file or use built-in examples
- **Smart Answer Extraction**: Automatically detects and extracts answer content
- **Citation Collection**: Gathers source links from answers
- **Session Management**: Save and reuse login sessions
- **Resilient Design**: Built-in retries and error handling
- **Multiple Output Formats**: CSV and optional JSONL export
- **Configurable Pacing**: Adjustable delays to be respectful to the service

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Chrome/Chromium browser** (if not already installed)
   - macOS: `brew install --cask google-chrome`
   - Ubuntu: `sudo apt install chromium-browser`
   - Windows: Download from [Chrome](https://www.google.com/chrome/)

3. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

## Quick Start

### 1. Basic Usage (Perplexity - Default)

```bash
python3 scraper.py --site perplexity
```

This runs with the built-in example prompts and saves results to `results.csv`.

### 2. Use Your Own Prompts

Create a CSV file with one prompt per row:

```bash
python3 scraper.py --site perplexity --prompts-csv my_prompts.csv
```

### 3. ChatGPT Scraping

```bash
python3 scraper.py --site chatgpt --prompts-csv prompts.csv
```

### 4. Limit for Testing

```bash
python3 scraper.py --site perplexity --prompts-csv prompts.csv --limit 5
```

### 5. Debug Mode (Visible Browser)

```bash
python3 scraper.py --site perplexity --headful
```

## Session Management

### Perplexity
- No login required for basic usage
- The scraper automatically handles Cloudflare challenges
- First prompt uses fast-fail mode to avoid bot detection

### ChatGPT
- Manual login required (browser will open)
- Uses fake warm-up prompts ("Hello", "Are you there?") to establish session
- Strategic delays between interactions to appear human-like

## Configuration

### Timing Settings

You can adjust these constants in `scraper.py`:

- `ANSWER_WAIT_SECONDS`: How long to wait for answers (default: 120s for ChatGPT, 120s for Perplexity)
- `PER_PROMPT_DELAY`: Random delay between prompts (default: 3.0-5.0s)
- `AFTER_LOGIN_DELAY`: Delay after login (default: 2.0s)
- `AFTER_NAVIGATION_DELAY`: Delay after page navigation (default: 1.0s)
- `AFTER_ANSWER_DELAY`: Delay after getting answer (default: 3.0-5.0s)

### Selectors

The scraper uses multiple fallback selectors to find input fields and answers. If the sites change their markup, update these in the script:

- `get_input_element()`: Input field detection (site-specific)
- `wait_for_answer()`: Answer container detection (site-specific)
- `extract_citations()`: Citation extraction (site-specific with advanced regex for ChatGPT)

## Output Format

### CSV Output

The scraper creates a CSV with these columns:

- `idx`: Sequential index
- `prompt`: The original question
- `answer`: Extracted answer text
- `citations`: Semicolon-separated list of source URLs

### JSONL Output

Optional JSONL format with one JSON object per line for easy processing.

## Error Handling

- **Soft Errors**: Retried automatically (e.g., input field not found)
- **Hard Errors**: Logged but processing continues
- **Failed Prompts**: Saved with "Error: [description]" in the answer field

## Troubleshooting

### Common Issues

1. **"Could not find the input box"**
   - Perplexity may have changed their markup
   - Try running with `--headful` to see what's happening
   - Update selectors in `get_input_locator()`

2. **Empty answers**
   - Increase `ANSWER_WAIT_SECONDS`
   - Check if answers are loading in a different format
   - Verify the site is accessible

3. **Playwright installation issues**
   ```bash
   python -m playwright install --force
   ```

### Debug Tips

- Use `--headful` to see the browser in action
- Check the console for JavaScript errors
- Monitor network requests in browser dev tools
- Adjust timing constants for your connection speed

## Advanced Usage

### Custom Prompts CSV Format

Your CSV should have one prompt per row in the first column:

```csv
What is the capital of France?
How does photosynthesis work?
What are the benefits of meditation?
```

### Batch Processing Large Lists

For large numbers of prompts, consider:

- Breaking into smaller batches
- Adding longer delays between batches
- Using multiple storage states if rate limited

### Integration with Other Tools

The CSV output can be easily imported into:
- Excel/Google Sheets
- Data analysis tools (Pandas, R)
- Database systems
- Other automation workflows

## Performance Considerations

- **Rate Limiting**: The scraper includes polite delays by default
- **Concurrency**: Runs one prompt at a time for stability
- **Memory**: Processes prompts sequentially to minimize memory usage
- **Network**: Respects timeouts and includes retry logic

## 🤝 Contributing

We welcome contributions! This project is open source and anyone can submit improvements.

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Test thoroughly** with both Perplexity and ChatGPT
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### What We're Looking For

- **Improved selectors** for better element detection
- **Additional AI platforms** (Claude, Gemini, etc.)
- **Better anti-bot detection** techniques
- **Enhanced citation extraction** algorithms
- **Performance optimizations** and speed improvements
- **Bug fixes** and error handling improvements
- **Documentation** improvements and examples

### Code Style

- Follow PEP 8 Python conventions
- Add comments for complex logic
- Include error handling for edge cases
- Test with both sites before submitting

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

The MIT License allows anyone to:
- Use the code commercially
- Modify the code
- Distribute the code
- Use it privately
- Sublicense it

**Please ensure compliance with the target websites' Terms of Service and applicable laws when using this scraper.**
