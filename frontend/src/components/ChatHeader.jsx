import React from 'react';
import { LogOut, User, Shield, Wifi, WifiOff, Settings } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

const ChatHeader = ({ isConnected, onClearSession, onShowSettings }) => {
  const { user, userType, logout } = useAuth();

  const handleLogout = async () => {
    if (window.confirm('Are you sure you want to logout?')) {
      await logout();
    }
  };

  return (
    <div className="bg-white border-b border-gray-200 px-4 py-3">
      <div className="flex items-center justify-between">
        {/* Left side - App title and status */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-medical-500 rounded-lg flex items-center justify-center">
              <span className="text-white text-sm font-bold">MT</span>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">
                Medical Transcription AI
              </h1>
              <div className="flex items-center space-x-2 text-xs text-gray-500">
                <span>Radiology Assistant</span>
                <div className="flex items-center space-x-1">
                  {isConnected ? (
                    <>
                      <Wifi className="w-3 h-3 text-success-500" />
                      <span className="text-success-600">Connected</span>
                    </>
                  ) : (
                    <>
                      <WifiOff className="w-3 h-3 text-error-500" />
                      <span className="text-error-600">Disconnected</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right side - User info and actions */}
        <div className="flex items-center space-x-3">
          {/* User info */}
          <div className="flex items-center space-x-2 text-sm">
            <div className="flex items-center space-x-1 px-2 py-1 bg-gray-100 rounded-md">
              {userType === 'admin' ? (
                <Shield className="w-4 h-4 text-medical-600" />
              ) : (
                <User className="w-4 h-4 text-medical-600" />
              )}
              <span className="text-gray-700 font-medium">
                {user?.username}
              </span>
              <span className="text-xs text-gray-500 capitalize">
                ({userType})
              </span>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center space-x-1">
            {onShowSettings && (
              <button
                onClick={onShowSettings}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors duration-200"
                title="Settings"
              >
                <Settings className="w-4 h-4" />
              </button>
            )}
            
            {onClearSession && (
              <button
                onClick={onClearSession}
                className="px-3 py-1 text-xs text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors duration-200"
                title="Clear Session"
              >
                Clear
              </button>
            )}
            
            <button
              onClick={handleLogout}
              className="flex items-center space-x-1 px-3 py-1 text-sm text-gray-600 hover:text-error-600 hover:bg-error-50 rounded-md transition-colors duration-200"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatHeader;