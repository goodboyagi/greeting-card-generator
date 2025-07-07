# GitHub Storage Setup for Persistent Stats

## 🎯 **What This Does:**
- Stores usage stats in a GitHub file (`production_stats.json`)
- Stats persist even when Render restarts
- Completely free and reliable

## 🔧 **Setup Steps:**

### 1. Create GitHub Personal Access Token
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name like "Greeting Card Stats"
4. Select scopes: `repo` (full control of private repositories)
5. Copy the token (you'll only see it once!)

### 2. Add Token to Render Environment Variables
1. Go to your [Render dashboard](https://dashboard.render.com/)
2. Select your greeting-card-generator-api service
3. Go to Environment → Environment Variables
4. Add new variable:
   - **Key**: `GITHUB_TOKEN`
   - **Value**: Your GitHub token from step 1

### 3. Deploy
The code will automatically:
- Create `production_stats.json` in your repo
- Save stats to GitHub after each request
- Load stats from GitHub when service restarts

## ✅ **Benefits:**
- **Persistent stats** - No more resetting to zero
- **Free storage** - Uses your existing GitHub repo
- **Reliable** - GitHub is very stable
- **Easy to view** - Check `production_stats.json` in your repo

## 🔍 **How It Works:**
1. When stats change → Save to GitHub file
2. When service restarts → Load from GitHub file
3. Stats accumulate over time instead of resetting

## 🚀 **Ready to Deploy!**
Just add the `GITHUB_TOKEN` environment variable and deploy! 