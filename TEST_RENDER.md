# Testing Your Render Deployment

## Quick Test Commands

Once your Render service is deployed, you'll get a URL like:
```
https://your-service-name.onrender.com
```

### Option 1: Using the Test Script (Recommended)

```bash
# Test with your Render URL
python test_render_deployment.py https://your-service-name.onrender.com
```

The script will test:
- ✅ Health check endpoint
- ✅ Invalid JSON → 400
- ✅ Invalid secret → 403
- ✅ Valid request → 200

### Option 2: Manual Testing with curl

```bash
# 1. Health check
curl https://your-service-name.onrender.com/health

# 2. Test invalid JSON (should return 400)
curl -X POST https://your-service-name.onrender.com/ \
  -H "Content-Type: application/json" \
  -d "invalid json"

# 3. Test invalid secret (should return 403)
curl -X POST https://your-service-name.onrender.com/ \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com", "secret": "wrong", "url": "https://example.com"}'

# 4. Test valid request (should return 200)
curl -X POST https://your-service-name.onrender.com/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "22f3002468@ds.study.iitm.ac.in",
    "secret": "your-secret-string",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

### Option 3: Using Python requests

```python
import requests

render_url = "https://your-service-name.onrender.com"

# Health check
response = requests.get(f"{render_url}/health")
print(response.json())

# Test endpoint
response = requests.post(
    f"{render_url}/",
    json={
        "email": "22f3002468@ds.study.iitm.ac.in",
        "secret": "your-secret-string",
        "url": "https://tds-llm-analysis.s-anand.net/demo"
    }
)
print(response.status_code)
print(response.json())
```

## Expected Results

### Health Check
```json
{
  "status": "ok",
  "time": "2025-11-29T..."
}
```

### Valid Request
```json
{
  "status": "ok",
  "message": "Quiz processing started.",
  "started_at": "2025-11-29T...",
  "deadline": "2025-11-29T..."
}
```

## Troubleshooting

### First Request is Slow (30-60 seconds)
- **Normal for Render free tier**
- Service "wakes up" after sleep
- Subsequent requests are faster

### Connection Timeout
- Service may still be building
- Check Render dashboard for build status
- Wait 5-10 minutes after deployment

### 403 Forbidden
- Check `SECRET` in Render environment variables
- Must match your `.env` file
- Must match Google Form submission

### 500 Internal Server Error
- Check Render logs (Dashboard → Your Service → Logs)
- Verify all environment variables are set
- Check if LLM API key is valid

## After Successful Test

Once all tests pass:
1. ✅ Copy your endpoint URL: `https://your-service-name.onrender.com/`
2. ✅ Submit in Google Form
3. ✅ Monitor during evaluation period

Your endpoint is ready! 🎉

