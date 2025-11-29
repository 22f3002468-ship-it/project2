# LLM Analysis Quiz – FastAPI Solution

This project implements the API endpoint described in the **LLM Analysis Quiz** spec.

## Features

- **FastAPI endpoint** `/` that:
  - Accepts POST JSON with `{ email, secret, url, ... }`
  - Returns:
    - `400` for invalid JSON
    - `403` for invalid secret
    - `200` JSON for valid payload & secret
- **Background task** that:
  - Visits the quiz URL using **Playwright** (JavaScript executed)
  - Automatically detects static vs dynamic pages
  - Downloads and processes data files (CSV, JSON, PDF, Excel, etc.)
  - Fetches data from API endpoints when mentioned
  - Uses **LLM** (OpenAI or compatible) to:
    - Understand the question
    - Analyze the data
    - Find the submit URL
    - Generate the correct answer
  - Submits the answer using **httpx**
  - Follows the chain of quiz URLs until finished or time limit (3 minutes) reached

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd llm-analysis-quiz
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```bash
# Required: Your email and secret (as submitted in Google Form)
EMAIL=your-email@example.com
SECRET=your-secret-string

# Required: LLM API Configuration
# For OpenAI API:
LLM_API_KEY=sk-your-openai-api-key
LLM_MODEL=gpt-4o-mini
# LLM_BASE_URL=  # Leave empty for OpenAI

# Optional: For custom LLM endpoints (like OpenRouter, AI Pipe, etc.)
# LLM_BASE_URL=https://openrouter.ai/api/v1
# LLM_MODEL=openai/gpt-4o-mini
```

### 5. Run the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or for development:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://localhost:8000`

### 6. Test the endpoint

You can test with the demo endpoint:

```bash
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "secret": "your-secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

## Project Structure

```
llm-analysis-quiz/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application and endpoints
│   ├── config.py         # Configuration and settings
│   ├── models.py         # Pydantic models
│   ├── browser.py        # Web scraping (Playwright + BeautifulSoup)
│   ├── data_processor.py # Data processing (CSV, JSON, PDF, etc.)
│   ├── solver.py         # LLM-based quiz solver
│   ├── quiz_handler.py   # Quiz processing orchestration
│   └── utils.py          # Utility functions
├── requirements.txt
├── README.md
└── .env                  # Environment variables (create this)
```

## How It Works

1. **Request Handling**: The endpoint receives a POST request with email, secret, and quiz URL
2. **Secret Verification**: Validates the secret matches your configured secret
3. **Page Rendering**: Uses Playwright to render JavaScript-heavy pages or BeautifulSoup for static pages
4. **Data Collection**:
   - Extracts question text from the page
   - Identifies and downloads data files (CSV, JSON, PDF, etc.)
   - Fetches data from API endpoints if mentioned
5. **Data Processing**: Processes files based on their type (parses CSV, JSON, extracts PDF text, etc.)
6. **LLM Analysis**: Sends question and data to LLM for analysis and answer generation
7. **Answer Submission**: Submits the answer to the specified endpoint
8. **Chain Following**: If correct, follows the next quiz URL and repeats

## Supported Data Types

- **CSV files**: Parsed and converted to structured data
- **JSON files**: Parsed and formatted
- **PDF files**: Text extraction (requires PyPDF2)
- **Excel files**: Parsed using pandas (requires pandas and openpyxl)
- **Text files**: Plain text extraction
- **HTML files**: Text extraction from HTML
- **API endpoints**: JSON or text responses

## LLM Configuration

The project supports any OpenAI-compatible API:

- **OpenAI**: Set `LLM_API_KEY` and `LLM_MODEL` (e.g., `gpt-4o-mini`)
- **OpenRouter**: Set `LLM_BASE_URL=https://openrouter.ai/api/v1` and appropriate model
- **AI Pipe**: Set `LLM_BASE_URL` to your AI Pipe endpoint
- **Other providers**: Any OpenAI-compatible API endpoint

## Deployment

### Local Development

```bash
uvicorn app.main:app --reload
```

### Production (using Gunicorn)

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker (optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Testing

### Quick Test

Test your endpoint with the demo URL:

```python
import requests

response = requests.post(
    "http://localhost:8000/",
    json={
        "email": "your-email@example.com",
        "secret": "your-secret",
        "url": "https://tds-llm-analysis.s-anand.net/demo"
    }
)
print(response.json())
```

Or use the simple test script:

```bash
python test_endpoint.py
```

### Comprehensive Testing

Run the comprehensive test suite to verify all requirements:

```bash
# Make sure your .env file has EMAIL and SECRET set
python run_tests.py
```

Or run the comprehensive tests directly:

```bash
python test_comprehensive.py http://localhost:8000 your-email@example.com your-secret
```

The comprehensive test suite verifies:
- ✅ Health check endpoint
- ✅ Invalid JSON → 400
- ✅ Missing required fields → 400
- ✅ Invalid secret → 403
- ✅ Invalid URL format → 400
- ✅ Valid request → 200
- ✅ Response structure validation
- ✅ Deadline calculation (3 minutes)

### Manual Testing Checklist

Before submission, verify:

1. **Endpoint Response Codes:**
   - [ ] Invalid JSON returns 400
   - [ ] Invalid secret returns 403
   - [ ] Valid request returns 200

2. **Response Structure:**
   - [ ] Response includes `status`, `message`, `started_at`, `deadline`
   - [ ] `status` is "ok"
   - [ ] `deadline` is approximately 3 minutes from `started_at`

3. **Quiz Solving:**
   - [ ] Can solve static pages
   - [ ] Can solve JavaScript-rendered pages
   - [ ] Can download and process CSV files
   - [ ] Can download and process JSON files
   - [ ] Can download and process PDF files
   - [ ] Can fetch data from API endpoints
   - [ ] Can submit answers correctly
   - [ ] Handles wrong answers with retries
   - [ ] Follows quiz URL chains
   - [ ] Respects 3-minute deadline

## Notes

- The quiz must be solved within **3 minutes** from when the POST request reaches your server
- Answers can be resubmitted if incorrect, as long as it's within the 3-minute window
- The endpoint handles multiple quiz rounds automatically
- Make sure your deployment has sufficient resources for Playwright (headless browser)
