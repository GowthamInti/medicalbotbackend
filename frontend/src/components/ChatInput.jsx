import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Paperclip, 
  Mic, 
  Square, 
  Settings, 
  FileText, 
  Brain,
  Loader2
} from 'lucide-react';

const ChatInput = ({ 
  onSendMessage, 
  isLoading, 
  disabled,
  transcriptionSuggestions = [],
  grammarSuggestions = []
}) => {
  const [message, setMessage] = useState('');
  const [showOptions, setShowOptions] = useState(false);
  const [transcriptionType, setTranscriptionType] = useState('');
  const [outputTemplate, setOutputTemplate] = useState('');
  const [grammarRules, setGrammarRules] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [message]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading || disabled) return;

    const options = {
      transcriptionType: transcriptionType || undefined,
      outputTemplate: outputTemplate || undefined,
      grammarRules: grammarRules || undefined,
    };

    onSendMessage(message, options);
    setMessage('');
    setTranscriptionType('');
    setOutputTemplate('');
    setGrammarRules('');
    setShowOptions(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const insertSuggestion = (suggestion) => {
    if (suggestion.prompt) {
      setMessage(prev => prev + (prev ? '\n\n' : '') + suggestion.prompt);
      setTranscriptionType(suggestion.type);
    }
  };

  const insertGrammarRule = (rule) => {
    setGrammarRules(prev => prev ? `${prev}, ${rule}` : rule);
  };

  const handleMicToggle = () => {
    setIsRecording(!isRecording);
    // TODO: Implement speech recognition
  };

  return (
    <div className="bg-white border-t border-gray-200">
      {/* Options Panel */}
      {showOptions && (
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Transcription Type */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Transcription Type
              </label>
              <select
                value={transcriptionType}
                onChange={(e) => setTranscriptionType(e.target.value)}
                className="w-full text-sm border border-gray-300 rounded-md px-2 py-1 focus:outline-none focus:ring-1 focus:ring-medical-500"
              >
                <option value="">Select type...</option>
                <option value="chest-xray">Chest X-Ray</option>
                <option value="ct-scan">CT Scan</option>
                <option value="mri">MRI</option>
                <option value="ultrasound">Ultrasound</option>
                <option value="general">General Radiology</option>
              </select>
            </div>

            {/* Output Template */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Output Template
              </label>
              <select
                value={outputTemplate}
                onChange={(e) => setOutputTemplate(e.target.value)}
                className="w-full text-sm border border-gray-300 rounded-md px-2 py-1 focus:outline-none focus:ring-1 focus:ring-medical-500"
              >
                <option value="">Standard format</option>
                <option value="detailed">Detailed report</option>
                <option value="brief">Brief summary</option>
                <option value="structured">Structured sections</option>
              </select>
            </div>

            {/* Grammar Rules */}
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Grammar Focus
              </label>
              <input
                type="text"
                value={grammarRules}
                onChange={(e) => setGrammarRules(e.target.value)}
                placeholder="e.g., formal tone, active voice"
                className="w-full text-sm border border-gray-300 rounded-md px-2 py-1 focus:outline-none focus:ring-1 focus:ring-medical-500"
              />
            </div>
          </div>

          {/* Quick Suggestions */}
          <div className="mt-3 space-y-2">
            {transcriptionSuggestions.length > 0 && (
              <div>
                <div className="text-xs font-medium text-gray-700 mb-1">Quick Transcription Types:</div>
                <div className="flex flex-wrap gap-1">
                  {transcriptionSuggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => insertSuggestion(suggestion)}
                      className="text-xs px-2 py-1 bg-medical-100 text-medical-700 rounded hover:bg-medical-200 transition-colors duration-200"
                    >
                      {suggestion.title}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {grammarSuggestions.length > 0 && (
              <div>
                <div className="text-xs font-medium text-gray-700 mb-1">Grammar Rules:</div>
                <div className="flex flex-wrap gap-1">
                  {grammarSuggestions.map((rule, index) => (
                    <button
                      key={index}
                      onClick={() => insertGrammarRule(rule)}
                      className="text-xs px-2 py-1 bg-primary-100 text-primary-700 rounded hover:bg-primary-200 transition-colors duration-200"
                    >
                      {rule}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="p-4">
        <form onSubmit={handleSubmit} className="space-y-3">
          {/* Main input */}
          <div className="flex items-end space-x-2">
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Enter your medical transcription or ask for help with formatting..."
                disabled={disabled || isLoading}
                className="w-full min-h-[80px] max-h-[200px] px-3 py-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-medical-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
                rows={1}
              />
              
              {/* Character count */}
              <div className="absolute bottom-2 right-2 text-xs text-gray-400">
                {message.length}
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex items-center space-x-1">
              {/* Voice recording */}
              <button
                type="button"
                onClick={handleMicToggle}
                disabled={disabled || isLoading}
                className={`p-2 rounded-lg transition-colors duration-200 ${
                  isRecording
                    ? 'bg-error-100 text-error-600 hover:bg-error-200'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
                title={isRecording ? 'Stop recording' : 'Start voice recording'}
              >
                {isRecording ? (
                  <Square className="w-4 h-4" />
                ) : (
                  <Mic className="w-4 h-4" />
                )}
              </button>

              {/* Options toggle */}
              <button
                type="button"
                onClick={() => setShowOptions(!showOptions)}
                disabled={disabled || isLoading}
                className={`p-2 rounded-lg transition-colors duration-200 ${
                  showOptions
                    ? 'bg-medical-100 text-medical-600'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
                title="Transcription options"
              >
                <Settings className="w-4 h-4" />
              </button>

              {/* Send button */}
              <button
                type="submit"
                disabled={!message.trim() || isLoading || disabled}
                className="px-4 py-2 bg-medical-600 text-white rounded-lg hover:bg-medical-700 focus:outline-none focus:ring-2 focus:ring-medical-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 flex items-center space-x-1"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Processing...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span className="text-sm">Send</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Status indicators */}
          {(transcriptionType || outputTemplate || grammarRules) && (
            <div className="flex flex-wrap gap-2 text-xs">
              {transcriptionType && (
                <span className="px-2 py-1 bg-medical-100 text-medical-700 rounded">
                  Type: {transcriptionType}
                </span>
              )}
              {outputTemplate && (
                <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded">
                  Template: {outputTemplate}
                </span>
              )}
              {grammarRules && (
                <span className="px-2 py-1 bg-success-100 text-success-700 rounded">
                  Grammar: {grammarRules}
                </span>
              )}
            </div>
          )}
        </form>

        {/* Help text */}
        <div className="mt-2 text-xs text-gray-500 text-center">
          Press Shift+Enter for new line, Enter to send. Use options for specialized medical transcription.
        </div>
      </div>
    </div>
  );
};

export default ChatInput;