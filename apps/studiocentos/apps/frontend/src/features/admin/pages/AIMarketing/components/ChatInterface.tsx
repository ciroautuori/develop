/**
 * ChatInterface Component
 * AI chatbot for marketing assistance
 */

import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Bot, Send, Loader2, User } from 'lucide-react';
import { Button } from '../../../../../shared/components/ui/button';
import { useTheme } from '../../../../../shared/contexts/ThemeContext';
import { useAIChat } from '../../../hooks/marketing/useAIChat';

export default function ChatInterface() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const { messages, isChatting, sendMessage, clearChat } = useAIChat();

  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const cardBg = isDark
    ? 'bg-gradient-to-br from-white/10 to-white/5 border border-white/10'
    : 'bg-white border border-gray-200 shadow-sm';
  const inputBg = isDark
    ? 'bg-white/5 border-white/10 text-white placeholder-gray-400'
    : 'bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-400';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || isChatting) return;

    const message = inputValue;
    setInputValue('');
    await sendMessage(message);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickPrompts = [
    'Come posso migliorare la mia presenza online?',
    'Quali social media dovrei usare per la mia PMI?',
    'Come creare una strategia di content marketing?',
    'Quali KPI dovrei monitorare?',
  ];

  return (
    <div className="space-y-6" role="region" aria-label="Chat assistente marketing AI">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className={`${cardBg} rounded-2xl p-6 h-[600px] flex flex-col`}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-4 pb-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-br from-gold to-gold">
              <Bot className="w-6 h-6 text-white" aria-hidden="true" />
            </div>
            <div>
              <h2 id="chat-heading" className={`text-xl font-bold ${textPrimary}`}>Marketing AI Assistant</h2>
              <p className={`text-sm ${textSecondary}`}>
                Chiedimi consigli su marketing e digital strategy
              </p>
            </div>
          </div>
          {messages.length > 0 && (
            <Button
              variant="outline"
              onClick={clearChat}
              size="sm"
              aria-label="Pulisci tutta la conversazione"
            >
              Pulisci Chat
            </Button>
          )}
        </div>

        {/* Messages */}
        <div
          className="flex-1 overflow-y-auto space-y-4 mb-4"
          role="log"
          aria-live="polite"
          aria-label="Storico conversazione"
          aria-atomic="false"
        >
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center space-y-4">
              <Bot className={`w-16 h-16 ${textSecondary}`} aria-hidden="true" />
              <p className={`text-center ${textSecondary}`}>
                Ciao! Sono il tuo assistente marketing AI.
                <br />
                Chiedimi consigli su strategie, contenuti o qualsiasi cosa!
              </p>
              <div
                className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-2xl mt-6"
                role="group"
                aria-label="Domande rapide suggerite"
              >
                {quickPrompts.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInputValue(prompt)}
                    aria-label={`Usa domanda rapida: ${prompt}`}
                    className={`p-4 rounded-xl text-left text-sm transition-all focus:outline-none focus:ring-2 focus:ring-gold ${
                      isDark
                        ? 'bg-white/5 hover:bg-white/10 text-gray-300'
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                    }`}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  role="article"
                  aria-label={`Messaggio ${msg.role === 'user' ? 'utente' : 'assistente AI'}`}
                  className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.role === 'assistant' && (
                    <div className="p-2 rounded-lg bg-gradient-to-br from-gold to-gold h-fit">
                      <Bot className="w-5 h-5 text-white" aria-hidden="true" />
                    </div>
                  )}
                  <div
                    className={`max-w-[70%] p-4 rounded-2xl ${
                      msg.role === 'user'
                        ? 'bg-gradient-to-r from-gold to-gold text-white'
                        : isDark
                        ? 'bg-white/10 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                    {msg.provider && (
                      <p className="text-xs mt-2 opacity-70">via {msg.provider}</p>
                    )}
                  </div>
                  {msg.role === 'user' && (
                    <div className={`p-2 rounded-lg ${isDark ? 'bg-white/10' : 'bg-gray-200'} h-fit`}>
                      <User className="w-5 h-5" aria-hidden="true" />
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input */}
        <div className="flex gap-2">
          <label htmlFor="chat-input" className="sr-only">Scrivi messaggio alla chat AI</label>
          <input
            id="chat-input"
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Scrivi il tuo messaggio..."
            disabled={isChatting}
            aria-label="Scrivi messaggio alla chat AI"
            aria-describedby="chat-instructions"
            className={`flex-1 px-4 py-3 rounded-xl border ${inputBg} focus:ring-2 focus:ring-gold`}
          />
          <span id="chat-instructions" className="sr-only">
            Premi Enter per inviare il messaggio, Shift+Enter per una nuova riga
          </span>
          <Button
            onClick={handleSend}
            disabled={!inputValue.trim() || isChatting}
            aria-label="Invia messaggio"
            aria-busy={isChatting}
            className="bg-gradient-to-r from-gold to-gold hover:from-gold/90 hover:to-gold"
          >
            {isChatting ? (
              <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" />
            ) : (
              <Send className="w-5 h-5" aria-hidden="true" />
            )}
          </Button>
        </div>
      </motion.div>
    </div>
  );
}
