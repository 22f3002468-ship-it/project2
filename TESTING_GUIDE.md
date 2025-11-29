# Testing Guide - LLM Analysis Quiz

This guide helps you test your endpoint comprehensively to ensure you get full marks.

## Quick Start

1. **Start your server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **Run comprehensive tests:**
   ```bash
   python run_tests.py
   ```

## Test Coverage

### 1. Endpoint Response Codes (Critical for Full Score)

#### ✅ Test: Invalid JSON → 400
```bash
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d "this is not json"
```
**Expected:** Status code 400

#### ✅ Test: Invalid Secret → 403
```bash
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "secret": "wrong-secret", "url": "https://example.com"}'
```
**Expected:** Status code 403

#### ✅ Test: Valid Request → 200
```bash
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com", "secret": "your-secret", "url": "https://tds-llm-analysis.s-anand.net/demo"}'
```
**Expected:** Status code 200 with JSON response

### 2. Response Structure Validation

The response must include:
- `status`: "ok"
- `message`: string
- `started_at`: ISO datetime string
- `deadline`: ISO datetime string (3 minutes from started_at)

### 3. Quiz Solving Capabilities

#### Static Page Scraping
Test with a simple HTML page that doesn't require JavaScript.

#### Dynamic Page Rendering
Test with JavaScript-rendered pages (like the demo URL).

#### File Processing
- CSV files: Should be parsed and analyzed
- JSON files: Should be parsed and analyzed
- PDF files: Should extract text (if PyPDF2 is installed)
- Excel files: Should be parsed (if pandas/openpyxl is installed)

#### API Endpoint Fetching
Test with quiz pages that mention API endpoints.

#### Answer Submission
- Correct answers should proceed to next URL
- Wrong answers should allow retries
- Multiple quiz rounds should be handled

## Running Tests

### Automated Tests

```bash
# Full test suite
python test_comprehensive.py http://localhost:8000 your-email@example.com your-secret

# Quick test
python test_endpoint.py
```

### Manual Testing

1. **Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Invalid JSON:**
   ```bash
   curl -X POST http://localhost:8000/ -d "invalid"
   ```

3. **Invalid Secret:**
   ```bash
   curl -X POST http://localhost:8000/ \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "secret": "wrong", "url": "https://example.com"}'
   ```

4. **Valid Request:**
   ```bash
   curl -X POST http://localhost:8000/ \
     -H "Content-Type: application/json" \
     -d '{"email": "your-email@example.com", "secret": "your-secret", "url": "https://tds-llm-analysis.s-anand.net/demo"}'
   ```

## Common Issues

### Issue: Tests fail with connection error
**Solution:** Make sure the server is running on the correct port.

### Issue: 403 errors even with correct secret
**Solution:** Check your `.env` file - the SECRET must match exactly.

### Issue: 400 errors on valid JSON
**Solution:** Check that all required fields (email, secret, url) are present and valid.

### Issue: Deadline not calculated correctly
**Solution:** Verify the deadline is approximately 3 minutes (180 seconds) from started_at.

## Evaluation Checklist

Before submission, ensure:

- [ ] All endpoint response codes are correct (400, 403, 200)
- [ ] Response structure matches specification
- [ ] Deadline is calculated correctly (3 minutes)
- [ ] Server handles concurrent requests
- [ ] Quiz solving works for various question types
- [ ] Error handling is robust
- [ ] Logging is informative
- [ ] Code is clean and well-documented

## Tips for Full Score

1. **Test all edge cases:** Missing fields, invalid formats, etc.
2. **Verify response structure:** All required fields must be present
3. **Check deadline calculation:** Must be exactly 3 minutes from POST
4. **Test retry logic:** Wrong answers should allow retries
5. **Handle errors gracefully:** Don't crash on unexpected inputs
6. **Log important events:** Helps with debugging during evaluation

## Support

If you encounter issues:
1. Check server logs for errors
2. Verify `.env` file configuration
3. Test with the demo URL first
4. Review the comprehensive test output

Good luck! 🚀

