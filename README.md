# Job Application Form Filler

Automate the process of filling out job application forms using your structured personal data and browser automation.

## Overview
This Python application streamlines the job application process by:
- Scraping form fields from a job application HTML form
- Mapping those fields to your personal data (from `user_data.json`)
- Using a language model to intelligently match form fields to your data
- Automatically filling out the form in a browser using Playwright

## Features
- **Form Scraping:** Extracts all relevant fields (text, select, radio) from a job application form
- **Knowledge Base Mapping:** Uses a structured JSON file (`user_data.json`) as your personal knowledge base
- **LLM-Powered Matching:** Employs a language model to map form fields to the correct data points
- **Automated Form Filling:** Fills out the form in a real browser using Playwright
- **Extensible:** Easily update your data or adapt to new forms

## Project Structure
- `main.py` — Main entry point; orchestrates the workflow
- `form_filler.py` — Handles browser automation and form filling
- `form_tools.py` — Tools for scraping forms and querying the knowledge base
- `knowledge_base.py` — Loads and validates user data
- `mcp_server.py` — Simulates a server for knowledge base queries
- `mcp_tool.py` — Tool for querying the knowledge base
- `user_data.json` — Your structured personal/job data
- `job_form.html` — Sample job application form

## Setup
1. **Clone the repository**
2. **Install dependencies**
   - Python 3.8+
   - [Playwright](https://playwright.dev/python/):
     ```bash
     pip install playwright
     playwright install
     ```
   - Other dependencies (see below):
     ```bash
     pip install -r requirements.txt
     ```
   - You may need to create a `requirements.txt` with:
     ```
     playwright
     langchain
     langchain_groq
     python-dotenv
     pydantic
     ```
3. **Configure your data**
   - Edit `user_data.json` with your personal, work, and education details
4. **(Optional) Set up environment variables**
   - If using LLM APIs, add your keys to a `.env` file

## Usage
1. Ensure your `user_data.json` is up to date
2. Place or update the target job application form as `job_form.html`
3. Run the main script:
   ```bash
   python main.py
   ```
4. A browser window will open and the form will be filled automatically

## Configuration
- **user_data.json:** Your personal data in structured format
- **job_form.html:** The job application form to be filled
- **.env:** (Optional) API keys for LLM providers

## Credits
- Built with Python, Playwright, and LangChain
- LLM integration via Groq

---
Feel free to adapt or extend this project for your own job search automation! 