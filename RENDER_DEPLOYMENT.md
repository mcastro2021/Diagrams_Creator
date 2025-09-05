# 🚀 Render Deployment Guide

## Quick Deploy to Render

### 1. Fork Repository
- Fork this repository to your GitHub account
- Clone your fork locally if needed

### 2. Create Render Account
- Go to [render.com](https://render.com)
- Sign up with your GitHub account
- Verify your email address

### 3. Deploy Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `diagrams-creator` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Plan**: `Starter` (free tier)

### 4. Environment Variables
Add these environment variables in Render dashboard:

#### Required
```
OPENAI_API_KEY = your_openai_api_key_here
FLASK_ENV = production
SECRET_KEY = your_secure_secret_key_here
```

#### Optional (AI Providers)
```
GROQ_API_KEY = your_groq_api_key_here
HUGGINGFACE_API_KEY = your_huggingface_api_key_here
OLLAMA_URL = http://localhost:11434
OLLAMA_MODEL = llama3.2
```

#### Application Settings
```
LOG_LEVEL = INFO
AI_TEMPERATURE = 0.7
MAX_TOKENS = 2000
AI_TIMEOUT = 30
DEFAULT_DIAGRAM_TYPE = auto
DEFAULT_DIAGRAM_STYLE = modern
ICON_CACHE_SIZE = 1000
ICON_SEARCH_LIMIT = 50
CORS_ORIGINS = *
RATE_LIMIT_PER_MINUTE = 60
MAX_FILE_SIZE = 16777216
ALLOWED_EXTENSIONS = txt,pdf,docx,doc,md,json
ENABLED_EXPORT_FORMATS = xml,svg,png,pdf
PNG_QUALITY = 95
PDF_DPI = 300
DEBUG_MODE = false
VERBOSE_LOGGING = false
TEST_MODE = false
```

### 5. Deploy
- Click **"Create Web Service"**
- Render will automatically build and deploy
- Wait for deployment to complete (usually 2-5 minutes)
- Your app will be available at: `https://your-app-name.onrender.com`

## 🎯 Features Available After Deployment

### ✅ What Works
- **AI-Powered Diagram Generation**: Create diagrams from natural language
- **1,000+ Icons**: Azure, AWS, and general infrastructure icons
- **Multiple Export Formats**: PNG, SVG, PDF, XML
- **Draw.io Integration**: Open diagrams directly in Draw.io
- **Real-time Generation**: Instant diagram creation
- **Responsive UI**: Works on desktop and mobile

### 🔧 Configuration Options
- **Multiple AI Providers**: OpenAI, Groq, Hugging Face, Ollama
- **Customizable Styles**: Modern, minimal, colorful themes
- **Flexible Architecture Types**: Auto-detection, Azure, AWS, microservices
- **File Upload Support**: Process documents (TXT, PDF, DOCX, MD, JSON)

## 🚨 Important Notes

### Free Tier Limitations
- **Sleep Mode**: App sleeps after 15 minutes of inactivity
- **Cold Start**: First request after sleep takes ~30 seconds
- **Build Time**: 90 minutes per month
- **Bandwidth**: 100GB per month

### Production Recommendations
- **Upgrade to Paid Plan**: For production use, consider upgrading
- **Custom Domain**: Add your own domain name
- **SSL Certificate**: Automatically provided by Render
- **Auto-Deploy**: Automatic deployments on git push

## 🔍 Troubleshooting

### Common Issues
1. **Build Fails**: Check Python version compatibility
2. **App Crashes**: Verify environment variables are set
3. **Slow Performance**: Consider upgrading to paid plan
4. **Icon Loading Issues**: Check network connectivity

### Support
- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **GitHub Issues**: Report bugs in this repository
- **Community**: Join Render community for help

## 🎉 Success!
Once deployed, you'll have a fully functional AI-powered diagram generator accessible from anywhere in the world!
