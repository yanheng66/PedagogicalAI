# PedagogicalAI: Intelligent SQL Learning Platform

An AI-powered adaptive learning platform designed to teach SQL concepts through personalized, multi-step pedagogical approaches. The system uses advanced AI agents to provide tailored analogies, interactive challenges, and comprehensive learning analytics.

## Project Overview

PedagogicalAI is a sophisticated educational platform that transforms SQL learning through:

- **Adaptive AI Teaching**: Personalized analogies and explanations based on student understanding
- **Comprehensive Analytics**: Real-time learning progress tracking and performance analysis
- **Interactive Learning**: Gamified lessons with XP, medals, and progressive challenges
- **Intelligent Assessment**: Multi-dimensional evaluation of student queries and explanations
- **Performance Monitoring**: Advanced metrics tracking for both students and instructors

## Team Members
- **[Yanheng Jiang]** - Project Lead
- **[Zizhao Wang]** - Database Design & Backend Architecture
- **[Xueyi Xie]** - Frontend Development & UI/UX Design
- **[Yanheng Jiang]** - AI Integration, & Performance Optimization


## Project Architecture

### Frontend (React)
```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── AIChatScene.jsx     # AI interaction interface
│   │   ├── ChallengeComponent.jsx  # Step 4 coding challenges
│   │   ├── MCQComponent.jsx     # Multiple choice questions
│   │   ├── TaskComponent.jsx    # SQL writing tasks
│   │   └── PerformanceDashboard.jsx  # Analytics dashboard
│   ├── pages/               # Main application pages
│   │   ├── HomePage.js         # Course overview
│   │   ├── LessonPage.js       # 5-step learning process
│   │   ├── AuthPage.js         # User authentication
│   │   └── CurriculumPage.js   # Course catalog
│   ├── utils/               # Utility functions
│   │   ├── lessonContent.js    # API integration
│   │   ├── userProgress.js     # Progress tracking
│   │   └── performanceMonitor.js  # Performance analytics
│   └── data/                # Static data and configurations
```

### Backend (FastAPI + Python)
```
backend/
├── api_server_enhanced.py   # Main FastAPI application
├── controllers/
│   └── enhanced_teaching_controller.py  # Core teaching logic
├── services/
│   ├── ai_service.py        # OpenAI integration
│   ├── grading_service.py   # Automated assessment
│   ├── firestore_service.py # Database operations
│   └── student_tracker.py   # Learning analytics
├── models/
│   ├── user_profile.py      # Student data models
│   ├── db_models.py         # Database schemas
│   └── concept_mastery.py   # Mastery tracking
└── utils/                   # Helper utilities
```

### Database Architecture
- **Primary**: Google Firestore (NoSQL) for all data storage and real-time synchronization
- **Authentication**: Firebase Authentication for user management
- **Storage**: Firebase Storage for file uploads (if applicable)
- **Caching**: In-memory caching for performance optimization

## Setup Instructions

### Prerequisites
- **Node.js** (v16 or higher)
- **Python** (3.9 or higher)
- **npm** or **yarn**
- **Google Firebase Account** (for Firestore)

### 1. Clone the Repository
```bash
git clone https://github.com/yanheng66/PedagogicalAI.git
cd PedagogicalAI
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment Variables
Create a `.env` file in the root directory:
```env
# OpenAI Configuration
OPENAI_API_KEY=<api key>

# Firebase Configuration
FIREBASE_PROJECT_ID=<firebase_project_id>
FIREBASE_PRIVATE_KEY=<firebase_private_key>
FIREBASE_CLIENT_EMAIL=<firebase_client_email>

# API Configuration
REACT_APP_API_URL=http://localhost:8000 #if run locally 
```

#### Firebase Setup
1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Firestore Database
3. Enable Firebase Authentication (if using authentication features)
4. Download the service account key JSON file
5. Place it in the project root as `firebase-service-account.json`

#### Start the Backend Server
```bash
uvicorn api_server_enhanced:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup

#### Navigate to Frontend Directory
```bash
cd frontend
```

#### Install Dependencies
```bash
npm install
```

#### Start the Development Server
```bash
npm start
```

The application will open at `http://localhost:3000`

## How It Works: The 5-Step Learning Process

### Step 1: Concept Introduction
- AI generates personalized analogies based on student background
- Adaptive language complexity and domain examples
- Real-time comprehension tracking

### Step 2: Prediction & Metacognition
- Interactive multiple-choice questions
- Confidence level assessment
- Prediction accuracy tracking

### Step 3: Guided Practice
- SQL query writing with intelligent hints
- Real-time syntax and logic validation
- Multi-attempt error analysis

### Step 4: Challenge Mode
- Adaptive difficulty based on previous performance
- Complex problem-solving scenarios
- Performance-based scoring

### Step 5: Reflection & Consolidation
- AI-generated personalized poetry summaries
- Concept mastery confirmation
- Progress celebration with gamification

## Features

### For Students
- **Personalized Learning**: AI adapts to individual learning styles and pace
- **Gamification**: XP points, medals, and progress tracking
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Real-time Feedback**: Instant assessment and guidance
- **Progress Analytics**: Detailed insights into learning journey

### For Instructors
- **Learning Analytics**: Comprehensive student performance dashboards
- **Adaptive Controls**: Customize difficulty and content parameters
- **Assessment Tools**: Automated grading and feedback generation
- **Class Insights**: Aggregate performance and learning patterns
- **Content Management**: Easy lesson and challenge customization

### Technical Features
- **Performance Optimized**: Advanced caching and preloading
- **Secure**: Firebase authentication and data protection
- **Progressive Web App**: Offline capabilities and mobile optimization
- **Real-time Sync**: Live progress updates across devices
- **A/B Testing**: Built-in experimentation framework

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for AI-powered features
- `FIREBASE_PROJECT_ID`: Firebase project identifier
- `DATABASE_URL`: Primary database connection string
- `REACT_APP_API_URL`: Backend API endpoint

### Customization Options
- **AI Models**: Configure OpenAI model parameters in `services/ai_service.py`
- **Learning Analytics**: Adjust tracking parameters in `services/student_tracker.py`
- **UI Themes**: Customize appearance in `frontend/src/App.css`
- **Gamification**: Modify XP and medal systems in `frontend/src/utils/levelSystem.js`

## Demo

### Live Demo
Visit our live deployment: **[Demo Link Coming Soon]**

### Local Demo Instructions
1. Follow the setup instructions above
2. Navigate to `http://localhost:3000`
3. Click "Start Learning" to begin the demo
4. Try the sample "INNER JOIN" lesson

### Sample Learning Path
1. **Register/Login** with demo credentials
2. **Select SQL Concept** from the curriculum
3. **Experience 5-Step Learning** process
4. **View Progress** in the analytics dashboard
5. **Earn Medals** and track XP progression

## Performance Monitoring

The system includes comprehensive performance monitoring:
- **Response Times**: API endpoint performance tracking
- **User Experience**: Core Web Vitals monitoring
- **Learning Analytics**: Real-time progress and engagement metrics
- **Error Tracking**: Automated error detection and reporting

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **OpenAI** for GPT-4 integration
- **Google Firebase** for real-time database services
- **React Team** for the excellent frontend framework
- **FastAPI** for the high-performance backend framework

## Support

For questions, issues, or contributions:
- Email: [team-email@example.com]
- Issues: [GitHub Issues](https://github.com/your-team/PedagogicalAI/issues)
- Documentation: [Wiki](https://github.com/your-team/PedagogicalAI/wiki)

---

**PedagogicalAI** - Transforming SQL education through intelligent, adaptive learning experiences.
