# 🎨 Greeting Card Generator - Development Guide

## 📋 Project Overview

A full-stack AI application that generates personalized greeting cards using OpenAI's GPT-4o-mini model and DALL-E 3 for image generation.

### 🏗️ Architecture
- **Frontend**: HTML/CSS/JavaScript (GitHub Pages)
- **Backend**: Flask API (Render)
- **AI**: OpenAI GPT-4o-mini + DALL-E 3
- **Analytics**: Built-in usage tracking
- **Storage**: GitHub API for persistent data storage

### 🌐 Live URLs
- **Production**: https://goodboyagi.github.io/greeting-card-generator/
- **Backend API**: https://greeting-card-generator-api.onrender.com
- **Stats Dashboard**: https://goodboyagi.github.io/greeting-card-generator/stats.html

## 🚀 Development Workflow

### Prerequisites
- Python 3.9+
- Virtual environment: `$VENV` (set your virtual environment path)
- OpenAI API key in `.env` file
- GitHub Personal Access Token with repo access

### Environment Setup
```bash
# Set your project directory
export PROJECT_DIR="/path/to/your/greeting-card-generator"

# Set your virtual environment path
export VENV="/path/to/your/virtual/environment"

# Example:
# export PROJECT_DIR="$HOME/projects/greeting-card-generator"
# export VENV="$HOME/venvs/my-venv"
```

### Local Development Setup

#### 1. Switch to Development Mode
Edit `index.html`:
```javascript
const DEV_MODE = true;  // Change this for local testing
const DEBUG_SHARING = true;  // Use dummy images to save DALL-E credits
```

#### 2. Start Backend Server
```bash
cd $PROJECT_DIR/backend
source $VENV/bin/activate
python app.py
```
Backend runs on: `http://localhost:5001`

#### 3. Start Frontend Server
```bash
cd $PROJECT_DIR
python serve_local.py
```
Frontend runs on: `http://localhost:8000`

#### 4. Test Locally
- Open: `http://localhost:8000/index.html`
- Test your changes
- Verify everything works

### Production Deployment

#### 1. Switch to Production Mode
Edit `index.html`:
```javascript
const DEV_MODE = false;  // Change this for production
const DEBUG_SHARING = false;  // Disable debug mode for production
```

#### 2. Deploy
```bash
git add .
git commit -m "Description of changes"
git push origin main
```

#### 3. Wait for Render (2-5 minutes)
- Render auto-deploys backend
- GitHub Pages updates frontend immediately

## 🛠️ Project Structure

```
greeting-card-generator/
├── index.html              # Main frontend with sharing functionality
├── stats.html              # Analytics dashboard
├── test.html               # API testing page
├── serve_local.py          # Local development server
├── render.yaml             # Render deployment config
├── backend/
│   ├── app.py              # Flask backend with AI integration
│   ├── requirements.txt    # Python dependencies
│   ├── test_api.py         # API testing script
│   └── usage_stats.json    # Usage analytics (auto-generated)
├── .env                    # Environment variables (not in git)
└── env.example             # Environment variables template
```

## 🔧 Key Features

### Frontend Features
- Responsive design
- Form validation
- Real-time API calls
- Error handling
- Loading states
- **Greeting card sharing with native share API**
- **Debug mode for local development (saves DALL-E credits)**

### Backend Features
- **OpenAI GPT-4o-mini integration for text generation**
- **DALL-E 3 integration for image generation**
- **Secure sharing system with 48-hour expiration**
- **GitHub storage for persistent shared card data**
- CORS configuration
- Usage analytics
- Error handling
- Health checks

### Analytics Features
- Request tracking
- Success/failure rates
- Usage by occasion/style
- Real-time dashboard
- **GitHub-based persistent storage**

### Sharing Features
- **Native Web Share API integration**
- **Secure shareable URLs with 48-hour expiration**
- **Persistent storage in private GitHub repository**
- **Automatic cleanup of expired cards**
- **Viral growth: recipients can create their own cards**

## 🎯 Adding New Features

### 1. Backend Changes
1. Edit `backend/app.py`
2. Test locally with Flask server
3. Commit and push
4. Wait for Render deployment

### 2. Frontend Changes
1. Edit `index.html`
2. Test locally with `serve_local.py`
3. Commit and push
4. GitHub Pages updates immediately

### 3. New Dependencies
1. Add to `backend/requirements.txt`
2. Test locally
3. Commit and push
4. Render will install new dependencies

## 🔍 Troubleshooting

### Common Issues

