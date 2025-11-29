# Deploy to Render - Direct Deployment Guide

## ✅ Your Project is Ready!

Your code is already pushed to GitHub: `https://github.com/22f3002468-ship-it/project2.git`

## 🚀 Deploy Using Blueprint (Easiest Method)

### Step 1: Go to Render
1. Visit: https://dashboard.render.com/
2. Sign up/Login (free account works)

### Step 2: Deploy from Blueprint
1. Click **"New +"** → **"Blueprint"**
2. Enter your repository URL: `https://github.com/22f3002468-ship-it/project2`
3. Click **"Apply"**

### Step 3: Set Environment Variables
Render will detect `render.yaml` but you **MUST** set these environment variables manually:

1. Go to your service → **"Environment"** tab
2. Add these variables:

```
EMAIL=22f3002468@ds.study.iitm.ac.in
SECRET=your-secret-string
LLM_API_KEY=sk-your-openai-api-key
LLM_MODEL=gpt-4o-mini
LOG_LEVEL=INFO
```

**Important**: 
- `SECRET` must match what you'll submit in Google Form
- `LLM_API_KEY` is your OpenAI API key
- Click "Save Changes" after each variable

### Step 4: Deploy
1. Click **"Apply"** or **"Save Changes"**
2. Render will automatically:
   - Build your project
   - Install dependencies
   - Install Playwright
   - Start the service
3. Wait 5-10 minutes for deployment

## 🚀 Alternative: Manual Deployment

If Blueprint doesn't work, use manual setup:

### Step 1: Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect GitHub account
3. Select repository: `22f3002468-ship-it/project2`

### Step 2: Configure
- **Name**: `llm-analysis-quiz`
- **Region**: Choose closest
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

### Step 3: Set Environment Variables
Same as above - add EMAIL, SECRET, LLM_API_KEY, etc.

### Step 4: Deploy
Click **"Create Web Service"**

## ✅ After Deployment

Your service will be at: `https://your-service-name.onrender.com`

### Test It:
```bash
python test_render_deployment.py https://your-service-name.onrender.com
```

## ⚠️ Important Notes

1. **Environment Variables are REQUIRED**
   - Without them, deployment will fail
   - Set them BEFORE or DURING deployment

2. **First Deploy Takes Time**
   - Playwright installation: 3-5 minutes
   - Total build: 5-10 minutes

3. **Free Tier Limitations**
   - Service sleeps after 15 min inactivity
   - First request after sleep: 30-60 seconds

4. **SECRET Must Match**
   - Must match your `.env` file
   - Must match Google Form submission

## 🎯 Quick Checklist

- [ ] Code pushed to GitHub ✅
- [ ] Go to Render dashboard
- [ ] Deploy using Blueprint or Manual
- [ ] Set environment variables:
  - [ ] EMAIL
  - [ ] SECRET
  - [ ] LLM_API_KEY
  - [ ] LLM_MODEL (optional)
- [ ] Wait for deployment
- [ ] Test endpoint
- [ ] Copy endpoint URL for Google Form

## 🚨 Troubleshooting

### Build Fails
- Check build logs
- Verify `requirements.txt` is correct
- Playwright install may take time

### Service Won't Start
- Check environment variables are set
- Verify all required vars: EMAIL, SECRET, LLM_API_KEY
- Check logs for specific errors

### 403 Forbidden
- Verify SECRET matches your .env
- SECRET must match Google Form submission

## 🎉 You're Ready!

Once deployed and tested, submit your endpoint URL in the Google Form!

