# 🏥 Medical Transcription AI - Frontend Setup Guide

Complete React frontend for the ChatGroq Medical Transcription Chatbot with dual authentication (Admin/User) and specialized medical transcription features.

## 🚀 Quick Start

### 1. **Start Backend API**
```bash
# Ensure backend is running on port 8000
cd /workspace
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. **Setup Frontend**
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm start
```

### 3. **Access Application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs

## 🔐 Authentication

### **Admin Login** (Default)
- **Username**: `admin`
- **Password**: `admin123`
- **Access**: Full system management + user creation

### **User Login** 
- **Create via Admin**: Use admin panel to create user accounts
- **Access**: Medical transcription chat interface

## 🎯 Medical Transcription Features

### **Specialized Input Options**
1. **Transcription Type**: 
   - Chest X-Ray
   - CT Scan  
   - MRI
   - Ultrasound
   - General Radiology

2. **Output Templates**:
   - Standard format
   - Detailed report
   - Brief summary
   - Structured sections

3. **Grammar Rules**: 
   - Custom grammar preferences
   - Medical terminology correction
   - Professional formatting

### **Chat Interface**
- **Real-time messaging** with ChatGroq AI
- **Professional medical formatting**
- **Copy/paste functionality**
- **Session management**
- **Automatic logout** on auth errors (401)

## 🐳 Docker Deployment

### **Complete Stack**
```bash
# Run both backend and frontend
docker-compose -f docker-compose.dev.yml up --build

# Access:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### **Environment Variables**
Create `.env` file in project root:
```env
# Required
GROQ_API_KEY=your_groq_api_key_here
REDIS_URL=rediss://default:password@host:port
SECRET_KEY=your-super-secret-key-min-32-characters-long

# Optional
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=admin123
```

## 📱 User Interface

### **Login Page**
- Toggle between User/Admin login
- Password visibility toggle
- Error handling with clear messages
- Medical-themed design

### **Chat Interface**
- **Header**: User info, connection status, logout
- **Messages**: Professional medical message display
- **Input**: Advanced transcription options
- **Settings**: Future expansion placeholder

### **Responsive Design**
- Mobile-friendly interface
- Tablet optimization
- Desktop experience
- Medical color scheme (blues/teals)

## 🔧 Technical Architecture

### **Frontend Stack**
- **React 18**: Modern React with hooks
- **React Router**: Client-side routing
- **Axios**: HTTP client with interceptors
- **Tailwind CSS**: Utility-first styling
- **Lucide Icons**: Professional iconography

### **State Management**
- **React Context**: Authentication state
- **Custom Hooks**: Chat functionality
- **Local Storage**: JWT token persistence

### **API Integration**
- **JWT Authentication**: Bearer token auth
- **Automatic Retry**: 401 error handling
- **Request Interceptors**: Auto-token injection
- **CORS Support**: Cross-origin requests

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── api/                # Backend communication
│   │   ├── axios.js        # HTTP client config
│   │   ├── auth.js         # Auth endpoints
│   │   └── chat.js         # Chat endpoints
│   ├── auth/               # Authentication logic
│   │   └── AuthContext.js  # Global auth state
│   ├── components/         # UI components
│   │   ├── ChatHeader.jsx  # Chat page header
│   │   ├── ChatMessage.jsx # Message display
│   │   └── ChatInput.jsx   # Input with options
│   ├── pages/              # Route components  
│   │   ├── LoginPage.jsx   # Dual login interface
│   │   └── ChatPage.jsx    # Main chat interface
│   ├── hooks/              # Custom hooks
│   │   ├── useAuth.js      # Authentication hook
│   │   └── useChat.js      # Chat functionality
│   ├── App.jsx             # Main app + routing
│   └── index.jsx           # React entry point
└── public/
    └── index.html          # HTML template
```

## 🎨 Medical UI Features

