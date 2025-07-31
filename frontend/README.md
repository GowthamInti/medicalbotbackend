# Medical Transcription AI - React Frontend

A modern React frontend for the ChatGroq Medical Transcription Chatbot, specialized for radiology transcription with professional medical formatting and grammar correction.

## 🏥 Features

### 🔐 **Dual Authentication System**
- **User Login**: For medical professionals and transcriptionists
- **Admin Login**: For system administrators and user management
- **Automatic Logout**: Handles 401 errors gracefully by redirecting to login

### 💬 **Medical Transcription Chat Interface**
- **Specialized Input**: Medical transcription-focused input with options
- **Real-time Chat**: Instant communication with ChatGroq AI
- **Professional Formatting**: Automated medical report structuring
- **Grammar Correction**: AI-powered medical terminology and grammar enhancement

### 🎯 **Transcription Features**
- **Modality Support**: Chest X-Ray, CT, MRI, Ultrasound, General Radiology
- **Output Templates**: Standard, Detailed, Brief, Structured formats
- **Grammar Rules**: Customizable grammar and style preferences
- **Quick Suggestions**: Pre-defined prompts for common transcription types

### 🎨 **Modern UI/UX**
- **Tailwind CSS**: Beautiful, responsive design
- **Lucide Icons**: Professional medical iconography
- **Medical Color Scheme**: Purpose-built color palette
- **Responsive Design**: Works on desktop, tablet, and mobile

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend API running on port 8000

### Installation

```bash
# Clone the repository (if not already done)
git checkout frontend/react-medical-transcription-ui

# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Edit environment variables
nano .env
```

### Environment Variables

Create a `.env` file in the frontend directory:

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000

# Optional: Enable development features
NODE_ENV=development
```

### Development Server

```bash
# Start development server
npm start

# The app will be available at http://localhost:3000
```

### Production Build

```bash
# Build for production
npm run build

# Serve production build (optional)
npm install -g serve
serve -s build -l 3000
```

## 🐳 Docker Deployment

### Build Docker Image

```bash
# Build the frontend image
docker build -t medical-transcription-frontend .

# Run the container
docker run -p 3000:3000 \
  -e REACT_APP_API_URL=http://localhost:8000 \
  medical-transcription-frontend
```

### Docker Compose (Recommended)

```bash
# Run the complete stack
docker-compose -f docker-compose.dev.yml up --build

# Access the application:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

## 📁 Project Structure

```
frontend/
├── public/
│   ├── index.html          # Main HTML template
│   └── favicon.ico         # App icon
├── src/
│   ├── api/                # API communication
│   │   ├── axios.js        # Axios configuration
│   │   ├── auth.js         # Authentication API
│   │   └── chat.js         # Chat API
│   ├── auth/               # Authentication context
│   │   └── AuthContext.js  # Auth state management
│   ├── components/         # Reusable UI components
│   │   ├── ChatHeader.jsx  # Chat page header
│   │   ├── ChatMessage.jsx # Message display component
│   │   └── ChatInput.jsx   # Message input with options
│   ├── pages/              # Page components
│   │   ├── LoginPage.jsx   # Login interface
│   │   └── ChatPage.jsx    # Main chat interface
│   ├── hooks/              # Custom React hooks
│   │   ├── useAuth.js      # Authentication hook
│   │   └── useChat.js      # Chat functionality hook
│   ├── App.jsx             # Main app component
│   ├── index.jsx           # React entry point
│   └── index.css           # Global styles
├── Dockerfile              # Container configuration
├── nginx.conf              # Nginx configuration
├── package.json            # Dependencies and scripts
├── tailwind.config.js      # Tailwind CSS configuration
└── README.md               # This file
```

## 🎯 Usage Guide

### 1. Login

1. **Navigate to the application** at http://localhost:3000
2. **Choose login type**: User or Admin
3. **Enter credentials**:
   - **Admin**: `admin` / `admin123` (default)
   - **User**: Contact admin for account creation

### 2. Medical Transcription