#### CORS Errors
- **Problem**: "Access to fetch blocked by CORS policy"
- **Solution**: Use `serve_local.py` instead of double-clicking HTML file

#### Backend Not Starting
- **Problem**: "Module not found" errors
- **Solution**: Activate virtual environment first
- **Solution**: Install missing packages: `pip install -r backend/requirements.txt`

#### Render Deployment Fails
- **Problem**: Build errors
- **Solution**: Check Render logs
- **Solution**: Test locally first

#### API Key Issues
- **Problem**: "OpenAI API key not configured"
- **Solution**: Check `.env` file exists and has correct format
- **Solution**: Verify API key in Render environment variables

#### GitHub Storage Issues
- **Problem**: Shared cards not persisting
- **Solution**: Check GitHub token has repo access to both repositories
- **Solution**: Verify `greeting-card-storage` repo exists and is private

#### Sharing Issues
- **Problem**: Share button stuck on "Preparing..."
- **Solution**: Check browser console for errors
- **Solution**: Verify native share API is supported
- **Solution**: Test with different browsers/devices

### Debug Commands

```bash
# Test backend locally
curl http://localhost:5001/api/health

# Test production backend
curl https://greeting-card-generator-api.onrender.com/api/health

# Check usage stats
curl https://greeting-card-generator-api.onrender.com/api/stats

# Debug shared cards (local only)
curl http://localhost:5001/api/debug/shared-cards
```

## 📊 Monitoring

### Usage Statistics
- **Dashboard**: https://goodboyagi.github.io/greeting-card-generator/stats.html
- **API Endpoint**: `/api/stats`
- **Auto-refresh**: Every 30 seconds

### Render Monitoring
- **Dashboard**: https://dashboard.render.com/
- **Logs**: Available in Render dashboard
- **Metrics**: Request count, response times

### GitHub Storage Monitoring
- **Stats Repository**: `goodboyagi/greeting-card-generator` (usage statistics)
- **Storage Repository**: `goodboyagi/greeting-card-storage` (shared cards)
- **Auto-cleanup**: Expired cards removed after 48 hours

## 🔐 Security Notes

### Environment Variables
- **Local**: Store in `.env` file (not committed to git)
- **Production**: Set in Render dashboard
- **Never commit**: API keys or sensitive data

### GitHub Configuration
- **Stats Storage**: `GITHUB_TOKEN`, `GITHUB_REPO`, `GITHUB_STATS_FILE`
- **Shared Cards Storage**: `GITHUB_STORAGE_REPO`, `GITHUB_SHARED_CARDS_FILE`
- **Token Permissions**: Requires `repo` scope for both repositories

### CORS Configuration
- **Local**: Allows `file://` protocol and localhost
- **Production**: Allows GitHub Pages and custom domain
- **Security**: Only necessary origins are allowed

### Sharing Security
- **Card IDs**: Cryptographically secure random generation
- **Expiration**: Automatic 48-hour cleanup
- **Access Control**: No password required, but cards expire automatically

## 🚀 Future Enhancements

### Potential Features
- **Card templates/designs** (partially implemented with DALL-E 3)
- **Advanced image generation** with style controls
- **Save/share functionality** (✅ implemented)
- **User accounts**
- **More occasions and styles**
- **Multi-language support**
- **Card analytics and tracking**

### Performance Optimizations
- **Caching responses** (✅ implemented for shared cards)
- **Rate limiting**
- **CDN for static assets**
- **Database for analytics** (✅ GitHub storage implemented)

## 📞 Support

### Quick Reference
- **Local Backend**: `http://localhost:5001`
- **Local Frontend**: `http://localhost:8000`
- **Production**: https://goodboyagi.github.io/greeting-card-generator/
- **Backend API**: https://greeting-card-generator-api.onrender.com
- **GitHub Storage**: `goodboyagi/greeting-card-storage`

### Development Commands
```bash
# Set environment variables first
export PROJECT_DIR="/path/to/your/greeting-card-generator"
export VENV="/path/to/your/virtual/environment"

# Start local development
cd $PROJECT_DIR/backend && source $VENV/bin/activate && python app.py
cd $PROJECT_DIR && python serve_local.py

# Deploy to production
git add . && git commit -m "Description" && git push origin main
```

### Debug Mode
- **Local Development**: Set `DEBUG_SHARING = true` to use dummy images
- **Production**: Automatically disabled to ensure real content
- **DALL-E Credits**: Save during development by using debug mode

---

**Last Updated**: August 10, 2025
**Version**: 2.0.0 - Added AI image generation, sharing system, and GitHub storage 