// src/components/chat/ChatWidget.jsx
import React, { useState, useRef, useEffect } from 'react';
import './ChatWidget.css';

const ChatWidget = ({ sessionId, isOpen, onClose, onToggle }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: "👋 Hi! I'm your EchoBI assistant. I can help you understand your dataset, explain the classification process, describe preprocessing steps, and answer questions about your data. What would you like to know?",
      timestamp: new Date(),
      suggestions: [
        "Tell me about my dataset",
        "What is the data classification?",
        "Show me column analysis",
        "What preprocessing was applied?"
      ]
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const sendMessage = async (messageText) => {
    if (!messageText.trim() || !sessionId) return;

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
      const response = await fetch(`http://localhost:8000/api/v1/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: messageText,
          conversation_history: messages.slice(-10).map(m => ({
            role: m.type,
            content: m.content
          }))
        })
      });

      if (!response.ok) {
        throw new Error('Chat request failed');
      }

      const data = await response.json();

      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: data.response,
        timestamp: new Date(),
        suggestions: data.suggestions || [],
        contextUsed: data.context_used || []
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: "I'm sorry, I encountered an error processing your request. Please make sure you have uploaded and analyzed a dataset first.",
        timestamp: new Date(),
        isError: true,
        suggestions: ["Upload a dataset", "Try again"]
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

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

  const formatTimestamp = (date) => {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatContent = (content) => {
    // Convert markdown-style formatting to JSX
    return content.split('\n').map((line, i) => {
      // Bold text
      line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      // Headers
      if (line.startsWith('## ')) {
        return <h4 key={i} className="chat-heading">{line.replace('## ', '')}</h4>;
      }
      // List items
      if (line.startsWith('- ')) {
        return <li key={i} dangerouslySetInnerHTML={{ __html: line.replace('- ', '') }} />;
      }
      // Numbered items
      if (/^\d+\.\s/.test(line)) {
        return <li key={i} dangerouslySetInnerHTML={{ __html: line.replace(/^\d+\.\s/, '') }} />;
      }
      // Empty lines
      if (!line.trim()) {
        return <br key={i} />;
      }
      return <p key={i} dangerouslySetInnerHTML={{ __html: line }} />;
    });
  };

  if (!isOpen) {
    return (
      <button className="chat-fab" onClick={onToggle} title="Chat with your data">
        <span className="chat-fab-icon">💬</span>
        <span className="chat-fab-pulse"></span>
      </button>
    );
  }

  return (
    <div className="chat-widget">
      <div className="chat-header">
        <div className="chat-header-left">
          <span className="chat-header-icon">🤖</span>
          <div className="chat-header-info">
            <h3>EchoBI Assistant</h3>
            <span className="chat-status">
              {sessionId ? '🟢 Connected to dataset' : '🔴 No dataset loaded'}
            </span>
          </div>
        </div>
        <div className="chat-header-actions">
          <button 
            className="chat-action-btn" 
            onClick={() => setMessages([messages[0]])}
            title="Clear chat"
          >
            🗑️
          </button>
          <button className="chat-close-btn" onClick={onClose}>✕</button>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((message) => (
          <div key={message.id} className={`chat-message ${message.type} ${message.isError ? 'error' : ''}`}>
            <div className="message-avatar">
              {message.type === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
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
            placeholder={sessionId ? "Ask about your dataset..." : "Upload a dataset first..."}
            disabled={isLoading || !sessionId}
          />
          <button 
            type="submit" 
            className="chat-send-btn"
            disabled={isLoading || !inputValue.trim() || !sessionId}
          >
            {isLoading ? '⏳' : '➤'}
          </button>
        </div>
        <p className="chat-hint">
          Press Enter to send • Ask about data, classification, or preprocessing
        </p>
      </form>
    </div>
  );
};

export default ChatWidget;
