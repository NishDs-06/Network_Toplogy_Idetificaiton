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

    const handleChatSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!chatInput.trim()) return;

        const userMessage = chatInput.trim();
        setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setChatInput('');
        setIsTyping(true);

        // Simulate LLM response
        setTimeout(() => {
            let response = '';
            if (userMessage.toLowerCase().includes('anomaly') || userMessage.toLowerCase().includes('anomalies')) {
                response = `Based on my analysis, I've detected ${anomalies.length} anomalies:\n\n${anomalies.map(a => `• ${a.id.toUpperCase()}: ${((a.anomalyScore || 0) * 100).toFixed(0)}% confidence`).join('\n')}\n\nThe primary anomaly in Cell 06 shows elevated congestion patterns correlating with Link 1 degradation.`;
            } else if (userMessage.toLowerCase().includes('correlation') || userMessage.toLowerCase().includes('pattern')) {
                response = 'I\'ve identified 78% correlation between Cells 01-06, suggesting shared infrastructure. The similarity matrix shows 4 distinct topology groups with 94% confidence.';
            } else if (userMessage.toLowerCase().includes('recommend') || userMessage.toLowerCase().includes('action')) {
                response = 'My recommendations:\n\n1. **Investigate** shared fronthaul segment between Link 1 and Link 2\n2. **Monitor** Cell 06 for 15-minute window before escalation\n3. **Consider** load balancing across detected topology groups';
            } else {
                response = `I can help analyze the network topology:\n\n• **24 cells** in the current batch\n• **4 topology groups** identified\n• **${anomalies.length} anomalies** detected\n\nAsk about patterns, anomalies, or correlations.`;
            }
            setChatMessages(prev => [...prev, { role: 'assistant', content: response }]);
            setIsTyping(false);
        }, 1500);
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
