# Deployment Guide - Render

## Prerequisites

1. GitHub repository (public)
2. Render account (free tier works)
3. Environment variables ready

## Step 1: Push to GitHub

```bash
# Add all files
git add .

# Commit changes
git commit -m "Complete LLM Analysis Quiz implementation with all requirements"

# Push to GitHub
git push origin main
```

## Step 2: Deploy on Render

### Option A: Using render.yaml (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml`
5. Review and deploy

### Option B: Manual Setup

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `llm-analysis-quiz` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && playwright install chromium && playwright install-deps chromium
     ```
   - **Start Command**: 
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

## Step 3: Configure Environment Variables

In Render dashboard, go to your service → Environment:

Add these variables:

```
EMAIL=your-email@example.com
SECRET=your-secret-string
LLM_API_KEY=sk-your-openai-api-key
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=  (leave empty for OpenAI, or set custom endpoint)
LOG_LEVEL=INFO
```

**Important**: 
- Set `SECRET` to match what you'll submit in Google Form
- Set `EMAIL` to match your submission
- Keep `LLM_API_KEY` secure (Render encrypts it)

## Step 4: Deploy

1. Click "Save Changes"
2. Render will automatically build and deploy
3. Wait for deployment to complete (5-10 minutes)
4. Your endpoint will be at: `https://your-service-name.onrender.com`

## Step 5: Test Deployment

```bash
# Test health check
curl https://your-service-name.onrender.com/health

# Test endpoint
curl -X POST https://your-service-name.onrender.com/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "secret": "your-secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

## Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Ensure `requirements.txt` is correct
- Playwright installation may take time

### Service Crashes
- Check logs in Render dashboard
- Verify environment variables are set
- Check if LLM API key is valid

### Timeout Issues
- Render free tier has 15-minute timeout
- Background tasks should complete within 3 minutes (quiz deadline)
- Consider upgrading if needed

### Playwright Issues
- Ensure build command includes `playwright install chromium`
- May need to add `playwright install-deps chromium`

## Render Free Tier Limitations

- **Sleeps after 15 minutes** of inactivity
- **First request** after sleep may be slow (cold start)
- **Build time** limited to 45 minutes
- **Memory** limited to 512MB

## Production Recommendations

1. **Upgrade to paid tier** for:
   - No sleep
   - Faster cold starts
   - More resources

2. **Use custom domain** (optional):
   - Add domain in Render settings
   - Update DNS records

3. **Monitor logs**:
   - Check Render dashboard regularly
   - Set up alerts if needed

## Security Notes

- ✅ Environment variables are encrypted in Render
- ✅ Never commit `.env` file
- ✅ Use HTTPS (Render provides automatically)
- ✅ Keep secrets secure

## Next Steps

After deployment:

1. ✅ Test endpoint with demo URL
2. ✅ Verify all environment variables
3. ✅ Submit endpoint URL in Google Form
4. ✅ Monitor during evaluation period

Your endpoint URL will be:
```
https://your-service-name.onrender.com/
```

Use this in your Google Form submission!

