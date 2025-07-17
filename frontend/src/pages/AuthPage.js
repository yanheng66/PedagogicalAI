import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { signInWithEmailAndPassword, createUserWithEmailAndPassword } from "firebase/auth";
import { auth } from "../firestoreSetUp/firebaseSetup";
import { initializeUser } from "../firestoreSetUp/firestoreHelper";
import robotIdle from "../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_idle.png";
import robotTalk from "../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_talk.png";

// CSS Animation Styles
const animationStyles = `
  @keyframes bounce {
    0%, 20%, 50%, 80%, 100% {
      transform: translateY(0);
    }
    40% {
      transform: translateY(-10px);
    }
    60% {
      transform: translateY(-5px);
    }
  }
  
  @keyframes pulse {
    0% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.05);
    }
    100% {
      transform: scale(1);
    }
  }
`;

// Map Firebase error codes to user-friendly English messages
const getErrorMessage = (errorCode, isLogin) => {
  const errorMessages = {
    'auth/user-not-found': 'This email is not registered yet. Please sign up first.',
    'auth/wrong-password': 'Incorrect password. Please try again.',
    'auth/invalid-email': 'Invalid email format.',
    'auth/email-already-in-use': 'This email is already in use. Please choose another email.',
    'auth/weak-password': 'Password is too weak. Please use at least 6 characters.',
    'auth/too-many-requests': 'Too many login attempts. Please try again later.',
    'auth/invalid-credential': isLogin ? 'Wrong credentials. Please check your email and password.' : 'Registration information is invalid.',
    'auth/network-request-failed': 'Network connection failed. Please check your connection.',
    'auth/user-disabled': 'This account has been disabled.',
    'auth/operation-not-allowed': 'This operation is not allowed.',
    'auth/requires-recent-login': 'Please log in again and try.'
  };

  return errorMessages[errorCode] || (isLogin ? 'Login failed. Please check your credentials.' : 'Registration failed. Please try again.');
};