1. **Access the chat interface** after login
2. **Choose transcription options** (click settings icon):
   - **Type**: Chest X-Ray, CT, MRI, Ultrasound, etc.
   - **Template**: Standard, Detailed, Brief, Structured
   - **Grammar**: Custom grammar rules and formatting
3. **Enter your raw transcription** in the input area
4. **Send message** to receive formatted medical report

### 3. Chat Features

- **Auto-scroll**: Messages automatically scroll to bottom
- **Copy responses**: Click copy icon on AI responses
- **Clear session**: Reset conversation history
- **Voice input**: Microphone button (future feature)
- **Real-time status**: Connection status indicator

### 4. Logout

- **Click logout button** in the header
- **Automatic logout** on authentication errors (401)
- **Secure cleanup** of stored credentials

## 🎨 Styling & Theming

### Medical Color Palette

```css
/* Primary Medical Colors */
medical-50: #f0f9ff    /* Light blue backgrounds */
medical-500: #0ea5e9   /* Primary blue */
medical-600: #0284c7   /* Darker blue for buttons */

/* Status Colors */
success-500: #22c55e   /* Success states */
warning-500: #f59e0b   /* Warning states */
error-500: #ef4444     /* Error states */
```

### Custom Components

- **Medical Report Styling**: Monospace font, structured layout
- **Professional Icons**: Lucide React icons throughout
- **Responsive Grid**: Tailwind CSS grid system
- **Smooth Animations**: Fade-in and slide-in effects

## 🔧 API Integration

### Authentication Flow

```javascript
// Login process
1. User enters credentials
2. Frontend calls /admin/login or /admin/user-login
3. Backend returns JWT token
4. Token stored in localStorage
5. Token included in all subsequent requests
6. Auto-logout on 401 responses
```

### Chat Communication

```javascript
// Message flow
1. User types transcription
2. Frontend enhances with medical context
3. API call to /chat/ endpoint
4. ChatGroq processes medical content
5. Formatted response displayed
6. Session maintained in backend
```

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based auth
- **Automatic Logout**: Handles expired sessions
- **CORS Protection**: Proper cross-origin setup
- **Input Validation**: Client-side validation
- **Secure Headers**: Nginx security headers

## 🐛 Troubleshooting

### Common Issues

1. **"Network Error" when logging in**
   - Check backend is running on port 8000
   - Verify REACT_APP_API_URL is correct
   - Check browser console for CORS errors

2. **"Authentication required" after login**
   - Clear localStorage: `localStorage.clear()`
   - Check JWT token format in browser dev tools
   - Verify backend authentication endpoint

3. **Chat messages not sending**
   - Check network connection
   - Verify authentication token is valid
   - Check backend chat endpoint status

4. **Styling issues**
   - Ensure Tailwind CSS is properly configured
   - Check for CSS build errors
   - Verify custom font loading

### Development Tips

```bash
# Clear all cached data
localStorage.clear()
sessionStorage.clear()

# Check API responses
# Open browser dev tools > Network tab

# Debug authentication
console.log(localStorage.getItem('access_token'))

# Test API directly
curl -H "Authorization: Bearer <token>" http://localhost:8000/health
```

## 🚀 Performance Optimization

- **Code Splitting**: React lazy loading
- **Image Optimization**: Compressed assets
- **Caching**: Static asset caching
- **Minification**: Production builds optimized
- **Gzip Compression**: Nginx compression enabled

## 📝 Contributing

1. Create feature branch from `frontend/react-medical-transcription-ui`
2. Follow React best practices
3. Use TypeScript for new components (optional)
4. Test on multiple screen sizes
5. Ensure accessibility compliance

## 📄 License

This project is part of the ChatGroq Medical Transcription Chatbot system.

## 🆘 Support

- **Backend API Documentation**: http://localhost:8000/docs
- **Chat with the system**: Use the built-in chat interface
- **GitHub Issues**: For bug reports and feature requests

---

**Built with ❤️ for Medical Professionals**  
*Powered by ChatGroq • React • Tailwind CSS*