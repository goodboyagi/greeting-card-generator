# 🎨 Greeting Card Generator

An AI-powered greeting card generator that creates personalized cards using generative AI technology. Features both text generation with GPT-4o-mini and image generation with DALL-E 3.

## ✨ Features

- **🤖 AI Text Generation**: Personalized greeting messages using OpenAI's GPT-4o-mini
- **🎨 AI Image Generation**: Beautiful, relevant images using DALL-E 3
- **📱 Native Sharing**: Share cards via email, WhatsApp, or save to device
- **🔗 Secure Sharing**: Generate shareable links with 48-hour expiration
- **💾 Persistent Storage**: Cards stored securely in private GitHub repository
- **📊 Usage Analytics**: Track usage patterns and success rates
- **🎯 Multiple Occasions**: Birthday, Holiday, Anniversary, Wedding, and more
- **🎭 Multiple Styles**: Formal, Casual, Humorous, Romantic, and more

## 🌐 Live Demo

- **Frontend**: https://goodboyagi.github.io/greeting-card-generator/
- **Backend API**: https://greeting-card-generator-api.onrender.com
- **Stats Dashboard**: https://goodboyagi.github.io/greeting-card-generator/stats.html

## 🚀 How It Works

1. **Choose Details**: Select recipient, occasion, style, and add a personal message
2. **AI Generation**: GPT-4o-mini creates personalized text, DALL-E 3 generates relevant images
3. **Share**: Use native sharing or generate secure shareable links
4. **Viral Growth**: Recipients can view shared cards and create their own

## 🏗️ Architecture

- **Frontend**: HTML/CSS/JavaScript (GitHub Pages)
- **Backend**: Flask API (Render)
- **AI**: OpenAI GPT-4o-mini + DALL-E 3
- **Storage**: GitHub API for persistent data
- **Analytics**: Built-in usage tracking

## 🔧 Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development setup and workflow.

### Quick Start
```bash
# Clone the repository
git clone https://github.com/goodboyagi/greeting-card-generator.git
cd greeting-card-generator

# Set up environment variables
cp env.example .env
# Edit .env with your OpenAI API key and GitHub token

# Install dependencies
cd backend
pip install -r requirements.txt

# Run locally
python app.py
```

## 📱 Sharing Features

- **Native Share API**: Works on mobile devices with native sharing options
- **Secure URLs**: 48-hour expiring links for privacy
- **Persistent Storage**: Cards stored in private GitHub repository
- **No Registration**: Simple sharing without user accounts

## 🔐 Privacy & Security

- **Private Storage**: All data stored in private GitHub repositories
- **Automatic Expiration**: Shared cards automatically deleted after 48 hours
- **Secure IDs**: Cryptographically secure card identification
- **No User Data**: No personal information collected or stored

## 📊 Analytics

- **Usage Tracking**: Monitor request patterns and success rates
- **Real-time Dashboard**: Live statistics and insights
- **Performance Metrics**: Track API response times and errors

## 🎯 Use Cases

- **Personal Greetings**: Birthday, anniversary, holiday cards
- **Business Communication**: Thank you notes, congratulations
- **Event Invitations**: Wedding, graduation, party invites
- **Creative Expression**: Custom occasions and messages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- OpenAI for GPT-4o-mini and DALL-E 3 APIs
- Render for hosting the backend API
- GitHub for storage and hosting solutions

---

**Last Updated**: August 10, 2025  
**Version**: 2.0.0 - Added AI image generation, sharing system, and GitHub storage
