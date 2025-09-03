# PDF RAG System - Netlify Deployment

This is a Netlify-compatible version of the PDF RAG system using Netlify Functions.

## 🚀 Quick Deploy to Netlify

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/krishna-droidmax/Semantic-Search-QA-Over-Policy-Documentation)

## 📁 Project Structure

```
├── netlify/
│   ├── functions/
│   │   ├── upload-pdf.js    # PDF upload handler
│   │   └── query-pdf.js     # Query processing handler
│   └── netlify.toml         # Netlify configuration
├── dist/
│   └── index.html           # Static frontend
├── package.json             # Dependencies
└── README_NETLIFY.md        # This file
```

## 🔧 Environment Variables

Set these in your Netlify dashboard under Site Settings > Environment Variables:

```
PPLX_API_KEY=your_perplexity_api_key_here
```

## 🛠️ Local Development

1. Install dependencies:
```bash
npm install
```

2. Install Netlify CLI:
```bash
npm install -g netlify-cli
```

3. Start local development server:
```bash
netlify dev
```

## 📝 Features

- ✅ PDF upload and processing
- ✅ Semantic search with embeddings
- ✅ Question answering with AI
- ✅ Modern responsive UI
- ✅ Netlify Functions integration

## ⚠️ Limitations

This Netlify version has some limitations compared to the full Node.js version:

- **File Storage**: Uses in-memory storage (files are lost on function restart)
- **Processing**: Simplified PDF processing for demo purposes
- **Performance**: Limited by Netlify Functions timeout (10 seconds)
- **Memory**: Limited by Netlify Functions memory constraints

## 🔄 Full Version

For production use with full functionality, deploy the Node.js version to:
- **Vercel** (recommended for Node.js apps)
- **Railway** (great for full-stack apps)
- **Heroku** (classic platform)
- **DigitalOcean App Platform**
- **AWS Lambda** (with proper setup)

## 🚀 Deployment Steps

1. **Fork this repository**
2. **Connect to Netlify**:
   - Go to [Netlify](https://netlify.com)
   - Click "New site from Git"
   - Connect your GitHub account
   - Select this repository

3. **Configure build settings**:
   - Build command: `npm run build`
   - Publish directory: `dist`
   - Functions directory: `netlify/functions`

4. **Set environment variables**:
   - Add your Perplexity API key in Site Settings

5. **Deploy!**

## 🎯 Usage

1. Visit your deployed Netlify site
2. Upload a PDF file
3. Ask questions about the content
4. Get AI-powered answers with sources

## 📞 Support

If you encounter issues:
1. Check the Netlify function logs
2. Verify environment variables are set
3. Ensure your Perplexity API key is valid
4. Check the browser console for errors

## 🔗 Links

- [Full Node.js Version](../README.md)
- [GitHub Repository](https://github.com/krishna-droidmax/Semantic-Search-QA-Over-Policy-Documentation)
- [Netlify Documentation](https://docs.netlify.com/)
