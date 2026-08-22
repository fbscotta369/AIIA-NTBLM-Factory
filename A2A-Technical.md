# A2A Technical Documentation

## System Overview

### Core Architecture

#### A2A Protocol
The A2A (Agent-to-Agent) protocol defines the operating contract for this multi-agent factory system. Key principles include:

- **Autonomy First**: Continue working without permission when next steps are obvious and safe
- **Verification First**: Never claim success without real checks
- **Source First**: Read live repo files, not memory
- **Single-Owner State**: Keep progress in files, not in chat
- **No Assumption Mode**: If UI, API, or build state is not verified, it is unknown

#### Execution Order (Mandatory)

Every agent must follow this sequence:

1. **Read** the repo state and relevant handoff docs
2. **Discover** current live behavior
3. **Plan** the smallest useful sequence
4. **Execute** the first step
5. **Verify** immediately
6. **Persist** in the repo
7. **Repeat** until done
8. **Handoff** with concrete next action or completion

### System Components

#### 1. **LLM Integration**
- **Provider**: OpenRouter with `anthropic/claude-3-haiku`
- **Fallback**: Direct API calls for redundancy
- **Language Support**: Spanish (es-MX) and English (en-GB)
- **Voice Synthesis**: ElevenLabs with Sarah (ES) and Alice (EN) voices

#### 2. **NotebookLM Integration**
- **Method**: Chrome DevTools Protocol (CDP) automation
- **Accounts**: 3 Google accounts in round-robin rotation
- **Purpose**: Content harvesting from NotebookLM sources

#### 3. **API Management**
- **Balancer**: Automatic failover on 429 errors
- **Providers**: OpenRouter, Direct, and other sources
- **Key Management**: Secure credential rotation

#### 4. **Message Monitoring**
- **Platforms**: Gmail, Telegram, WhatsApp, LinkedIn
- **Frequency**: 30-minute intervals
- **Notification**: Only when new messages detected

### Technical Specifications

#### Environment Requirements
```bash
# Python Version
python3 >= 3.10

# Dependencies
pip install -r requirements.txt

# Environment Variables
export OPENROUTER_API_KEY="your-key"
export ELEVENLABS_API_KEY="your-key"
export GOOGLE_CREDENTIALS="path/to/creds"
```

#### Directory Structure
```
/home/fb/AIIA-NTBLM-Factory/
├── .aiia/                           # AIIA configuration
│   └── factory.manifest.json
├── scripts/                        # Automation scripts
│   ├── llm_provider.py             # LLM integration
│   ├── tts_provider.py            # TTS integration
│   ├── notebooklm_browser.py      # NotebookLM automation
│   ├── content_harvest_p1.py       # Content harvesting
│   ├── content_harvest_p2.py       # Content processing
│   ├── content_harvest_p3.py       # Content generation
│   ├── content_harvest_p4.py       # Pipeline orchestration
│   └── engines/                    # Engine implementations
│       ├── api_key_balancer.py     # API management
│       ├── auto_healing_engine.py  # System recovery
│       ├── bidirectional_sync_engine.py # Sync operations
│       └── rate_limit_free_failover.py # Failover handling
├── skills/                         # Hermes Agent skills
│   └── notebooklm-integration/    # NotebookLM integration skill
├── outputs/                        # Generated products
│   ├── pdf/                       # PDF outputs
│   ├── audio/                     # Audio outputs
│   ├── video/                     # Video outputs
│   └── logs/                      # Output logs
└── docs/                           # Documentation
    ├── A2A-Quickstart.md
    ├── A2A-Technical.md
    ├── A2A-Tasks.md
    ├── A2A-Bugs.md
    ├── A2A-Fixes.md
    ├── A2A-Tests.md
    ├── A2A-Analysis.md
    └── A2A-WHAT.md
```

#### Data Flow

1. **Input**: NotebookLM content harvesting
2. **Processing**: Language detection and translation
3. **Generation**: LLM content creation
4. **Synthesis**: TTS voice generation
5. **Distribution**: Multi-format output production

