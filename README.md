# SQL Tutor - System Architecture

## 📁 Directory Structure

```
demo-test/
├── config/                    # Configuration management
│   ├── __init__.py
│   └── settings.py           # API settings, constants
├── models/                    # Data models
│   ├── __init__.py
│   ├── user_profile.py       # UserProfile class
│   ├── concept_mastery.py    # (Reserved for future use)
│   ├── learning_profile.py   # (Reserved for future use)
│   └── student.py           # (Reserved for future use)
├── services/                  # Business logic services
│   ├── __init__.py
│   ├── ai_service.py         # AI/LLM interaction service
│   └── grading_service.py    # Student submission grading
├── controllers/               # Application controllers
│   ├── __init__.py
│   └── teaching_controller.py # Teaching flow management
├── utils/                     # Utility functions
│   ├── __init__.py
│   └── io_helpers.py         # Input/output helpers
├── main.py                   # Application entry point
└── sql_tutor.py             # Original monolithic file (deprecated)
```

## 🏗️ Architecture Design

### **1. Separation of Concerns**
- **Config**: Centralized configuration management
- **Models**: Data structures and business entities
- **Services**: Business logic and external integrations
- **Controllers**: Request handling and flow control
- **Utils**: Reusable utility functions

### **2. Key Components**

#### **UserProfile Model**
- Tracks learning progress and performance
- Handles profile updates from grading data
- Supports serialization to dictionary format

#### **AIService**
- Handles all language model interactions
- Provides unified interface for AI requests
- Includes JSON parsing with error handling

#### **GradingService**
- Evaluates student SQL submissions
- Updates user profiles based on performance
- Provides structured feedback

#### **TeachingController**
- Manages the 4-step instructional flow
- Coordinates between services and models
- Handles user interaction flow

### **3. Benefits of This Architecture**
- **Maintainability**: Clear separation makes code easier to modify
- **Testability**: Each component can be unit tested independently
- **Scalability**: Easy to add new features or modify existing ones
- **Reusability**: Services can be reused across different controllers
- **Single Responsibility**: Each class has one clear purpose

## 🚀 Usage

```bash
# Run the refactored application
python main.py

# The functionality remains identical to the original sql_tutor.py
```

## 🔄 Migration from Original

The original `sql_tutor.py` file has been completely refactored while maintaining:
- ✅ All existing functionality
- ✅ Same user interface and experience
- ✅ Identical teaching flow (Steps 1-4)
- ✅ Same AI prompts and behavior

**Breaking Changes**: None - the application works exactly the same way as before. 