### **Color Scheme**
- **Medical Blue**: Primary interface colors
- **Success Green**: Positive feedback  
- **Warning Orange**: Alerts and warnings
- **Error Red**: Error states
- **Neutral Gray**: Supporting elements

### **Typography**
- **Inter**: Primary font for readability
- **JetBrains Mono**: Medical reports and code

### **Components**
- **Professional Icons**: Medical and system icons
- **Smooth Animations**: Fade-in, slide-in effects
- **Focus Management**: Keyboard accessibility
- **Responsive Grid**: Mobile-first design

## 🚦 Routing & Navigation

### **Public Routes**
- `/login` - Authentication page
- `/` - Redirects to login

### **Protected Routes** 
- `/chat` - Main chat interface (requires auth)

### **Auto-Redirect Logic**
- Unauthenticated → `/login`
- Authenticated → `/chat`
- 401 Errors → `/login` (with cleanup)

## 🔒 Security Features

### **Authentication Security**
- JWT token validation
- Automatic token refresh handling
- Secure localStorage management
- Session timeout handling

### **API Security**
- CORS configuration
- Request/response interceptors
- Error boundary protection
- Input sanitization

### **UI Security**
- Protected route enforcement
- State cleanup on logout
- Secure credential handling
- XSS prevention

## 📊 Development Workflow

### **Development Mode**
```bash
# Backend (Terminal 1)
cd /workspace
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (Terminal 2) 
cd frontend
npm start
```

### **Production Build**
```bash
# Build frontend
cd frontend
npm run build

# Serve with nginx (via Docker)
docker build -t medical-frontend .
docker run -p 3000:3000 medical-frontend
```

### **Testing**
```bash
# Run frontend tests
cd frontend
npm test

# E2E testing (future)
npm run cypress:open
```

## 🐛 Troubleshooting

### **Common Issues**

1. **Backend Connection Failed**
   - Verify backend running on port 8000
   - Check `REACT_APP_API_URL` in .env
   - Review browser console for CORS errors

2. **Authentication Loop**
   - Clear localStorage: `localStorage.clear()`
   - Check JWT token validity
   - Verify admin credentials

3. **Chat Not Working**
   - Confirm successful login
   - Check network connectivity
   - Verify ChatGroq API key in backend

4. **Styling Issues**
   - Run `npm run build` to rebuild Tailwind
   - Check for CSS conflicts
   - Verify font loading

### **Debug Commands**
```bash
# Check API health
curl http://localhost:8000/health

# Test authentication
curl -X POST http://localhost:8000/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# View frontend logs
# Open browser dev tools → Console tab
```

## 🎯 Next Steps

### **Immediate Usage**
1. Start backend server
2. Install frontend dependencies
3. Start frontend dev server
4. Login with admin credentials
5. Begin medical transcription

### **Production Deployment**
1. Set up environment variables
2. Build Docker images
3. Deploy with docker-compose
4. Configure reverse proxy (optional)
5. Set up SSL certificates

### **Feature Extensions**
- Voice input recording
- Advanced grammar rules
- Template customization
- User management interface
- Reporting dashboard

## 📝 Configuration Summary

### **Required Environment Variables**
```env
# Backend (.env in root)
GROQ_API_KEY=your_groq_key
REDIS_URL=your_redis_url
SECRET_KEY=your_secret_key

# Frontend (.env in frontend/)
REACT_APP_API_URL=http://localhost:8000
```

### **Default Ports**
- **Frontend**: 3000
- **Backend**: 8000
- **Redis**: 6379 (external service)

### **Default Credentials**
- **Admin**: admin / admin123
- **Users**: Created via admin interface

---

## ✅ Success Criteria

**You've successfully set up the frontend when:**

✅ Login page loads at http://localhost:3000  
✅ Admin login works with default credentials  
✅ Chat interface appears after login  
✅ Messages send and receive responses  
✅ Logout redirects back to login  
✅ 401 errors trigger automatic logout  

**🎉 Ready for Medical Transcription AI!**

*Built with React, Tailwind CSS, and medical professionals in mind.*