### Configuration Details

#### Output Configuration
```yaml
output:
  formats:
    - desktop_pdf          # Professional eBook format
    - mobile_pdf          # Responsive mobile format
    - epub               # Standard e-book format
    - audio              # Voice-narrated content
    - video              # Animated presentations
    - slides            # Deck format
    - infographics      # Visual content
    - quizzes            # Interactive assessments

  languages:
    - es-LATAM          # Spanish with female voice
    - en-UK             # English with female voice

  quality:
    visual_qa_checklist: true
    typecheck: true
    content_structure_test: true
    build_verification: true
```

#### Language Configuration
```yaml
language_config:
  es-MX:
    voice: es-MX-DaliaNeural
    provider: elevenlabs
    gender: female

  en-GB:
    voice: en-GB-LibbyNeural
    provider: elevenlabs
    gender: female
```

### Quality Assurance

#### Visual QA Checklist
- Hero section visible above fold without scroll
- CTA visible and clickable in hero
- All text legible on target device resolution
- Modal text legible (not cut off)
- No content overflow / clipping
- No missing text / missing sections
- Spacing, padding, size hierarchy within 10% tolerance

#### Verification Commands
- `typecheck` - Type checking
- `content_structure_test` - Content structure validation
- `build_verification` - Build verification

### Performance Metrics

#### Response Times
- **LLM Generation**: < 5 seconds
- **TTS Synthesis**: < 2 seconds
- **Content Processing**: < 10 seconds
- **Quality Validation**: < 3 seconds

#### Throughput
- **Concurrent Users**: 10+
- **Content per Hour**: 100+ items
- **CPU Usage**: < 80%
- **Memory Usage**: < 2GB

### Security Specifications

#### Authentication
```yaml
auth:
  jwt_secret: "${JWT_SECRET}"
  api_key_rotation: "true"
  session_timeout: "24h"
  mfa_required: "true"
```

#### Encryption
- **TLS 1.3**: All API communications
- **AES-256**: Data at rest encryption
- **RSA-4096**: Key exchange

### API Endpoints

#### Internal APIs
```http
# LLM Service
POST /api/llm/generate
Content-Type: application/json
Authorization: Bearer ${OPENROUTER_TOKEN}

# TTS Service
POST /api/tts/synthesize
Content-Type: application/json
Authorization: Bearer ${ELEVENLABS_TOKEN}

# NotebookLM Service
GET /api/notebooklm/content
Authorization: Bearer ${GOOGLE_TOKEN}
```

### Monitoring and Logging

#### Log Formats
```json
{
  "timestamp": "2026-08-21T12:30:00Z",
  "level": "INFO",
  "service": "llm_provider",
  "message": "Content generated successfully",
  "metadata": {
    "user_id": "123",
    "content_type": "educational",
    "language": "es"
  }
}
```

#### Metrics Collection
- **Application Metrics**: HTTP requests, response times
- **Business Metrics**: Content generation volume, user engagement
- **System Metrics**: CPU, memory, disk usage
- **Error Metrics**: Error rates, failure patterns

### Error Handling

#### Error Codes
```yaml
errors:
  1XXX: "Authentication Errors"
  2XXX: "Validation Errors"
  3XXX: "Processing Errors"
  4XXX: "External Service Errors"
  5XXX: "System Errors"
```

#### Retry Logic
- **Max Retries**: 3 per operation
- **Exponential Backoff**: 1s, 2s, 4s
- **Circuit Breaker**: 5 consecutive failures → pause 5 minutes

### Integration Points

#### A2A Compliance
```yaml
a2a:
  solo_mode:
    independent_operation: true
    clear_entry_points: true
    exit_criteria: true

  team_mode:
    coordination: true
    handoff_protocol: true
    verification_gates: true
```

