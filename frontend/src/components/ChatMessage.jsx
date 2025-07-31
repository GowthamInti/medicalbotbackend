import React from 'react';
import { User, Bot, AlertTriangle, Info, Copy, Check } from 'lucide-react';
import { useState } from 'react';

const ChatMessage = ({ message }) => {
  const [copied, setCopied] = useState(false);

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  };

  const renderMessageContent = () => {
    // Handle different message types
    switch (message.type) {
      case 'system':
        return (
          <div className="flex items-start space-x-3 max-w-4xl mx-auto">
            <div className="flex-shrink-0 w-8 h-8 bg-medical-100 rounded-full flex items-center justify-center">
              <Info className="w-4 h-4 text-medical-600" />
            </div>
            <div className="flex-1 bg-medical-50 border border-medical-200 rounded-lg p-4">
              <div className="prose prose-sm text-medical-800 whitespace-pre-wrap">
                {message.content}
              </div>
            </div>
          </div>
        );

      case 'error':
        return (
          <div className="flex items-start space-x-3 max-w-4xl mx-auto">
            <div className="flex-shrink-0 w-8 h-8 bg-error-100 rounded-full flex items-center justify-center">
              <AlertTriangle className="w-4 h-4 text-error-600" />
            </div>
            <div className="flex-1 bg-error-50 border border-error-200 rounded-lg p-4">
              <div className="text-error-800 text-sm">
                {message.content}
              </div>
            </div>
          </div>
        );

      case 'user':
        return (
          <div className="flex items-start space-x-3 max-w-4xl mx-auto">
            <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center ml-auto order-2">
              <User className="w-4 h-4 text-primary-600" />
            </div>
            <div className="flex-1 bg-primary-50 border border-primary-200 rounded-lg p-4 order-1">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-primary-700">
                  {message.user}
                </span>
                <span className="text-xs text-gray-500">
                  {formatTimestamp(message.timestamp)}
                </span>
              </div>
              <div className="text-gray-800 whitespace-pre-wrap">
                {message.content}
              </div>
            </div>
          </div>
        );

      case 'assistant':
        return (
          <div className="flex items-start space-x-3 max-w-4xl mx-auto">
            <div className="flex-shrink-0 w-8 h-8 bg-success-100 rounded-full flex items-center justify-center">
              <Bot className="w-4 h-4 text-success-600" />
            </div>
            <div className="flex-1 bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-medium text-success-700">
                    Medical AI Assistant
                  </span>
                  {message.model && (
                    <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                      {message.model}
                    </span>
                  )}
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-500">
                    {formatTimestamp(message.timestamp)}
                  </span>
                  <button
                    onClick={handleCopy}
                    className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors duration-200"
                    title="Copy response"
                  >
                    {copied ? (
                      <Check className="w-3 h-3 text-success-500" />
                    ) : (
                      <Copy className="w-3 h-3" />
                    )}
                  </button>
                </div>
              </div>
              <div className="prose prose-sm max-w-none text-gray-800 whitespace-pre-wrap">
                {message.content}
              </div>
            </div>
          </div>
        );

      default:
        return (
          <div className="flex items-start space-x-3 max-w-4xl mx-auto">
            <div className="flex-1 bg-gray-50 border border-gray-200 rounded-lg p-4">
              <div className="text-gray-800 whitespace-pre-wrap">
                {message.content}
              </div>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="py-4 px-4 animate-fade-in">
      {renderMessageContent()}
    </div>
  );
};

export default ChatMessage;