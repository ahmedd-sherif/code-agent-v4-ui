"use client";

import { useState, useEffect, useRef } from "react";
import {
    Terminal,
    MessageSquare,
    Folder,
    Settings,
    Plus,
    Send,
    Box,
    Cpu,
    Search,
    Code,
    MoreVertical,
    Trash2,
    Edit2,
    Clipboard,
    Check
} from "lucide-react";
import axios from "axios";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

// --- Types ---
interface Workspace {
    name: string;
    path: string;
}

interface Message {
    role: "user" | "assistant" | "system";
    content: string;
    timestamp?: string;
}

interface Session {
    session_id: string;
    name: string;
    last_active: string;
    project_path?: string;
}

// --- Helper to clean generic JSON wrappers ---
function cleanContent(text: string): string {
    if (!text) return "";
    let cleaned = text;
    if (/^\s*\{\s*"content"\s*:\s*"/.test(cleaned)) {
        cleaned = cleaned.replace(/^\s*\{\s*"content"\s*:\s*"/, "");
    }
    if (cleaned.endsWith('"}')) {
        cleaned = cleaned.slice(0, -2);
    } else if (cleaned.endsWith('"\n}')) {
        cleaned = cleaned.slice(0, -3);
    }
    cleaned = cleaned
        .replace(/\\n/g, "\n")
        .replace(/\\"/g, '"')
        .replace(/\\\\/g, "\\")
        .replace(/\\t/g, "\t");
    cleaned = cleaned.replace(/([^\n])```/g, "$1\n```");
    return cleaned;
}

// --- Code Block Component ---
const CodeBlock = ({ node, inline, className, children, ...props }: any) => {
    const [copied, setCopied] = useState(false);
    const match = /language-(\w+)/.exec(className || "");
    const codeString = String(children).replace(/\n$/, "");

    const handleCopy = () => {
        navigator.clipboard.writeText(codeString);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (!inline && match) {
        return (
            <div className="relative group my-4 rounded-lg overflow-hidden border border-white/10 bg-[#1e1e1e]">
                <div className="flex items-center justify-between px-4 py-2 bg-[#2d2d2d] border-b border-white/5">
                    <span className="text-xs text-gray-400 font-mono">{match[1]}</span>
                    <button onClick={handleCopy} className="text-gray-400 hover:text-white transition">
                        {copied ? <Check className="w-3.5 h-3.5" /> : <Clipboard className="w-3.5 h-3.5" />}
                    </button>
                </div>
                <SyntaxHighlighter
                    style={vscDarkPlus}
                    language={match[1]}
                    PreTag="div"
                    customStyle={{ margin: 0, padding: "16px", background: "transparent", fontSize: "13px" }}
                    {...props}
                >
                    {codeString}
                </SyntaxHighlighter>
            </div>
        );
    }
    return (
        <code className={cn("bg-secondary/50 px-1.5 py-0.5 rounded text-sm font-mono text-purple-300", className)} {...props}>
            {children}
        </code>
    );
};

// --- Components ---

const SidebarWorkspace = ({
    workspace,
    active,
    expanded,
    onToggle,
    sessions,
    onAddSession,
    onDeleteWorkspace,
    onRenameWorkspace,
    onSessionClick,
    onDeleteSession,
    onRenameSession,
    activeSessionId,
    isStreaming // Added prop support
}: any) => {
    const [showMenu, setShowMenu] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: any) => {
            if (menuRef.current && !menuRef.current.contains(event.target)) {
                setShowMenu(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    return (
        <div className="mb-1">
            <div
                className={cn(
                    "group flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors cursor-pointer relative pr-16",
                    active ? "bg-secondary/30 text-white" : "text-muted-foreground hover:text-white hover:bg-secondary/20"
                )}
                onClick={onToggle}
            >
                <Folder className={cn("w-4 h-4", active ? "text-purple-400" : "text-gray-500")} />
                <span className="truncate flex-1 font-medium select-none text-xs uppercase tracking-wider">
                    {workspace.name}
                </span>
                <div className="absolute right-1 top-1/2 -translate-y-1/2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                        onClick={(e) => { e.stopPropagation(); onAddSession(); }}
                        className="p-1 hover:bg-white/20 rounded text-muted-foreground hover:text-white"
                        title="New Chat in Workspace"
                    >
                        <Plus className="w-3.5 h-3.5" />
                    </button>
                    <div className="relative" ref={menuRef}>
                        <button
                            onClick={(e) => { e.stopPropagation(); setShowMenu(!showMenu); }}
                            className="p-1 hover:bg-white/20 rounded text-muted-foreground hover:text-white"
                        >
                            <MoreVertical className="w-3.5 h-3.5" />
                        </button>
                        {showMenu && (
                            <div className="absolute right-0 top-full mt-1 w-32 bg-[#1e1e20] border border-white/10 rounded-lg shadow-xl z-50 overflow-hidden">
                                <button
                                    onClick={(e) => { e.stopPropagation(); setShowMenu(false); onRenameWorkspace(); }}
                                    className="w-full text-left px-3 py-2 text-xs hover:bg-white/10 flex items-center gap-2 text-gray-300"
                                >
                                    <Edit2 className="w-3 h-3" /> Rename
                                </button>
                                <button
                                    onClick={(e) => { e.stopPropagation(); setShowMenu(false); onDeleteWorkspace(); }}
                                    className="w-full text-left px-3 py-2 text-xs hover:bg-red-900/30 text-red-400 flex items-center gap-2"
                                >
                                    <Trash2 className="w-3 h-3" /> Delete
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
            {expanded && (
                <div className="ml-2 pl-2 border-l border-white/5 space-y-0.5 mt-1">
                    {sessions.length === 0 && (
                        <div className="text-[10px] text-muted-foreground px-3 py-1 italic opacity-50">
                            No chats yet
                        </div>
                    )}
                    {sessions.map((sess: any) => (
                        <SidebarItem
                            key={sess.session_id}
                            icon={MessageSquare}
                            label={sess.name}
                            active={activeSessionId === sess.session_id}
                            isLoading={activeSessionId === sess.session_id && isStreaming}
                            onClick={(e: any) => { e.stopPropagation(); onSessionClick(sess.session_id); }}
                            onDelete={() => onDeleteSession(sess.session_id)}
                            onRename={() => onRenameSession(sess.session_id, sess.name)}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

const SidebarItem = ({
    icon: Icon,
    label,
    active,
    onClick,
    onDelete,
    onRename,
    isLoading
}: any) => {
    const [showMenu, setShowMenu] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: any) => {
            if (menuRef.current && !menuRef.current.contains(event.target)) {
                setShowMenu(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    return (
        <div className={cn("relative group", showMenu ? "z-50" : "z-0")}>
            <button
                onClick={onClick}
                className={cn(
                    "w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors pr-8 relative",
                    active
                        ? "bg-secondary text-white"
                        : "text-muted-foreground hover:text-white hover:bg-secondary/50"
                )}
            >
                {isLoading ? (
                    <div className="w-4 h-4 rounded-full border-2 border-purple-400/50 border-t-purple-400 animate-spin shrink-0" />
                ) : (
                    <Icon className="w-4 h-4 shrink-0" />
                )}
                <span className="truncate flex-1 text-left">{label}</span>
            </button>

            {(onDelete || onRename) && (
                <div
                    ref={menuRef}
                    className={cn(
                        "absolute right-1 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity",
                        showMenu && "opacity-100"
                    )}
                >
                    <button
                        onClick={(e) => { e.stopPropagation(); setShowMenu(!showMenu); }}
                        className="p-1 hover:bg-white/20 rounded text-muted-foreground/80 hover:text-white"
                    >
                        <MoreVertical className="w-3.5 h-3.5" />
                    </button>
                    {showMenu && (
                        <div className="absolute right-0 top-full mt-1 w-32 bg-[#1e1e20] border border-white/10 rounded-lg shadow-xl z-50 overflow-hidden">
                            {onRename && (
                                <button
                                    onClick={(e) => { e.stopPropagation(); setShowMenu(false); onRename(); }}
                                    className="w-full text-left px-3 py-2 text-xs hover:bg-white/10 flex items-center gap-2 text-gray-300"
                                >
                                    <Edit2 className="w-3 h-3" /> Rename
                                </button>
                            )}
                            {onDelete && (
                                <button
                                    onClick={(e) => { e.stopPropagation(); setShowMenu(false); onDelete(); }}
                                    className="w-full text-left px-3 py-2 text-xs hover:bg-red-900/30 text-red-400 flex items-center gap-2"
                                >
                                    <Trash2 className="w-3 h-3" /> Delete
                                </button>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default function AgentManager() {
    const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
    const [sessions, setSessions] = useState<Session[]>([]);
    const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
    const [expandedWorkspaces, setExpandedWorkspaces] = useState<Set<string>>(new Set());

    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isStreaming, setIsStreaming] = useState(false);
    const [statusMessage, setStatusMessage] = useState("");

    const messagesEndRef = useRef<HTMLDivElement>(null);

    const refreshSessions = async () => {
        try {
            const sessRes = await axios.get("http://localhost:8000/sessions");
            setSessions(sessRes.data);
        } catch (err) { console.error(err); }
    };

    const refreshWorkspaces = async () => {
        try {
            const wsRes = await axios.get("http://localhost:8000/workspaces");
            setWorkspaces(wsRes.data);
        } catch (err) { console.error(err); }
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                await refreshWorkspaces();
                await refreshSessions();
            } catch (err) { console.error(err); }
        };
        fetchData();
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const loadSession = async (sessionId: string) => {
        setActiveSessionId(sessionId);
        try {
            const res = await axios.get(`http://localhost:8000/sessions/${sessionId}/history`);
            setMessages(res.data);
        } catch (err) { console.error(err); }
    };

    const toggleWorkspace = (path: string) => {
        const newSet = new Set(expandedWorkspaces);
        if (newSet.has(path)) newSet.delete(path);
        else newSet.add(path);
        setExpandedWorkspaces(newSet);
    };

    const handleCreateWorkspace = async () => {
        const name = prompt("Enter new workspace name:");
        if (!name) return;
        try {
            await axios.post("http://localhost:8000/workspaces", { name });
            await refreshWorkspaces();
        } catch (err) { alert("Failed to create workspace"); }
    };

    const handleDeleteWorkspace = async (name: string) => {
        if (!confirm(`Are you sure you want to delete workspace '${name}'?`)) return;
        try {
            await axios.delete(`http://localhost:8000/workspaces/${name}`);
            setWorkspaces(prev => prev.filter(ws => ws.name !== name));
        } catch (err) { alert("Failed"); }
    };

    const handleRenameWorkspace = async (name: string) => {
        const newName = prompt("Enter new workspace name:", name);
        if (newName && newName !== name) {
            try {
                await axios.patch(`http://localhost:8000/workspaces/${name}`, { new_name: newName });
                await refreshWorkspaces();
            } catch (err) { alert("Failed"); }
        }
    };

    const handleDeleteSession = async (sessionId: string) => {
        if (!confirm("Are you sure you want to delete this session?")) return;
        try {
            await axios.delete(`http://localhost:8000/sessions/${sessionId}`);
            setSessions(prev => prev.filter(s => s.session_id !== sessionId));
            if (activeSessionId === sessionId) {
                setActiveSessionId(null);
                setMessages([]);
            }
        } catch (err) { alert("Failed"); }
    };

    const handleRenameSession = async (sessionId: string, oldName: string) => {
        const newName = prompt("Enter new session name:", oldName);
        if (newName && newName !== oldName) {
            try {
                await axios.patch(`http://localhost:8000/sessions/${sessionId}`, { name: newName });
                await refreshSessions();
            } catch (err) { alert("Failed"); }
        }
    };

    const handleNewSession = async () => {
        try {
            const res = await axios.post("http://localhost:8000/sessions", { name: "New Chat" });
            const newSession = {
                session_id: res.data.session_id,
                name: res.data.name,
                last_active: new Date().toISOString()
            };
            setSessions([newSession, ...sessions]);
            setActiveSessionId(newSession.session_id);
            setMessages([]);
        } catch (err) { console.error(err); }
    };

    const handleNewSessionInWorkspace = async (wsPath: string | null) => {
        try {
            const payload = { name: "New Chat", project_path: wsPath };
            const res = await axios.post("http://localhost:8000/sessions", payload);
            const newSession = {
                session_id: res.data.session_id,
                name: res.data.name,
                last_active: new Date().toISOString(),
                project_path: payload.project_path
            };
            setSessions([newSession, ...sessions]);
            setActiveSessionId(newSession.session_id);
            setMessages([]);
            if (wsPath) setExpandedWorkspaces(prev => new Set(prev).add(wsPath));
        } catch (err) { console.error(err); }
    };

    const inboxSessions = sessions.filter(s => !s.project_path);
    const getWorkspaceSessions = (path: string) => sessions.filter(s => s.project_path === path);

    const handleSend = async () => {
        if (!input.trim() || !activeSessionId) return;

        const userMessage = { role: "user" as const, content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput("");
        setIsStreaming(true);
        setStatusMessage("Thinking...");

        setMessages(prev => [...prev, { role: "assistant", content: "" }]);

        try {
            const response = await fetch("http://localhost:8000/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    session_id: activeSessionId,
                    message: userMessage.content,
                    model: "openai/qwen3-coder:30b",
                    web_search: false
                })
            });

            if (!response.body) throw new Error("No response body");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let assistantContent = "";

            const updateMessage = (newText: string) => {
                setMessages(prev => {
                    const newMsgs = [...prev];
                    if (newMsgs.length > 0 && newMsgs[newMsgs.length - 1].role === "assistant") {
                        newMsgs[newMsgs.length - 1].content = cleanContent(newText);
                    }
                    return newMsgs;
                });
            };

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split("\n").filter(line => line.trim() !== "");

                for (const line of lines) {
                    try {
                        const data = JSON.parse(line);

                        if (data.type === "content") {
                            assistantContent += data.content;
                            updateMessage(assistantContent);
                        }
                        else if (data.type === "status") {
                            setStatusMessage(data.content);
                        }
                    } catch (e) { console.error(e); }
                }
            }
        } catch (err) {
            setMessages(prev => [...prev, { role: "system", content: "Error: " + String(err) }]);
        } finally {
            setIsStreaming(false);
            setStatusMessage("");
        }
    };

    return (
        <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans">
            {/* Sidebar */}
            <div className="w-64 border-r border-border bg-card flex flex-col">
                <div className="h-14 flex items-center px-4 border-b border-border glass">
                    <Box className="w-5 h-5 text-purple-500 mr-2" />
                    <span className="font-semibold text-lg">Agent Manager</span>
                </div>
                <div className="flex-1 overflow-y-auto p-2 space-y-4">
                    <div>
                        <div className="px-4 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider flex justify-between items-center">
                            Inbox
                            <Plus className="w-3 h-3 hover:text-white cursor-pointer" onClick={() => handleNewSessionInWorkspace(null)} />
                        </div>
                        <div className="space-y-0.5">
                            {inboxSessions.map(sess => (
                                <SidebarItem
                                    key={sess.session_id}
                                    icon={MessageSquare}
                                    label={sess.name}
                                    active={activeSessionId === sess.session_id}
                                    isLoading={activeSessionId === sess.session_id && isStreaming}
                                    onClick={() => loadSession(sess.session_id)}
                                    onDelete={() => handleDeleteSession(sess.session_id)}
                                    onRename={() => handleRenameSession(sess.session_id, sess.name)}
                                />
                            ))}
                        </div>
                    </div>
                    <div>
                        <div className="px-4 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider flex justify-between items-center">
                            Workspaces
                            <button onClick={handleCreateWorkspace} title="New Workspace"><Plus className="w-3 h-3 hover:text-white" /></button>
                        </div>
                        {workspaces.map(ws => (
                            <SidebarWorkspace
                                key={ws.path}
                                workspace={ws}
                                active={false}
                                expanded={expandedWorkspaces.has(ws.path)}
                                onToggle={() => toggleWorkspace(ws.path)}
                                sessions={getWorkspaceSessions(ws.path)}
                                activeSessionId={activeSessionId}
                                isStreaming={isStreaming}
                                onAddSession={() => handleNewSessionInWorkspace(ws.path)}
                                onDeleteWorkspace={() => handleDeleteWorkspace(ws.name)}
                                onRenameWorkspace={() => handleRenameWorkspace(ws.name)}
                                onSessionClick={loadSession}
                                onDeleteSession={handleDeleteSession}
                                onRenameSession={handleRenameSession}
                            />
                        ))}
                    </div>
                </div>
                <div className="p-3 border-t border-border mt-auto">
                    <SidebarItem icon={Settings} label="Settings" />
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col min-w-0">
                <div className="h-14 border-b border-border glass flex items-center justify-between px-6">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <span className="text-foreground font-medium">Code Agent</span>
                        <span>/</span>
                        {(() => {
                            const activeSess = sessions.find(s => s.session_id === activeSessionId);
                            const activeWs = workspaces.find(w => w.path === activeSess?.project_path);
                            if (activeWs) return <span className="text-purple-400 font-medium">{activeWs.name}</span>;
                            return <span>Global</span>;
                        })()}
                        {activeSessionId && <span>/</span>}
                        <span>{sessions.find(s => s.session_id === activeSessionId)?.name || "Home"}</span>
                    </div>
                    <div className="flex items-center gap-3">
                        {isStreaming && (
                            <div className="flex items-center gap-2 px-3 py-1 bg-purple-500/10 text-purple-400 rounded-full text-xs animate-pulse">
                                <div className="w-2 h-2 rounded-full bg-purple-400 animate-bounce" />
                                {statusMessage || "Thinking..."}
                            </div>
                        )}
                        <div className="px-3 py-1.5 bg-secondary/50 rounded-full text-xs font-mono text-muted-foreground flex items-center gap-2">
                            <Cpu className="w-3.5 h-3.5" /> Qwen3-Coder
                        </div>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto p-4 md:p-8 scroll-smooth code-font">
                    <div className="max-w-3xl mx-auto space-y-6">
                        {!activeSessionId && (
                            <div className="text-center py-20">
                                <div className="w-16 h-16 bg-secondary/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                    <Box className="w-8 h-8 text-purple-400" />
                                </div>
                                <h2 className="text-2xl font-bold mb-2">Welcome to Code Agent</h2>
                                <p className="text-muted-foreground">Select a workspace or create a new session to get started.</p>
                                <button
                                    onClick={handleNewSession}
                                    className="mt-6 px-6 py-2 bg-white text-black font-medium rounded-full hover:bg-gray-200 transition"
                                >
                                    Start Creation
                                </button>
                            </div>
                        )}

                        {messages.map((msg, idx) => (
                            <div key={idx} className={cn("flex gap-4", msg.role === "user" ? "justify-end" : "justify-start")}>
                                {msg.role === "assistant" && (
                                    <div className="w-8 h-8 rounded-full bg-blue-600/20 flex items-center justify-center shrink-0">
                                        <Code className="w-4 h-4 text-blue-400" />
                                    </div>
                                )}
                                <div className={cn(
                                    "rounded-lg p-4 max-w-[85%] text-sm leading-relaxed",
                                    msg.role === "user" ? "bg-secondary text-white" : "text-gray-300"
                                )}>
                                    {msg.role === "assistant" ? (
                                        <ReactMarkdown
                                            components={{
                                                code: CodeBlock,
                                                pre: ({ children }) => <>{children}</>
                                            }}
                                        >
                                            {msg.content}
                                        </ReactMarkdown>
                                    ) : (
                                        <div className="whitespace-pre-wrap">{msg.content}</div>
                                    )}
                                    {msg.role === "assistant" && msg.content === "" && isStreaming && idx === messages.length - 1 && (
                                        <span className="animate-pulse">▍</span>
                                    )}
                                </div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                </div>

                <div className="p-4 border-t border-border bg-card/50 backdrop-blur pb-8">
                    <div className="max-w-3xl mx-auto relative group">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && handleSend()}
                            placeholder={activeSessionId ? "Ask Code Agent to build something..." : "Select a session first..."}
                            disabled={!activeSessionId || isStreaming}
                            className="w-full bg-secondary/50 text-white placeholder-gray-500 rounded-xl px-4 py-3 pr-12 focus:outline-none focus:ring-1 focus:ring-white/20 transition-all font-medium disabled:opacity-50"
                        />
                        <button
                            onClick={handleSend}
                            disabled={!activeSessionId || !input.trim() || isStreaming}
                            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-gray-400 hover:text-white disabled:opacity-50 transition-colors"
                        >
                            {isStreaming ? (
                                <div className="w-4 h-4 border-2 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" />
                            ) : (
                                <Send className="w-4 h-4" />
                            )}
                        </button>
                    </div>
                    <div className="text-center mt-2 text-[10px] text-zinc-600">
                        Code Agent can make mistakes. Review generated code.
                    </div>
                </div>
            </div>
        </div>
    );
}
