import { useState, useCallback, useRef, useEffect } from 'react';
import { chatAPI } from '../api/chat';
import { useAuth } from './useAuth';

export const useChat = (sessionId = 'medical-transcription') => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isConnected, setIsConnected] = useState(true);
  const messagesEndRef = useRef(null);

  // Scroll to bottom of messages
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Add initial medical transcription prompt
  useEffect(() => {
    if (messages.length === 0) {
      const initialMessage = {
        id: 'system-prompt',
        type: 'system',
        content: `Welcome to the Medical Transcription AI Assistant. I'm specialized in radiology transcription with structured formatting and grammar correction.

**How to use:**
1. **Input your raw transcription** - I'll improve grammar and structure
2. **Specify template preferences** - Normal, detailed, or custom format
3. **Review the output** - Professional, structured medical reports

**Specializations:**
• Radiology reports (X-ray, CT, MRI, Ultrasound)
• Medical terminology accuracy
• Proper formatting and structure
• Grammar and clarity enhancement

Ready to help with your medical transcription needs!`,
        timestamp: new Date().toISOString(),
      };
      setMessages([initialMessage]);
    }
  }, [messages.length]);

  // Send message
  const sendMessage = useCallback(async (messageContent, options = {}) => {
    if (!messageContent.trim()) return;

    setError(null);
    setIsLoading(true);

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: messageContent.trim(),
      timestamp: new Date().toISOString(),
      user: user?.username || 'User',
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      // Enhance the message with medical context if specified
      let enhancedMessage = messageContent;
      
      if (options.transcriptionType) {
        enhancedMessage = `[${options.transcriptionType.toUpperCase()} TRANSCRIPTION]
${messageContent}

Please format this as a professional radiology report with:
- Proper medical terminology
- Clear structure and organization
- Corrected grammar and syntax
- Standard medical report format`;
      }

      if (options.outputTemplate) {
        enhancedMessage += `\n\nOutput Template: ${options.outputTemplate}`;
      }

      if (options.grammarRules) {
        enhancedMessage += `\n\nGrammar Requirements: ${options.grammarRules}`;
      }

      // Send to API
      const response = await chatAPI.sendMessage(sessionId, enhancedMessage);

      // Add AI response
      const aiMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
        llmProvider: response.llm_provider,
        model: response.model,
        sessionId: response.session_id,
      };

      setMessages(prev => [...prev, aiMessage]);
      setIsConnected(true);
    } catch (error) {
      console.error('Error sending message:', error);
      setError(error.response?.data?.detail || 'Failed to send message');
      setIsConnected(false);
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, user]);

  // Clear chat session
  const clearSession = useCallback(async () => {
    try {
      setIsLoading(true);
      await chatAPI.clearSession(sessionId);
      setMessages([]);
      setError(null);
    } catch (error) {
      console.error('Error clearing session:', error);
      setError('Failed to clear session');
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  // Get quick transcription suggestions
  const getTranscriptionSuggestions = useCallback(() => {
    return [
      {
        title: 'Chest X-Ray',
        prompt: 'Please transcribe this chest X-ray finding with proper medical formatting',
        type: 'chest-xray',
      },
      {
        title: 'CT Scan',
        prompt: 'Format this CT scan report with standard radiology structure',
        type: 'ct-scan',
      },
      {
        title: 'MRI Report',
        prompt: 'Create a structured MRI report from this transcription',
        type: 'mri',
      },
      {
        title: 'Ultrasound',
        prompt: 'Format this ultrasound finding with proper terminology',
        type: 'ultrasound',
      },
    ];
  }, []);

  // Get grammar improvement suggestions
  const getGrammarSuggestions = useCallback(() => {
    return [
      'Correct medical terminology and spelling',
      'Improve sentence structure and clarity',
      'Standardize abbreviations and formatting',
      'Ensure proper tense and voice consistency',
      'Add appropriate medical report sections',
    ];
  }, []);

  return {
    messages,
    isLoading,
    error,
    isConnected,
    messagesEndRef,
    sendMessage,
    clearSession,
    getTranscriptionSuggestions,
    getGrammarSuggestions,
    setError,
  };
};