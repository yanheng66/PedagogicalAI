# AI-Driven SQL Learning System - Backend

A revolutionary backend system for intelligent SQL education that transforms traditional teaching from passive knowledge transfer to active, personalized learning experiences.

## 🚀 Features

### Core Capabilities
- **Intelligent SQL Analysis**: Two-stage analysis using rule-based validation and LLM-powered educational insights
- **Adaptive Learning Paths**: Personalized learning trajectories based on student performance and preferences
- **Multi-Level Hint System**: Progressive hints from conceptual guidance to detailed implementation
- **Prediction Learning Engine**: Learn by predicting query results before execution
- **Concept Mastery Tracking**: Bayesian knowledge tracking for SQL concepts
- **Learning Coin Economy**: Gamified learning incentives and resource management

### Technical Architecture
- **FastAPI**: High-performance async API framework
- **PostgreSQL**: Primary database with async SQLAlchemy ORM
- **Redis**: Caching and session management
- **Celery**: Background task processing
- **LLM Integration**: OpenAI via OpenRouter for educational analysis

## 📁 Project Structure

```
backend/
├── src/
│   ├── api/                    # FastAPI routes and endpoints
│   │   └── v1/                 # API version 1
│   │       ├── sql_analysis.py # SQL analysis endpoints
│   │       ├── students.py     # Student management
│   │       ├── learning.py     # Learning path endpoints
│   │       └── hints.py        # Hint system endpoints
│   ├── core/                   # Core business logic
│   │   └── database.py         # Database configuration
│   ├── models/                 # SQLAlchemy data models
│   │   ├── student.py          # Student entity
│   │   ├── learning_profile.py # Learning analytics
│   │   ├── query_submission.py # SQL submissions
│   │   ├── analysis_result.py  # Analysis outcomes
│   │   ├── concept.py          # SQL concepts
│   │   ├── concept_mastery.py  # Mastery tracking
│   │   ├── coin_transaction.py # Learning economy
│   │   ├── prediction_task.py  # Prediction exercises
│   │   └── hint_request.py     # Hint usage tracking
│   ├── services/               # Business services
│   │   ├── sql_analysis_service.py      # Core analysis logic
│   │   ├── learning_path_service.py     # Adaptive pathways
│   │   ├── hint_generation_service.py   # Intelligent hints
│   │   ├── student_profile_service.py   # Profile management
│   │   ├── concept_tracker.py           # Mastery tracking
│   │   ├── prediction_learning_engine.py # Prediction system
│   │   ├── coin_management_service.py   # Learning economy
│   │   ├── llm_client.py               # LLM integration
│   │   └── cache_service.py            # Caching layer
│   ├── schemas/                # Pydantic validation models
│   │   ├── sql_analysis.py     # Analysis request/response
│   │   ├── student.py          # Student schemas
│   │   ├── learning.py         # Learning schemas
│   │   ├── llm.py             # LLM integration
│   │   └── common.py          # Shared schemas
│   ├── utils/                  # Utility functions
│   │   └── logging.py         # Logging configuration
│   ├── config/                 # Configuration management
│   │   └── settings.py        # Application settings
│   └── main.py                # FastAPI application entry
├── requirements.txt           # Python dependencies
├── env.example               # Environment variables template
└── README.md                 # This file
```

## 🛠 Setup and Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- OpenRouter API key (for LLM integration)

### Installation Steps

1. **Clone and navigate to backend**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   # Create database
   createdb sql_learning_db
   
   # Run migrations (when available)
   alembic upgrade head
   ```

6. **Start services**
   ```bash
   # Start Redis
   redis-server
   
   # Start the application
   python -m src.main
   ```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/sql_learning_db
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=your-secret-key

# LLM Integration
OPENROUTER_API_KEY=your-openrouter-key
LLM_MODEL=openai/gpt-4o-mini

# Performance
CACHE_TTL_ANALYSIS=3600
RATE_LIMIT_PER_MINUTE=60
```

## 🎯 Core Services

### SQL Analysis Service
- **Quick Analysis**: Rule-based syntax and structure validation
- **Deep Analysis**: LLM-powered educational insights
- **Result Caching**: Optimized response times
- **Error Patterns**: Common mistake identification

### Learning Path Service
- **Adaptive Sequencing**: Personalized concept ordering
- **Difficulty Adjustment**: Dynamic content difficulty
- **Progress Tracking**: Comprehensive learning analytics
- **Prerequisite Management**: Concept dependency handling

### Hint Generation Service
- **Progressive Disclosure**: 4-level hint system
- **Context Awareness**: Student profile integration
- **Cost Management**: Learning coin integration
- **Effectiveness Tracking**: Hint impact measurement

### Prediction Learning Engine
- **Result Prediction**: Query outcome forecasting
- **Conceptual Reinforcement**: Knowledge strengthening
- **Misconception Detection**: Learning gap identification
- **Adaptive Feedback**: Personalized response generation

## 📊 Data Models

### Core Entities
- **Student**: Authentication and profile data
- **LearningProfile**: Analytics and preferences
- **QuerySubmission**: SQL query submissions
- **AnalysisResult**: Comprehensive analysis outcomes
- **ConceptMastery**: Bayesian knowledge tracking
- **CoinTransaction**: Learning economy management

### Key Relationships
- Student ↔ LearningProfile (1:1)
- Student ↔ QuerySubmission (1:N)
- QuerySubmission ↔ AnalysisResult (1:N)
- Student ↔ ConceptMastery (1:N)
- Student ↔ CoinTransaction (1:N)

## 🔌 API Endpoints

### SQL Analysis
- `POST /api/v1/analysis/analyze` - Analyze SQL query
- `GET /api/v1/analysis/history/{student_id}` - Analysis history
- `GET /api/v1/analysis/errors/{student_id}` - Common errors

### Learning Management
- `GET /api/v1/learning/path/{student_id}` - Learning path
- `POST /api/v1/learning/progress` - Update progress
- `GET /api/v1/learning/concepts` - Available concepts

### Hint System
- `POST /api/v1/hints/request` - Request hint
- `POST /api/v1/hints/feedback` - Provide feedback
- `GET /api/v1/hints/history/{student_id}` - Hint usage

## 🧪 Development

### Code Quality
```bash
# Format code
black src/
isort src/

# Lint
flake8 src/
mypy src/

# Test
pytest tests/
```

### Project Status
🚧 **Framework Phase**: Core architecture and service interfaces established
- ✅ Project structure and configuration
- ✅ Database models and schemas
- ✅ Service layer interfaces
- ✅ API endpoint structure
- 🔄 Service implementations (in progress)
- ⏳ Testing suite
- ⏳ Documentation completion

## 🤝 Contributing

This is a educational project framework. To contribute:

1. Implement service methods marked with `# TODO`
2. Add comprehensive tests
3. Follow established patterns and architecture
4. Maintain English-only comments and documentation

## 📝 License

This project is part of an educational initiative for AI-driven programming education.

---

**Note**: This is a framework implementation. Service methods contain TODO markers indicating where specific business logic should be implemented. 