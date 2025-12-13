# Deployment Guide: AI Intelligence Dashboard

This guide will help you deploy your AI Intelligence Dashboard to the web so you can access it from any browser without running it locally.

## Option 1: Streamlit Community Cloud (Recommended - FREE)

### Prerequisites
1. GitHub account
2. Your code pushed to a GitHub repository

### Step-by-Step Deployment

#### 1. Initialize Git Repository (if not already done)
```bash
cd C:\Users\aston_weapiyi\Documents\claude_code_projects\ai_tool_database
git init
git add .
git commit -m "Initial commit: AI Intelligence Dashboard"
```

#### 2. Create GitHub Repository
1. Go to https://github.com/new
2. Create a new repository (name it `ai-intelligence-dashboard` or similar)
3. **Important**: Make it PUBLIC (required for free Streamlit hosting)
4. Don't initialize with README (you already have one)

#### 3. Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/ai-intelligence-dashboard.git
git branch -M main
git push -u origin main
```

#### 4. Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Click "New app"
3. Sign in with GitHub
4. Authorize Streamlit to access your repositories
5. Select your repository: `ai-intelligence-dashboard`
6. Set the main file path: `dashboard.py`
7. Click "Deploy!"

### Your Dashboard Will Be Live At:
```
https://YOUR_USERNAME-ai-intelligence-dashboard-dashboard-HASH.streamlit.app
```

---

## Option 2: Render (Alternative - FREE Tier Available)

### Prerequisites
1. GitHub account (same as above)
2. Render account (https://render.com)

### Deployment Steps
1. Push your code to GitHub (see Option 1, steps 1-3)
2. Go to https://render.com and sign up
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: ai-intelligence-dashboard
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0`
6. Click "Create Web Service"

---

## Option 3: Railway (Alternative - FREE Tier Available)

### Prerequisites
1. GitHub account
2. Railway account (https://railway.app)

### Deployment Steps
1. Push code to GitHub (see Option 1, steps 1-3)
2. Go to https://railway.app and sign up
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-detect it's a Python app
6. Add these environment variables in Settings:
   - `PORT`: 8501
7. Click "Deploy"

---

## Files Created for Deployment

I've created the following files to support web deployment:

1. **requirements.txt** - Lists all Python dependencies
   - streamlit
   - pandas
   - plotly

2. **.streamlit/config.toml** - Streamlit configuration
   - Theme settings
   - Server configuration

3. **.gitignore** - Excludes unnecessary files from Git
   - Python cache files
   - Virtual environments
   - Backup files

---

## Testing Locally Before Deployment

To test your dashboard locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run dashboard.py
```

Then open your browser to `http://localhost:8501`

---

## Troubleshooting

### Issue: "Module not found" error
**Solution**: Make sure all dependencies are in `requirements.txt`

### Issue: "File not found: data/models.json"
**Solution**: Ensure the `data/` directory and JSON files are committed to Git

### Issue: Dashboard looks different than local
**Solution**: Check `.streamlit/config.toml` for theme settings

### Issue: Deployment fails
**Solution**: Check the deployment logs for specific error messages

---

## Next Steps After Deployment

1. **Custom Domain** (Optional)
   - Streamlit Cloud allows custom domains on paid plans
   - Or use a service like Cloudflare to set up a custom domain

2. **Authentication** (Optional)
   - Add password protection using `streamlit-authenticator`
   - Or use OAuth with Google/GitHub

3. **Analytics** (Optional)
   - Add Google Analytics to track usage
   - Use Streamlit's built-in analytics (if available)

---

## Cost Comparison

| Service | Free Tier | Limitations | Best For |
|---------|-----------|-------------|----------|
| Streamlit Cloud | Yes | Public repos only | Quick, easy deployment |
| Render | Yes | 750 hrs/month | More control, private repos |
| Railway | Yes | $5 credit/month | Modern interface, good DX |
| Heroku | No* | Paid only now | Legacy projects |

*Heroku discontinued free tier in Nov 2022

---

## Support

If you encounter issues:
- Streamlit Docs: https://docs.streamlit.io/
- Streamlit Community: https://discuss.streamlit.io/
- Check deployment logs in your hosting platform

---

**Recommended**: Start with Streamlit Cloud (Option 1) - it's the fastest and easiest way to get your dashboard online!
