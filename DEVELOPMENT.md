# 🎨 Greeting Card Generator - Development Guide

## 📋 Project Overview

A full-stack AI application that generates personalized greeting cards using OpenAI's GPT-3.5-turbo model.

### 🏗️ Architecture
- **Frontend**: HTML/CSS/JavaScript (GitHub Pages)
- **Backend**: Flask API (Render)
- **AI**: OpenAI GPT-3.5-turbo
- **Analytics**: Built-in usage tracking

### 🌐 Live URLs
- **Production**: https://goodboyagi.github.io/greeting-card-generator/
- **Backend API**: https://greeting-card-generator-api.onrender.com
- **Stats Dashboard**: https://goodboyagi.github.io/greeting-card-generator/stats.html

## 🚀 Development Workflow

### Prerequisites
- Python 3.9+
- Virtual environment: `/Users/nitinsuresh/progs/my-venv/my-venv/`
- OpenAI API key in `.env` file

### Local Development Setup

#### 1. Switch to Development Mode
Edit `index.html`:
```javascript
const DEV_MODE = true;  // Change this for local testing
```

#### 2. Start Backend Server
```bash
cd backend
source /Users/nitinsuresh/progs/my-venv/my-venv/bin/activate
python app.py
```
Backend runs on: `http://localhost:5001`

#### 3. Start Frontend Server
```bash
cd /Users/nitinsuresh/progs/experiments/2025/2025/2025_06/greeting-card-generator
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
├── index.html              # Main frontend
├── stats.html              # Analytics dashboard
├── test.html               # API testing page
├── serve_local.py          # Local development server
├── render.yaml             # Render deployment config
├── backend/
│   ├── app.py              # Flask backend
│   ├── requirements.txt    # Python dependencies
│   ├── test_api.py         # API testing script
│   └── usage_stats.json    # Usage analytics (auto-generated)
└── .env                    # Environment variables (not in git)
```

## 🔧 Key Features

### Frontend Features
- Responsive design
- Form validation
- Real-time API calls
- Error handling
- Loading states

### Backend Features
- OpenAI integration
- CORS configuration
- Usage analytics
- Error handling
- Health checks

### Analytics Features
- Request tracking
- Success/failure rates
- Usage by occasion/style
- Real-time dashboard

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

### Debug Commands

```bash
# Test backend locally
curl http://localhost:5001/api/health

# Test production backend
curl https://greeting-card-generator-api.onrender.com/api/health

# Check usage stats
curl https://greeting-card-generator-api.onrender.com/api/stats
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

## 🔐 Security Notes

### Environment Variables
- **Local**: Store in `.env` file (not committed to git)
- **Production**: Set in Render dashboard
- **Never commit**: API keys or sensitive data

### CORS Configuration
- **Local**: Allows `file://` protocol and localhost
- **Production**: Allows GitHub Pages and custom domain
- **Security**: Only necessary origins are allowed

## 🚀 Future Enhancements

### Potential Features
- Card templates/designs
- Image generation with DALL-E
- Save/share functionality
- User accounts
- More occasions and styles
- Multi-language support

### Performance Optimizations
- Caching responses
- Rate limiting
- CDN for static assets
- Database for analytics

## 📞 Support

### Quick Reference
- **Local Backend**: `http://localhost:5001`
- **Local Frontend**: `http://localhost:8000`
- **Production**: https://goodboyagi.github.io/greeting-card-generator/
- **Backend API**: https://greeting-card-generator-api.onrender.com

### Development Commands
```bash
# Start local development
cd backend && source /Users/nitinsuresh/progs/my-venv/my-venv/bin/activate && python app.py
cd .. && python serve_local.py

# Deploy to production
git add . && git commit -m "Description" && git push origin main
```

---

**Last Updated**: June 21, 2025
**Version**: 1.0.0 