import { useState, useEffect, useRef } from 'react';
import { useNetworkStore } from '../store/networkStore';

export function FloatingChatbot() {
    const [isOpen, setIsOpen] = useState(false);
    const [chatInput, setChatInput] = useState('');
    const [chatMessages, setChatMessages] = useState<{ role: 'user' | 'assistant'; content: string }[]>([
        { role: 'assistant', content: 'Hello! I\'m your Network Intelligence Copilot. Ask me about topology patterns, anomalies, or correlations.' }
    ]);
    const [isTyping, setIsTyping] = useState(false);
    const chatEndRef = useRef<HTMLDivElement>(null);
    const chatboxRef = useRef<HTMLDivElement>(null);

    const { cells } = useNetworkStore();
    const anomalies = cells.filter(c => c.isAnomaly);

    // Close on outside click
    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (chatboxRef.current && !chatboxRef.current.contains(e.target as Node)) {
                setIsOpen(false);
            }
        };

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [isOpen]);

    // Scroll to bottom on new messages
    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [chatMessages]);

    const handleChatSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!chatInput.trim()) return;

        const userMessage = chatInput.trim();
        setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setChatInput('');
        setIsTyping(true);

        try {
            // Call real backend API
            const response = await fetch('http://localhost:8000/v1/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMessage })
            });

            if (response.ok) {
                const data = await response.json();
                setChatMessages(prev => [...prev, {
                    role: 'assistant',
                    content: data.response || 'I couldn\'t process that request.'
                }]);
            } else {
                // Fallback to contextual response
                let fallbackResponse = '';
                if (userMessage.toLowerCase().includes('anomal')) {
                    fallbackResponse = `Currently detecting ${anomalies.length} anomalous cell(s):\n\n${anomalies.map(a => `• ${a.name}: ${((a.confidence || a.anomalyScore || 0) * 100).toFixed(0)}% anomaly rate`).join('\n') || 'No anomalies detected.'}`;
                } else if (userMessage.toLowerCase().includes('where')) {
                    fallbackResponse = anomalies.length > 0
                        ? `Anomalies detected in: ${anomalies.map(a => a.name).join(', ')}`
                        : 'No anomalies currently detected in the network.';
                } else {
                    fallbackResponse = `Network Status:\n• ${cells.length} total cells\n• ${cells.filter(c => c.isAnomaly).length} anomalies\n• ${Math.round((1 - anomalies.length / cells.length) * 100)}% network health\n\nAsk about specific anomalies or topology.`;
                }
                setChatMessages(prev => [...prev, { role: 'assistant', content: fallbackResponse }]);
            }
        } catch (error) {
            // Network error fallback
            setChatMessages(prev => [...prev, {
                role: 'assistant',
                content: `Network Status:\n• ${cells.length} cells monitored\n• ${anomalies.length} anomalies detected\n\n${anomalies.length > 0 ? `Anomalous cells: ${anomalies.map(a => a.name).join(', ')}` : 'All cells healthy.'}`
            }]);
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <>
            {/* Floating Bot Icon */}
            <button
                onClick={() => setIsOpen(true)}
                className={`floating-bot-button ${isOpen ? 'hidden' : ''}`}
                title="Network Copilot"
            >
                <span className="bot-icon">✨</span>
                <span className="bot-pulse"></span>
            </button>

            {/* Chat Window */}
            {isOpen && (
                <div className="chatbot-overlay">
                    <div ref={chatboxRef} className="chatbot-window">
                        {/* Header */}
                        <div className="chatbot-header">
                            <div className="chatbot-title">
                                <span className="chatbot-icon">✨</span>
                                <div>
                                    <h4>Network Copilot</h4>
                                    <span className="chatbot-status">
                                        <span className="status-dot healthy"></span>
                                        AI Active
                                    </span>
                                </div>
                            </div>
                            <button
                                onClick={() => setIsOpen(false)}
                                className="chatbot-minimize"
                                title="Minimize"
                            >
                                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                                    <path d="M1 1L13 13M1 13L13 1" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                </svg>
                            </button>
                        </div>

                        {/* Messages */}
                        <div className="chatbot-messages">
                            {chatMessages.map((msg, idx) => (
                                <div key={idx} className={`chat-bubble ${msg.role}`}>
                                    {msg.role === 'assistant' && <span className="ai-badge">AI</span>}
                                    <div className="bubble-content">{msg.content}</div>
                                </div>
                            ))}
                            {isTyping && (
                                <div className="chat-bubble assistant">
                                    <span className="ai-badge">AI</span>
                                    <div className="bubble-content typing">
                                        <span className="typing-dot"></span>
                                        <span className="typing-dot"></span>
                                        <span className="typing-dot"></span>
                                    </div>
                                </div>
                            )}
                            <div ref={chatEndRef} />
                        </div>

                        {/* Input */}
                        <form onSubmit={handleChatSubmit} className="chatbot-input-form">
                            <input
                                type="text"
                                value={chatInput}
                                onChange={(e) => setChatInput(e.target.value)}
                                placeholder="Ask about topology..."
                                className="chatbot-input"
                                autoFocus
                            />
                            <button type="submit" className="chatbot-send" disabled={isTyping}>
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13" />
                                </svg>
                            </button>
                        </form>
                    </div>
                </div>
            )}
        </>
    );
}
