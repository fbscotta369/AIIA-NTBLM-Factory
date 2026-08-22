# A2A Quickstart Guide — AIIA-NTBLM-Factory

**Version:** 2.0  
**Last Updated:** 2026-08-22 UTC  
**Status:** Production Ready  
**Target Audience:** New users, developers, integrators

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Basic Usage](#basic-usage)
5. [API Integration](#api-integration)
6. [Common Tasks](#common-tasks)
7. [Troubleshooting](#troubleshooting)
8. [Support](#support)

---

## System Overview

### What is AIIA-NTBLM-Factory?

**AIIA-NTBLM-Factory** is an intelligent multi-agent system that transforms content (videos, articles, notes) into professional digital products in 8 formats:

- 📄 **PDF** (Desktop & Mobile)
- 📚 **ePub** (E-reader compatible)
- 🎵 **Audio** (Professional narration)
- 🎬 **Video** (Animated presentations)
- 📊 **Slides** (Presentation decks)
- 🎨 **Infographics** (Visual summaries)
- 📝 **Quizzes** (Interactive assessments)
- 💾 **Complete Bundles** (All formats)

### Key Features

✅ **Bilingual Support** — Spanish (es-MX) and English (en-GB)  
✅ **AI-Powered Processing** — Multi-agent architecture with OpenRouter LLM  
✅ **Automated Quality Control** — Built-in validation and verification  
✅ **Instant Delivery** — CDN-backed downloads  
✅ **API-First Design** — Integrate anywhere  
✅ **White-Label Ready** — Custom branding available  

---

## Prerequisites

### System Requirements
- **Python**: 3.10+ (for self-hosted)
- **Node.js**: 18+ (for dashboard)
- **Docker**: 20.10+ (recommended)
- **RAM**: 8GB minimum (16GB recommended)
- **Disk**: 50GB free space

### Required Accounts
1. **OpenRouter API Key** — For LLM processing
2. **ElevenLabs API Key** — For voice synthesis
3. **Google Account** — For NotebookLM integration (3 accounts recommended)
4. **Cloud Storage** — AWS S3, GCS, or similar

### Environment Variables
```bash
# LLM
OPENROUTER_API_KEY="sk-or-..."
OPENROUTER_MODEL="anthropic/claude-3-haiku"

# TTS
ELEVENLABS_API_KEY="sk_..."
ELEVENLABS_VOICE_SARAH="EXAVITQu4vr4xnSDxMaL"  # Spanish
ELEVENLABS_VOICE_ALICE="Xb7hH8MSUJpSbSDYk0k2"   # English

# Storage
AWS_ACCESS_KEY_ID="AKIA..."
AWS_SECRET_ACCESS_KEY="..."
AWS_S3_BUCKET="aiia-products"

# Webhook (optional)
WEBHOOK_URL="https://your-app.com/webhook"
WEBHOOK_SECRET="your-secret"
```

---

## Installation

### Option 1: Local Installation (Development)

```bash
# Clone repository
git clone https://github.com/fbscotta369/AIIA-NTBLM-Factory.git
cd AIIA-NTBLM-Factory

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run tests
python3 scripts/final_integration_test.py

# Start API server
python3 scripts/api_server.py
# Server runs on http://localhost:8000
```

### Option 2: Docker Deployment

```bash
# Build Docker image
docker build -t aiia-factory:latest .

# Run container
docker run -d \
  --name aiia-factory \
  -e OPENROUTER_API_KEY="sk-or-..." \
  -e ELEVENLABS_API_KEY="sk_..." \
  -p 8000:8000 \
  aiia-factory:latest

# Check logs
docker logs -f aiia-factory

# API available at http://localhost:8000
```

### Option 3: Cloud Deployment (Vercel)

```bash
# Deploy to Vercel
vercel deploy

# Configure environment variables in Vercel dashboard
# https://vercel.com/settings/environment-variables

# View deployed app
# https://aiia-factory-<your-team>.vercel.app
```

---

## Basic Usage

### Web Dashboard

1. **Sign Up**
   ```
   Visit: https://dashboard.aiia-factory.com
   Click: "Sign Up"
   Enter: Email and password
   Create: Account
   ```

2. **Add Content Source**
   ```
   Click: "New Project"
   Select: Content type (YouTube, NotebookLM, Document)
   Paste: URL or upload file
   ```

3. **Configure Output**
   ```
   Select: Desired formats (PDF, ePub, Audio, etc.)
   Choose: Language (Spanish/English)
   Set: Custom options (branding, styling)
   ```

4. **Generate**
   ```
   Click: "Generate Products"
   Monitor: Progress bar
   Download: When complete (email notification)
   ```

### Command Line Interface

```bash
# List available commands
python3 scripts/content_harvest_p4.py --help

# Generate content from URL
python3 scripts/content_harvest_p4.py \
  --topic "AI Self-Education" \
  --languages es en \
  --formats pdf epub audio \
  --output-dir outputs/my_project

# Monitor progress
python3 scripts/content_harvest_p4.py --status <job_id>

# Download results
python3 scripts/content_harvest_p4.py --download <job_id>
```

---

## API Integration

### Authentication

All API requests require an API key in the Authorization header:

```bash
Authorization: Bearer sk_live_xxxxxxxxxxxxx
```

### Example: Generate Content via API

```bash
curl -X POST https://api.aiia-factory.com/v1/process \
  -H "Authorization: Bearer sk_live_xxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "content_url": "https://youtube.com/watch?v=...",
    "formats": ["pdf", "epub", "audio", "video"],
    "languages": ["es", "en"],
    "webhook_url": "https://your-app.com/webhook"
  }'

# Response:
# {
#   "job_id": "job_1234567890",
#   "status": "processing",
#   "estimated_completion": "2026-08-22T15:30:00Z"
# }
```

### Polling for Status

```bash
curl -X GET https://api.aiia-factory.com/v1/status/job_1234567890 \
  -H "Authorization: Bearer sk_live_xxxxxxxxxxxxx"

# Response:
# {
#   "job_id": "job_1234567890",
#   "status": "completed",
#   "results": {
#     "pdf": "https://cdn.aiia-factory.com/outputs/job_1234567890/document.pdf",
#     "epub": "https://cdn.aiia-factory.com/outputs/job_1234567890/document.epub",
#     "audio_es": "https://cdn.aiia-factory.com/outputs/job_1234567890/narration_es.mp3",
#     "audio_en": "https://cdn.aiia-factory.com/outputs/job_1234567890/narration_en.mp3"
#   }
# }
```

### Webhook Notifications

Configure webhook URL in dashboard settings. Receives POST requests:

```json
{
  "event": "job.completed",
  "job_id": "job_1234567890",
  "status": "completed",
  "timestamp": "2026-08-22T15:30:00Z",
  "results": {
    "pdf": "https://cdn.aiia-factory.com/outputs/...",
    "epub": "https://cdn.aiia-factory.com/outputs/...",
    "audio_es": "https://cdn.aiia-factory.com/outputs/..."
  }
}
```

---

## Common Tasks

### Task 1: Generate PDF from YouTube Video

```bash
# Method 1: Dashboard
1. Go to Dashboard
2. Click "New Project"
3. Select "YouTube"
4. Paste video URL
5. Select "PDF (Desktop + Mobile)"
6. Click "Generate"

# Method 2: API
curl -X POST https://api.aiia-factory.com/v1/process \
  -H "Authorization: Bearer sk_live_xxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "content_url": "https://youtube.com/watch?v=...",
    "formats": ["pdf_desktop", "pdf_mobile"],
    "languages": ["en"]
  }'
```

### Task 2: Create Complete Course Bundle

```bash
python3 scripts/content_harvest_p4.py \
  --topic "Machine Learning Basics" \
  --languages es en \
  --formats pdf epub audio video slides quiz infographic \
  --output-dir outputs/ml_course
```

### Task 3: Generate Audio in Both Languages

```bash
curl -X POST https://api.aiia-factory.com/v1/process \
  -H "Authorization: Bearer sk_live_xxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "content_url": "https://example.com/article",
    "formats": ["audio"],
    "languages": ["es", "en"],
    "voice_spanish": "Sarah",
    "voice_english": "Alice"
  }'
```

### Task 4: Batch Process Multiple Items

```bash
# Create batch.json
[
  {
    "url": "https://youtube.com/watch?v=...",
    "formats": ["pdf", "audio"],
    "name": "Video 1"
  },
  {
    "url": "https://example.com/article2",
    "formats": ["pdf", "epub"],
    "name": "Article 2"
  }
]

# Process batch
python3 scripts/batch_processor.py --file batch.json
```

---

## Troubleshooting

### Issue: API Key Invalid

**Error**: `401 Unauthorized`

**Solution**:
1. Check API key format: `sk_live_xxxxx` or `sk_test_xxxxx`
2. Verify key is not expired (check dashboard)
3. Ensure key has correct permissions (Admin scope)
4. Try regenerating key in settings

### Issue: Slow Processing

**Symptoms**: Processing takes >30 minutes

**Causes & Solutions**:
1. **Large files**: Expected for video/audio content
2. **High queue**: System busy (typical during peak hours)
3. **Network issues**: Check internet connection
4. **Action**: Check status via API or dashboard

### Issue: Audio Generation Fails

**Error**: `TTS Service Unavailable`

**Solutions**:
1. Check ElevenLabs API key validity
2. Verify account has remaining quota
3. Try different voice or language
4. Contact support if persistent

### Issue: PDF Generation Incomplete

**Error**: `PDF missing content or formatting`

**Solutions**:
1. Verify source content is accessible
2. Try with smaller content first
3. Check output format options (mobile vs desktop)
4. Review quality gates in settings

### Issue: Storage Limits Exceeded

**Error**: `Storage quota exceeded`

**Solutions**:
1. Upgrade subscription tier
2. Delete old projects (30+ days old)
3. Archive completed projects
4. Enable automatic cleanup (settings)

---

## Performance Tips

### For Faster Generation
- ✅ Use smaller content sources initially
- ✅ Generate PDF first (fastest format)
- ✅ Avoid large videos (15+ minutes)
- ✅ Use API for batch processing

### For Better Quality
- ✅ Provide clear, well-structured content
- ✅ Include high-resolution images
- ✅ Use standard fonts and formatting
- ✅ Review and approve preview before final generation

### For Cost Optimization
- ✅ Use annual billing (20% discount)
- ✅ Batch multiple items together
- ✅ Reuse generated templates
- ✅ Enable aggressive caching (settings)

---

## Support

### Documentation
- **Full API Reference**: https://docs.aiia-factory.com
- **GitHub Repo**: https://github.com/fbscotta369/AIIA-NTBLM-Factory
- **Blog & Tutorials**: https://blog.aiia-factory.com

### Getting Help
| Issue Type | Channel | Response Time |
|------------|---------|----------------|
| Account issues | support@aiia-factory.com | 2 hours |
| Technical support | support+tech@aiia-factory.com | 4 hours |
| Billing questions | support+billing@aiia-factory.com | 24 hours |
| Emergency/Urgent | +1-555-AIIA-911 | 30 minutes |

### Community
- **Discord Server**: https://discord.gg/aiia-factory
- **GitHub Issues**: https://github.com/fbscotta369/AIIA-NTBLM-Factory/issues
- **Twitter**: @aiia_factory

---

## Next Steps

1. **Create Account** → https://dashboard.aiia-factory.com
2. **Configure API Keys** → Dashboard Settings
3. **Try First Generation** → Use sample project
4. **Review Documentation** → Full API docs
5. **Join Community** → Discord server
6. **Integrate API** → Production setup
7. **Scale Usage** → Upgrade tier as needed

---

**Quick Start Complete! 🚀**

Ready to generate amazing digital products? Start with a free trial today!

**Version**: 2.0  
**Last Updated**: 2026-08-22 UTC  
**Status**: ✅ Production Ready