function AuthPage() {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [pose, setPose] = useState(robotIdle);
  const [animation, setAnimation] = useState("bounce");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccessMessage("");

    try {
      if (isLogin) {
        await signInWithEmailAndPassword(auth, email, password);
        navigate("/");
      } else {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        await initializeUser(userCredential.user.uid, {
          email: email,
          xp: 0,
          stepsCompleted: [],
          medals: []
        });
        
        // After successful registration, switch to login mode and show success message
        setIsLogin(true);
        setPassword(""); // Clear password field for security
        setSuccessMessage("Registration successful! Please log in with your new account.");
        
        // Change robot to talk animation to show excitement
        setPose(robotTalk);
        setAnimation("pulse");
        
        // Reset robot pose after a few seconds
        setTimeout(() => {
          setPose(robotIdle);
          setAnimation("bounce");
        }, 3000);
      }
    } catch (error) {
      console.error("Auth error:", error);
      const userFriendlyMessage = getErrorMessage(error.code, isLogin);
      setError(userFriendlyMessage);
    }
  };

  const handleInputFocus = () => {
    setPose(robotTalk);
    setAnimation("pulse");
  };

  const handleInputBlur = () => {
    setPose(robotIdle);
    setAnimation("bounce");
  };

  const handleToggleMode = () => {
    setIsLogin(!isLogin);
    setError("");
    setSuccessMessage("");
  };

  const handleInputChange = (setter) => (e) => {
    setter(e.target.value);
    // Clear messages when user starts typing
    if (error) setError("");
    if (successMessage) setSuccessMessage("");
  };

  return (
    <>
      {/* Inject CSS animation styles */}
      <style>{animationStyles}</style>
      
      <div style={{
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      padding: "20px"
    }}>
      <div style={{
        maxWidth: "400px",
        width: "100%",
        background: "rgba(255, 255, 255, 0.95)",
        borderRadius: "20px",
        padding: "40px",
        boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)",
        backdropFilter: "blur(10px)",
        border: "1px solid rgba(255, 255, 255, 0.2)"
      }}>
        <div style={{ textAlign: "center", marginBottom: "30px" }}>
          {/* Robot character display */}
          <div style={{ marginBottom: "20px" }}>
            <img 
              src={pose}
              alt="AI Teacher Robot"
              style={{
                width: "80px",
                height: "80px",
                animation: `${animation} 2s infinite`,
                transition: "all 0.3s ease"
              }}
            />
          </div>
          
          <h1 style={{
            color: "#4a5568",
            fontSize: "28px",
            marginBottom: "10px",
            fontWeight: "bold"
          }}>
            {isLogin ? "Welcome Back!" : "Join the Adventure!"}
          </h1>
          <p style={{ color: "#718096", fontSize: "16px" }}>
            {isLogin 
              ? "Continue your SQL learning journey" 
              : "Start your journey to become a SQL master"}
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ marginTop: "30px" }}>
          <div style={{ marginBottom: "20px" }}>
            <label style={{
              display: "block",
              marginBottom: "8px",
              color: "#4a5568",
              fontWeight: "500"
            }}>
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={handleInputChange(setEmail)}
              onFocus={handleInputFocus}
              onBlur={handleInputBlur}
              style={{
                width: "100%",
                padding: "12px",
                borderRadius: "8px",
                border: "2px solid #e2e8f0",
                fontSize: "16px",
                transition: "all 0.3s ease",
                outline: "none"
              }}
              placeholder="Enter your email"
              required
            />
          </div>

          <div style={{ marginBottom: "30px" }}>
            <label style={{
              display: "block",
              marginBottom: "8px",
              color: "#4a5568",
              fontWeight: "500"
            }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={handleInputChange(setPassword)}
              onFocus={handleInputFocus}
              onBlur={handleInputBlur}
              style={{
                width: "100%",
                padding: "12px",
                borderRadius: "8px",
                border: "2px solid #e2e8f0",
                fontSize: "16px",
                transition: "all 0.3s ease",
                outline: "none"
              }}
              placeholder="Enter your password"
              required
            />
          </div>

          {error && (
            <div style={{
              padding: "12px",
              borderRadius: "8px",
              backgroundColor: "#fed7d7",
              color: "#c53030",
              marginBottom: "20px",
              fontSize: "14px"
            }}>
              {error}
            </div>
          )}

          {successMessage && (
            <div style={{
              padding: "12px",
              borderRadius: "8px",
              backgroundColor: "#c6f6d5",
              color: "#22543d",
              marginBottom: "20px",
              fontSize: "14px",
              border: "1px solid #9ae6b4"
            }}>
              {successMessage}
            </div>
          )}

          <button
            type="submit"
            style={{
              width: "100%",
              padding: "14px",
              borderRadius: "8px",
              backgroundColor: "#4CAF50",
              color: "white",
              fontSize: "16px",
              fontWeight: "600",
              border: "none",
              cursor: "pointer",
              transition: "all 0.3s ease",
              boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)"
            }}
            onMouseOver={(e) => {
              e.target.style.transform = "translateY(-2px)";
              e.target.style.boxShadow = "0 6px 8px rgba(0, 0, 0, 0.15)";
            }}
            onMouseOut={(e) => {
              e.target.style.transform = "translateY(0)";
              e.target.style.boxShadow = "0 4px 6px rgba(0, 0, 0, 0.1)";
            }}
          >
            {isLogin ? "Sign In" : "Create Account"}
          </button>

          <div style={{
            marginTop: "20px",
            textAlign: "center",
            color: "#718096"
          }}>
            <button
              type="button"
              onClick={handleToggleMode}
              style={{
                background: "none",
                border: "none",
                color: "#4CAF50",
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: "500",
                textDecoration: "underline"
              }}
            >
              {isLogin 
                ? "Don't have an account? Sign up" 
                : "Already have an account? Sign in"}
            </button>
          </div>
        </form>
      </div>
    </div>
    </>
  );
}

export default AuthPage;