#### Related Skills
- **369x-Auto-Improvement-Engine**: Continuous optimization
- **API-Key-Balancer**: API key management
- **Auto-Healing-Engine**: Fault tolerance
- **Bidirectional-Sync-Engine**: Sync operations
- **Cross-Session-Insight-Distiller**: Insight extraction
- **Gateway-Online-Notifier**: Notifications
- **Gateway-Self-Healing**: Recovery
- **Rate-Limit-Free-Failover**: Failover
- **Battery-Telegram-Alert**: Alerting
- **Top-Skills-Collection**: Skill curation

### Deployment Specifications

#### Environment Variables
```bash
# Production
OPENROUTER_API_KEY="prod-key"
ELEVENLABS_API_KEY="prod-key"
GOOGLE_CREDENTIALS_FILE="/etc/secrets/google-creds.json"

# Testing
OPENROUTER_API_KEY="test-key"
ELEVENLABS_API_KEY="test-key"
GOOGLE_CREDENTIALS_FILE="/tmp/test-creds.json"
```

#### Docker Configuration
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "scripts/final_integration_test.py"]
```

#### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: a2a-factory
  labels:
    app: a2a-factory
spec:
  replicas: 3
  selector:
    matchLabels:
      app: a2a-factory
  template:
    metadata:
      labels:
        app: a2a-factory
    spec:
      containers:
      - name: a2a-factory
        image: a2a-factory:latest
        ports:
        - containerPort: 8080
        env:
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: a2a-secrets
              key: openrouter-key
```

### Monitoring Configuration

#### Health Checks
```yaml
health_checks:
  llm_service:
    endpoint: "/health"
    expected_status: 200
    timeout: 5s

  tts_service:
    endpoint: "/health"
    expected_status: 200
    timeout: 5s

  notebooklm_service:
    endpoint: "/health"
    expected_status: 200
    timeout: 5s
```

#### Alerting
```yaml
alerts:
  high_error_rate:
    condition: "error_rate > 5%"
    notification: "telegram"
    urgency: "high"

  high_latency:
    condition: "response_time > 10s"
    notification: "email"
    urgency: "medium"
```

### Compliance and Standards

#### Security Standards
- **ISO 27001**: Information Security Management
- **SOC 2**: Security, Availability, Confidentiality
- **GDPR**: Data Protection Regulation
- **PCI DSS**: Payment Card Industry Security

#### Development Standards
- **Git Flow**: Feature branches, pull requests, CI/CD
- **Code Quality**: Type checking, linting, testing
- **Documentation**: Comprehensive API and user docs
- **Testing**: Unit tests, integration tests, end-to-end tests

### Troubleshooting Guide

#### Common Issues and Solutions

**Issue**: API authentication failures
**Solution**: 
1. Verify API keys are correct
2. Check key rotation schedule
3. Ensure proper environment configuration

**Issue**: Gmail access problems
**Solution**:
1. Enable less secure apps or use app-specific passwords
2. Verify Gmail account permissions
3. Check IMAP settings

**Issue**: Chrome DevTools automation failures
**Solution**:
1. Ensure Chrome is installed and accessible
2. Verify CDP permissions
3. Check automation configuration

### Performance Optimization

#### Scaling Strategies
- **Horizontal Scaling**: Multiple instances behind load balancer
- **Vertical Scaling**: Increase CPU/memory resources
- **Database Optimization**: Query optimization, indexing
- **Cache Optimization**: Redis for frequently accessed data

#### Monitoring Tools
- **Prometheus**: Metrics collection
- **Grafana**: Visualization and alerts
- **ELK Stack**: Log aggregation and analysis

### Future Enhancements

#### Planned Features
1. **Enhanced AI Models**: Integration with new LLM providers
2. **Advanced Analytics**: Real-time performance dashboards
3. **Multi-language Support**: Additional languages and voices
4. **Enterprise Features**: Advanced security and compliance
5. **Mobile Integration**: Native mobile applications

#### Research Areas
- **Prompt Engineering**: Advanced content generation techniques
- **Model Optimization**: Performance improvements
- **User Personalization**: Tailored content recommendations
- **Quality Assurance**: Automated content validation

---
*Document Version: 1.0.0*
*Last Updated: 2026-08-21*
*Next Review: 2026-09-21*