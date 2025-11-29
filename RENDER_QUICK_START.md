# Render Deployment - Quick Start

## ✅ Step 1: Code Pushed to GitHub
Your code is now at: `https://github.com/22f3002468-ship-it/project2.git`

## 🚀 Step 2: Deploy on Render

### Quick Setup (5 minutes)

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com/
   - Sign up/Login (free account works)

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect GitHub account (if not already)
   - Select repository: `22f3002468-ship-it/project2`

3. **Configure Service**
   - **Name**: `llm-analysis-quiz` (or any name)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && playwright install chromium && playwright install-deps chromium
     ```
   - **Start Command**: 
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

4. **Set Environment Variables**
   Click "Advanced" → "Add Environment Variable" and add:

   ```
   EMAIL=22f3002468@ds.study.iitm.ac.in
   SECRET=your-secret-string  (MUST match Google Form submission!)
   LLM_API_KEY=sk-your-openai-api-key
   LLM_MODEL=gpt-4o-mini
   LOG_LEVEL=INFO
   ```

   **Important**: 
   - `SECRET` must match what you submit in Google Form
   - `LLM_API_KEY` is your OpenAI API key
   - Leave `LLM_BASE_URL` empty if using OpenAI

5. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for build
   - Your service will be live at: `https://your-service-name.onrender.com`

## 🧪 Step 3: Test Your Deployment

Once deployed, test with:

```bash
# Health check
curl https://your-service-name.onrender.com/health

# Test endpoint
curl -X POST https://your-service-name.onrender.com/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "22f3002468@ds.study.iitm.ac.in",
    "secret": "your-secret-string",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

## 📝 Step 4: Submit in Google Form

Your endpoint URL will be:
```
https://your-service-name.onrender.com/
```

Use this URL in your Google Form submission!

## ⚠️ Important Notes

1. **First Deploy**: Takes 5-10 minutes (Playwright installation)
2. **Free Tier**: Service sleeps after 15 min inactivity
3. **Cold Start**: First request after sleep may take 30-60 seconds
4. **Secrets**: Never commit `.env` file (already in .gitignore)

## 🔧 Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Ensure all dependencies in `requirements.txt`
- Playwright install may take time

### Service Crashes
- Check logs: Render Dashboard → Your Service → Logs
- Verify environment variables are set correctly
- Check if LLM API key is valid

### 403 Errors
- Verify `SECRET` in Render matches your `.env` file
- Must match what you submit in Google Form

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Render service created
- [ ] Environment variables set
- [ ] Build successful
- [ ] Health check works
- [ ] Test endpoint works
- [ ] Endpoint URL copied for Google Form

## 🎉 You're Done!

Once deployed, your endpoint is ready for evaluation!

