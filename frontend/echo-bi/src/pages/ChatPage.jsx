// src/pages/ChatPage.jsx
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { sendChatMessage } from '../services/api';
import './ChatPage.css';

const ChatPage = () => {
  const navigate = useNavigate();
  const [sessionId, setSessionId] = useState(null);
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Get session from localStorage
  useEffect(() => {
    const stored = localStorage.getItem('echobi_session');
    if (stored) {
      try {
        const sessionData = JSON.parse(stored);
        setSession(sessionData);
        setSessionId(sessionData?.sessionId || null);
      } catch (e) {
        setSession(null);
        setSessionId(null);
      }
    }
  }, []);

  // Initialize welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([{
        id: 1,
        type: 'assistant',
        content: sessionId 
          ? "👋 Hello! I'm your EchoBI data assistant. I have access to your uploaded dataset and can answer questions about:\n\n• **Dataset overview** - rows, columns, data types\n• **Classification** - why your data was classified as a specific type\n• **Column analysis** - details about each column\n• **Preprocessing** - what cleaning steps were applied\n• **Data quality** - scores and issues\n• **Insights** - key findings from your data\n\nWhat would you like to know?"
          : "👋 Hello! I'm your EchoBI data assistant. Please upload a dataset first to start asking questions about your data.",
        timestamp: new Date(),
        suggestions: sessionId 
          ? ["Tell me about my dataset", "What is the data classification?", "Show column analysis", "What's the data quality?"]
          : ["Go to Upload Page"]
      }]);
    }
  }, [sessionId, messages.length]);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const sendMessage = useCallback(async (messageText) => {
    if (!messageText.trim()) return;

    // Handle navigation suggestion
    if (messageText === "Go to Upload Page") {
      navigate('/upload');
      return;
    }

    if (!sessionId) {
      setMessages(prev => [...prev, {
        id: Date.now(),
        type: 'user',
        content: messageText,
        timestamp: new Date()
      }, {
        id: Date.now() + 1,
        type: 'assistant',
        content: "I don't have access to any dataset yet. Please upload a dataset first to ask questions about it.",
        timestamp: new Date(),
        suggestions: ["Go to Upload Page"]
      }]);
      return;
    }

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: messageText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const data = await sendChatMessage(
        sessionId,
        messageText,
        messages.slice(-10).map(m => ({
          role: m.type,
          content: m.content
        }))
      );

      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: data.response,
        timestamp: new Date(),
        suggestions: data.suggestions || [],
        contextUsed: data.context_used || [],
        aiPowered: data.ai_powered || false
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: "I'm sorry, I encountered an error. Please make sure your session is still active and try again.",
        timestamp: new Date(),
        isError: true,
        suggestions: ["Tell me about my dataset", "Try again"]
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, messages, navigate]);

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputValue);
  };

  const handleSuggestionClick = (suggestion) => {
    sendMessage(suggestion);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const clearChat = () => {
    setMessages([{
      id: Date.now(),
      type: 'assistant',
      content: "Chat cleared! How can I help you with your dataset?",
      timestamp: new Date(),
      suggestions: ["Tell me about my dataset", "What is the classification?", "Show column analysis", "Data quality overview"]
    }]);
  };

  const formatTimestamp = (date) => {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatContent = (content) => {
    return content.split('\n').map((line, i) => {
      // Bold text
      let processedLine = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      
      // Headers
      if (line.startsWith('## ')) {
        return <h4 key={i} className="chat-heading">{line.replace('## ', '')}</h4>;
      }
      // List items
      if (line.startsWith('- ') || line.startsWith('• ')) {
        return <li key={i} dangerouslySetInnerHTML={{ __html: processedLine.replace(/^[-•]\s/, '') }} />;
      }
      // Numbered items
      if (/^\d+\.\s/.test(line)) {
        return <li key={i} dangerouslySetInnerHTML={{ __html: processedLine.replace(/^\d+\.\s/, '') }} />;
      }
      // Empty lines
      if (!line.trim()) {
        return <br key={i} />;
      }
      return <p key={i} dangerouslySetInnerHTML={{ __html: processedLine }} />;
    });
  };

  return (
    <div className="chat-page">
      <div className="chat-page-header">
        <div className="chat-header-content">
          <div className="chat-header-left">
            <span className="chat-header-icon">🤖</span>
            <div className="chat-header-info">
              <h1>Chat with Your Data</h1>
              <p className="chat-status">
                {sessionId ? (
                  <>🟢 Connected to: <strong>{session?.filename || 'Dataset'}</strong></>
                ) : (
                  <>🔴 No dataset loaded</>
                )}
              </p>
            </div>
          </div>
          <div className="chat-header-actions">
            <button className="chat-action-btn" onClick={clearChat} title="Clear chat">
              🗑️ Clear
            </button>
            {!sessionId && (
              <button className="chat-upload-btn" onClick={() => navigate('/upload')}>
                📤 Upload Dataset
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="chat-container">
        <div className="chat-messages-area">
          {messages.map((message) => (
            <div key={message.id} className={`chat-message ${message.type} ${message.isError ? 'error' : ''}`}>
              <div className="message-avatar">
                {message.type === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                {message.type === 'assistant' && message.aiPowered && (
                  <span className="ai-badge">✨ AI</span>
                )}
                <div className="message-text">
                  {formatContent(message.content)}
                </div>
                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="message-suggestions">
                    {message.suggestions.map((suggestion, i) => (
                      <button
                        key={i}
                        className="suggestion-chip"
                        onClick={() => handleSuggestionClick(suggestion)}
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
                <span className="message-time">{formatTimestamp(message.timestamp)}</span>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="chat-message assistant loading">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <form className="chat-input-form" onSubmit={handleSubmit}>
          <div className="chat-input-container">
            <input
              ref={inputRef}
              type="text"
              className="chat-input"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={sessionId ? "Ask about your dataset..." : "Upload a dataset to start chatting..."}
              disabled={isLoading}
            />
            <button 
              type="submit" 
              className="chat-send-btn"
              disabled={isLoading || !inputValue.trim()}
            >
              {isLoading ? '⏳' : '➤'}
            </button>
          </div>
          <p className="chat-hint">
            Press Enter to send • Ask about data, classification, columns, or insights
          </p>
        </form>
      </div>
    </div>
  );
};

export default ChatPage;
