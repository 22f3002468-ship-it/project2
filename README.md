# LLM Analysis Quiz – FastAPI Solution

This project implements the API endpoint described in the **LLM Analysis Quiz** spec.

## Features

- FastAPI endpoint `/` that:
  - Accepts POST JSON with `{ email, secret, url, ... }`
  - Returns:
    - `400` for invalid JSON
    - `403` for invalid secret
    - `200` JSON for valid payload & secret
- Background task that:
  - Visits the quiz URL using **Playwright** (JavaScript executed)
  - Uses **OpenAI** to:
    - Understand the question
    - Find the submit URL
    - Build the correct JSON payload
  - Submits the answer using **httpx**
  - Follows the chain of quiz URLs until finished or time/depth limit hit

## Setup

```bash
git clone <your-repo-url>
cd llm-analysis-quiz

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
playwright install
