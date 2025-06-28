#!/usr/bin/env python3
"""
SQL AI Teaching System - Quick Launcher
Quick launcher for SQL AI Teaching System (New 5-Step Version Only)
"""

import sys
import subprocess
from utils.io_helpers import get_user_input, print_header


def show_welcome():
    """Display welcome interface"""
    print_header("SQL AI Teaching System - 5-Step Dynamic Learning Flow")
    print("""
🎓 SQL AI Teaching System - 5-Step Intelligent Adaptive Teaching

✨ System Features:
   • Concept Introduction with Understanding Confirmation Loop
   • Example Prediction (MCQ with Retry Mechanism)
   • Conceptual Assessment (Query + Explanation Dual Scoring)
   • Guided Practice (Adaptive Difficulty Adjustment)
   • AI Reflection Poem (Creative Learning Summary)
   • Intelligent User Modeling & Personalized Analysis

🎯 Supported SQL Concepts:
   INNER JOIN, LEFT JOIN, RIGHT JOIN, GROUP BY, WHERE, ORDER BY, 
   HAVING, SUBQUERIES, COUNT/SUM/AVG, and more

💡 Complete AI-driven personalized SQL learning experience
    """)


def run_system_check():
    """Run system check"""
    print_header("System Environment Check")
    
    checks = [
        ("Python Version", lambda: sys.version_info >= (3, 8)),
        ("Core Models", lambda: check_core_models()),
        ("New Controller", lambda: check_new_controller()),
        ("Service Modules", lambda: check_services()),
        ("Utility Modules", lambda: check_utils()),
    ]
    
    all_passed = True
    
    for name, check_func in checks:
        try:
            result = check_func()
            status = "✅ Pass" if result else "❌ Fail"
            print(f"{name:15}: {status}")
            if not result:
                all_passed = False
        except Exception as e:
            print(f"{name:15}: ❌ Error - {e}")
            all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! System ready.")
        print("💡 You can start using the 5-step intelligent teaching system!")
    else:
        print("\n⚠️  Some checks failed, may affect system operation.")
        print("💡 Please check help information or system configuration.")
    
    return all_passed


def check_core_models():
    """Check core models"""
    try:
        from models import UserProfile, UserModel, TeachingFlowData
        return True
    except ImportError:
        return False


def check_new_controller():
    """Check new controller"""
    try:
        from controllers.teaching_controller_v2 import TeachingControllerV2
        return True
    except ImportError:
        return False


def check_services():
    """Check service modules"""
    try:
        from services.ai_service import AIService
        from services.grading_service import GradingService
        return True
    except ImportError:
        return False


def check_utils():
    """Check utility modules"""
    try:
        from utils.io_helpers import get_user_input, print_header
        return True
    except ImportError:
        return False


def run_teaching_system():
    """Run 5-step teaching system"""
    print_header("Launch 5-Step Intelligent Teaching System")
    print("🚀 Starting the latest SQL AI Teaching System...")
    print("💡 Tip: You can type 'quit' or 'exit' at any step to exit")
    
    try:
        subprocess.run([sys.executable, "run_new_system.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ System startup failed: {e}")
        print("💡 Please check system configuration or view help information")
    except KeyboardInterrupt:
        print("\n👋 Program interrupted by user")
    except FileNotFoundError:
        print("❌ Cannot find run_new_system.py file")
        print("💡 Please ensure all system files are complete")


def show_help():
    """Display help information"""
    print_header("System Help Information")
    print("""
🔧 System Requirements:
   • Python 3.8+ 
   • openai library: pip install openai
   • Valid AI API configuration (optional, for full AI functionality)

📁 Core Files:
   • run_new_system.py - 5-step teaching system main program
   • controllers/teaching_controller_v2.py - New teaching controller
   • models/ - Data models (user modeling, teaching flow data)
   • services/ - AI service and grading service

🔑 API Configuration (if AI functionality needed):
   Edit services/ai_service.py to set API key and endpoint

📚 Detailed Documentation:
   • Check available .md files for complete guides and documentation

🎯 Learning Flow:
   Step 1: Concept Introduction & Understanding Confirmation
   Step 2: Example Prediction (MCQ + Retry)
   Step 3: Conceptual Assessment (Query Writing + Explanation)
   Step 4: Guided Practice (Adaptive Difficulty)
   Step 5: AI Reflection Poem (Creative Summary)

💡 Usage Tips:
   • Type 'quit' or 'exit' to exit anytime
   • Type 'DONE' after multi-line input
   • Answer understanding confirmation questions carefully for best experience
   • Check learning analysis reports to understand progress

📞 Troubleshooting:
   • Ensure running in project root directory
   • Check Python version: python --version
   • Verify module imports: python -c "from models import *"
   • Check error messages for specific issues
    """)


def main():
    """Main function"""
    while True:
        show_welcome()
        
        print("\nPlease select an option:")
        print("  1. 🚀 Start SQL Learning (Launch 5-Step Teaching System)")
        print("  2. 🔍 System Environment Check")
        print("  3. 📖 View Help Information")
        print("  4. 👋 Exit Program")
        
        choice = get_user_input("\nChoose (1-4): ").strip()
        
        if choice == "1":
            run_teaching_system()
            get_user_input("\nPress Enter to return to main menu...")
        elif choice == "2":
            run_system_check()
            get_user_input("\nPress Enter to return to main menu...")
        elif choice == "3":
            show_help()
            get_user_input("\nPress Enter to return to main menu...")
        elif choice == "4":
            print("\n👋 Thank you for using SQL AI Teaching System, see you next time!")
            break
        else:
            print("❌ Invalid choice, please choose again")
            get_user_input("\nPress Enter to return to main menu...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program interrupted by user, goodbye!")
    except Exception as e:
        print(f"\n❌ Program error: {e}")
        print("💡 Please check help information or system configuration") 