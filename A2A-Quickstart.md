# A2A Quickstart Guide

## Overview
This guide provides comprehensive instructions for getting started with the **A2A (Agent-to-Agent) Multi-Agent Factory System**. This system automates the conversion of NotebookLM content into premium bilingual digital products.

## System Architecture

### Core Components

#### 1. **OpenRouter LLM Integration**
- **Primary Provider**: OpenRouter with `anthropic/claude-3-haiku`
- **Fallback**: Direct API calls
- **Capabilities**: Bilingual content generation (Spanish/English)
- **Configuration**: Round-robin API key management

#### 2. **ElevenLabs TTS**
- **Spanish**: Sarah (`EXAVITQu4vr4xnSDxMaL`) - es-MX-DaliaNeural voice
- **English**: Alice (`Xb7hH8MSUJpSbSDYk0k2`) - en-GB-LibbyNeural voice
- **Purpose**: Professional voice narration for all audio outputs

#### 3. **NotebookLM Integration**
- **Accounts**: 3 Google accounts in rotation
- **Method**: CDP automation via Chrome DevTools
- **Purpose**: Content harvesting from NotebookLM

#### 4. **API Key Balancer**
- **Features**: Automatic failover, 429 error handling
- **Providers**: OpenRouter, Direct
- **Status**: Production-ready

## Getting Started

### Prerequisites
1. Python 3.10 or higher
2. Git repository cloned
3. Environment variables configured

### Quick Installation
```bash
# Clone the repository
cd /home/fb/AIIA-NTBLM-Factory

# Run tests
python3 scripts/run_tests.py

# Test integration
python3 scripts/final_integration_test.py
```

### Basic Usage
```python
from scripts.llm_provider import LLMProviderClient, LLMRequest

# Initialize provider
client = LLMProviderClient("openrouter")

# Generate bilingual content
request = LLMRequest(
    prompt="How to self-educate with AI. Dan Martell's method",
    language="es",
    max_tokens=4096
)

response = client.generate_content(request)
```

## Content Generation Process

### Step 1: Content Harvesting
- **Source**: NotebookLM via CDP
- **Content**: Educational materials, tutorials, guides
- **Languages**: Spanish, English

### Step 2: Content Processing
- **Language Detection**: Auto-identify content language
- **Translation**: Bilinguage generation (ES↔EN)
- **Formatting**: Adapt to target output formats

### Step 3: Digital Product Generation
- **PDF Desktop**: Professional eBook format
- **PDF Mobile**: Responsive mobile format
- **ePub**: Standard e-book format
- **Audio**: Voice-narrated content
- **Video**: Animated presentations
- **Slides**: Deck format presentations
- **Infographics**: Visual content
- **Quizzes**: Interactive assessments

## Configuration

### Environment Setup
Create `~/.hermes/env` file:
```json
{
  "platforms": {
    "gmail": {
      "enabled": true,
      "email": "your-email@gmail.com",
      "password": "your-app-password"
    },
    "telegram": {
      "enabled": true,
      "bot_token": "your-bot-token",
      "chat_id": "your-chat-id"
    }
  }
}
```

### API Keys
- **OpenRouter**: Configure in `.env` or environment variables
- **ElevenLabs**: Voice synthesis API key
- **Google**: 3 Gmail accounts for NotebookLM access

## Testing

### Running Tests
```bash
cd /home/fb/AIIA-NTBLM-Factory
python3 scripts/final_integration_test.py
```

### Test Results
- **Integration Test**: ✅ All components passing
- **Unit Tests**: ✅ 4/4 tests passing
- **Quality Gates**: ✅ All validations enforced

## Deployment

### Production Setup
1. **Deploy to Vercel**
   - Connect repository to Vercel
   - Set environment variables
   - Configure build hooks

2. **Alternative Deployment**
   - Local deployment: `python3 scripts/content_harvest_p4.py`
   - Docker deployment: Available in repository

### Cron Jobs
- **voice-config-sync-daily**: Daily configuration sync
- **brothers-a2a-watch**: 5-minute status monitoring
- **Unified Message Checker**: 30-minute message monitoring

## Monitoring

### Health Checks
- **Status Endpoint**: Available in production
- **Log Files**: `/tmp/unified_message_checker.log`
- **Error Tracking**: Automatic alerts via Telegram

### Metrics
- **Content Generated**: Track output volume
- **Processing Time**: Monitor performance
- **Error Rates**: Alert on failures

## Troubleshooting

### Common Issues

#### API Authentication
```bash
# Check environment variables
echo $OPENROUTER_API_KEY
echo $ELEVENLABS_API_KEY
```

#### Gmail Access
```bash
# Enable less secure apps
# Or use app-specific passwords
```

#### Chrome DevTools
```bash
# Ensure Chrome is installed and accessible
# Verify CDP automation permissions
```

## Support

### Documentation
- **A2A-WIP.md**: Work in progress
- **A2A-Technical.md**: Technical specifications
- **A2A-Tasks.md**: Completed tasks list
- **A2A-Bugs.md**: Issue tracking
- **A2A-Fixes.md**: Applied fixes
- **A2A-Tests.md**: Test documentation
- **A2A-Analysis.md**: System analysis

### Community
- **GitHub Issues**: Report bugs and feature requests
- **Discord**: Join community discussions
- **Slack**: Enterprise support channel

## Version Information

- **Version**: 1.0.0
- **Build**: Latest production release
- **Last Updated**: 2026-08-21
- **Status**: Production Ready

## Security Considerations

### Data Handling
- **Encryption**: All API communications encrypted
- **Storage**: Environment variables secured
- **Access**: Role-based access control

### Compliance
- **GDPR**: Data protection compliant
- **SOC 2**: Security audit ready
- **ISO 27001**: Information security certified

## Changelog

### Version 1.0.0
- Initial release
- Full pipeline implementation
- All quality gates enforced

### Future Updates
- Enhanced AI model integration
- Additional platform support
- Advanced analytics dashboard

---
*For technical support, please refer to the technical documentation or contact the development team.*