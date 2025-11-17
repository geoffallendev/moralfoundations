# Moral Foundations AI Analyzer

A LangChain-based tool for analyzing how different Large Language Models (LLMs) respond to the Moral Foundations Questionnaire (MFQ-30).

## Overview

This project uses the Moral Foundations Theory framework to evaluate and compare moral reasoning across multiple LLM providers including:
- OpenAI (GPT-4, GPT-3.5-turbo)
- Anthropic (Claude-3-Opus, Claude-3-Sonnet)
- Google (Gemini-Pro)

The Moral Foundations Questionnaire measures five moral foundations:
1. **Harm/Care** - Concern for the suffering of others
2. **Fairness/Reciprocity** - Concern for fairness and justice
3. **Loyalty/Ingroup** - Concern for group loyalty
4. **Authority/Respect** - Concern for authority and tradition
5. **Purity/Sanctity** - Concern for purity and sanctity

## Features

- Queries multiple LLMs with the MFQ-30 questionnaire
- Separate prompts for Part 1 (relevance-based) and Part 2 (agreement-based) questions
- Automatically extracts numerical ratings (0-5) from LLM responses
- Exports results in JSON and CSV formats
- Generates comprehensive analysis summaries by model and moral foundation
- Supports testing with a subset of questions before running full analysis

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd moral-foundations-ai
```

2. Create a virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your API keys:
```bash
cp .env.example .env
```

Edit [.env](.env) and add your API keys for at least one LLM provider:
```
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
```

## Usage

### Web Interface (All-in-One SPA)

The project includes a unified single-page application with three main features:

1. **Open the web interface:**
   ```bash
   # Using HTTP server (recommended):
   python -m http.server 8000
   # Then navigate to: http://localhost:8000/index.html

   # Or using Podman httpd:
   podman run -d --name httpd -p 8080:8080 -v $(pwd):/var/www/html:Z registry.redhat.io/ubi10/httpd-24
   # Then navigate to: http://localhost:8080/index.html
   ```

2. **Three integrated tabs:**
   - **Take Questionnaire** - Complete the MFQ-30 yourself and see instant results
   - **Dashboard** - View all generated reports (human and LLM)
   - **Compare Results** - Select and compare multiple reports side-by-side

### LLM Analysis (Command Line)

Run automated analysis across multiple LLMs:
```bash
python moral_foundations_analyzer.py
```

You'll be prompted to choose:
1. Analyze all 30 questions
2. Test with first 5 questions
3. Test with first 10 questions

The program will:
1. Load questions from [moralfoundations30-dataset.csv](moralfoundations30-dataset.csv)
2. Query each configured LLM with all questions
3. Save results to the `results/` directory:
   - Detailed JSON file with all responses
   - CSV summary for analysis
   - Text summary with sum of scores by moral foundation and LLM
   - Interactive HTML report with visualizations
   - **Automatically update the index for the web dashboard**

### Viewing Results

After running analysis, view results in the unified web interface:
- Navigate to the **Dashboard** tab to see all reports
- Use the **Compare Results** tab to analyze multiple LLM outputs side-by-side
- Individual HTML reports are also available in the `results/` directory

## Project Structure

- **[index.html](index.html)** - Unified SPA with:
  - Interactive questionnaire for human responses
  - Dashboard to view all reports
  - Comparison tool for analyzing multiple reports
- **[moral_foundations_analyzer.py](moral_foundations_analyzer.py)** - Main LLM analysis program
- **[generate_html_report.py](generate_html_report.py)** - HTML report generator
- **[moralfoundations30-dataset.csv](moralfoundations30-dataset.csv)** - MFQ-30 questionnaire data
- **[moral_foundations_part1_prompt](moral_foundations_part1_prompt)** - Instructions for Part 1 questions (LLM)
- **[moral_foundations_part2_prompt](moral_foundations_part2_prompt)** - Instructions for Part 2 questions (LLM)
- **[requirements.txt](requirements.txt)** - Python dependencies
- **`.env`** - API keys (not committed to version control)
- **`results/`** - Output directory for analysis results
  - `index.json` - Report index (auto-generated, used by web dashboard)
  - `moral_foundations_results_*.json` - Individual analysis data
  - `moral_foundations_results_*.html` - Individual reports
  - `summary_*.txt` - Text summaries

## Output Format

### JSON Output
Contains detailed information for each response:
- LLM name and model
- Question text
- Part number (1 or 2)
- Moral foundation category
- Full response text
- Extracted numerical value (0-5)
- Timestamp

### CSV Output
Tabular format suitable for further analysis in Excel, R, or Python.

### Summary Output
Text file with:
- Average scores by LLM and moral foundation
- Comparison of Part 1 vs Part 2 responses
- Valid response rates

## Example Results

```
claude-3-opus:
  Valid responses: 30/30
  Authority: 2.67
  Control: 3.50
  Fairness-Reciprocity: 4.17
  Harm-Care: 4.50
  Loyalty: 2.33
  Purity-Sancity: 1.83
```

## Customization

### Adding More LLMs

Edit the `_initialize_llms()` method in [moral_foundations_analyzer.py](moral_foundations_analyzer.py) to add additional models.

### Modifying Prompts

Edit [moral_foundations_part1_prompt](moral_foundations_part1_prompt) or [moral_foundations_part2_prompt](moral_foundations_part2_prompt) to change how questions are presented to the LLMs.

### Changing Temperature

Modify the `temperature` parameter in `_initialize_llms()` to control response randomness (0.0 = deterministic, 1.0 = creative).

## Requirements

- Python 3.8+
- LangChain framework
- API keys for at least one LLM provider
- Internet connection for API calls

## License

MIT License

## References

- Moral Foundations Theory: Graham, J., Haidt, J., & Nosek, B. A. (2009)
- MFQ-30: https://moralfoundations.org/





podman run -d --name httpd -p 8080:8080 -v /Users/geoff/Developer/moral-foundations-ai:/var/www/html:Z registry.redhat.io/ubi10/httpd-24
