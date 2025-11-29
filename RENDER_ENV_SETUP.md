# Render Environment Variables Setup - URGENT

## ⚠️ Deployment Failed - Missing Environment Variables

Your deployment failed because these required environment variables are not set in Render:

```
email
secret
llm_api_key
```

## 🔧 Quick Fix (5 minutes)

### Step 1: Go to Render Dashboard
1. Open your Render service: https://dashboard.render.com/
2. Click on your service name
3. Go to **"Environment"** tab (left sidebar)

### Step 2: Add Required Environment Variables

Click **"Add Environment Variable"** and add these **ONE BY ONE**:

#### 1. EMAIL
- **Key**: `EMAIL`
- **Value**: `22f3002468@ds.study.iitm.ac.in`
- Click **"Save Changes"**

#### 2. SECRET
- **Key**: `SECRET`
- **Value**: `your-secret-string` (MUST match what you'll submit in Google Form!)
- Click **"Save Changes"**

#### 3. LLM_API_KEY
- **Key**: `LLM_API_KEY`
- **Value**: `sk-your-openai-api-key` (Your OpenAI API key)
- Click **"Save Changes"**

#### 4. LLM_MODEL (Optional but recommended)
- **Key**: `LLM_MODEL`
- **Value**: `gpt-4o-mini`
- Click **"Save Changes"**

#### 5. LOG_LEVEL (Optional)
- **Key**: `LOG_LEVEL`
- **Value**: `INFO`
- Click **"Save Changes"**

### Step 3: Redeploy

After adding all environment variables:
1. Go to **"Manual Deploy"** tab
2. Click **"Deploy latest commit"**
3. Wait for deployment to complete (5-10 minutes)

## ✅ Verification

After redeploy, check the logs. You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

## 🧪 Test Your Deployment

Once deployed, test with:

```bash
python test_render_deployment.py https://your-service-name.onrender.com
```

## 📋 Complete Environment Variables List

Make sure you have ALL of these set:

| Variable | Required | Example Value |
|----------|----------|---------------|
| `EMAIL` | ✅ Yes | `22f3002468@ds.study.iitm.ac.in` |
| `SECRET` | ✅ Yes | `your-secret-string` |
| `LLM_API_KEY` | ✅ Yes | `sk-...` |
| `LLM_MODEL` | ⚠️ Recommended | `gpt-4o-mini` |
| `LLM_BASE_URL` | ❌ Optional | (leave empty for OpenAI) |
| `LOG_LEVEL` | ❌ Optional | `INFO` |

## ⚠️ Important Notes

1. **SECRET must match** what you submit in Google Form
2. **Never commit** `.env` file (already in .gitignore)
3. **Environment variables are encrypted** in Render
4. **After adding env vars**, you MUST redeploy

## 🚨 Common Issues

### Issue: Still getting validation errors
- **Solution**: Make sure you clicked "Save Changes" after each variable
- **Solution**: Check variable names are EXACTLY: `EMAIL`, `SECRET`, `LLM_API_KEY` (case-sensitive)

### Issue: Service won't start
- **Solution**: Check logs for specific error messages
- **Solution**: Verify all required variables are set
- **Solution**: Make sure LLM_API_KEY is valid

### Issue: 403 Forbidden
- **Solution**: Verify SECRET matches your .env file
- **Solution**: SECRET must match Google Form submission

## 🎯 Next Steps

1. ✅ Add environment variables in Render
2. ✅ Redeploy service
3. ✅ Test with test script
4. ✅ Submit endpoint URL in Google Form

Your deployment will work once environment variables are set!

