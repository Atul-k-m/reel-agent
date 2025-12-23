import { useState, useEffect } from 'react'
import './index.css'

const STYLES = [
    { id: "Typographic: Bauhaus", name: "Bauhaus" },
    { id: "Typographic: Swiss", name: "Swiss" },
    { id: "Typographic: Neon", name: "Neon" },
    { id: "Typographic: Kinetic", name: "Kinetic" },
    { id: "Typographic: Bold", name: "Bold" },
    { id: "Typographic: Minimal", name: "Minimal" },
    { id: "Typographic: Glitch", name: "Glitch" },
    { id: "Typographic: Retro", name: "Retro" },
];

const StyleThumbnail = ({ name }) => {
    const base = { width: '100%', height: '100%', position: 'relative', overflow: 'hidden', borderRadius: '4px' };

    if (name === "Bauhaus") return (
        <div style={{ ...base, background: '#F0EAD6' }}>
            <div style={{ position: 'absolute', width: '30px', height: '30px', background: '#D93025', borderRadius: '50%', top: '10px', left: '15px' }} />
            <div style={{ position: 'absolute', width: '10px', height: '50px', background: '#1A3F99', top: '15px', right: '25px', transform: 'rotate(20deg)' }} />
            <div style={{ position: 'absolute', bottom: '5px', width: '100%', textAlign: 'center', fontFamily: 'sans-serif', fontSize: '8px', fontWeight: 'bold', color: '#202020' }}>BAUHAUS</div>
        </div>
    );
    if (name === "Swiss") return (
        <div style={{ ...base, background: '#fff', border: '1px solid #eee' }}>
            <div style={{ position: 'absolute', top: '10px', left: '10px', right: '10px', height: '2px', background: '#000' }} />
            <div style={{ position: 'absolute', top: '10px', left: '30px', bottom: '10px', width: '2px', background: '#000' }} />
            <div style={{ position: 'absolute', bottom: '15px', right: '10px', fontSize: '24px', fontWeight: '900', fontFamily: 'Arial', color: '#000', lineHeight: 0.8 }}>CH</div>
        </div>
    );
    if (name === "Neon") return (
        <div style={{ ...base, background: '#111' }}>
            <div style={{
                position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
                border: '2px solid #0ff', boxShadow: '0 0 10px #0ff', padding: '4px 10px', borderRadius: '4px',
                color: '#fff', fontFamily: 'sans-serif', fontSize: '12px', textShadow: '0 0 5px #0ff'
            }}>NEON</div>
        </div>
    );
    if (name === "Kinetic") return (
        <div style={{ ...base, background: '#FFD700', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ fontSize: '16px', fontWeight: '900', transform: 'rotate(-10deg)', fontFamily: 'sans-serif' }}>
                MOVE<br />FAST
            </div>
        </div>
    );
    if (name === "Bold") return (
        <div style={{ ...base, background: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ fontSize: '20px', fontWeight: '900', color: '#fff', fontFamily: 'Impact, sans-serif', textTransform: 'uppercase' }}>
                BOLD
            </div>
        </div>
    );
    if (name === "Minimal") return (
        <div style={{ ...base, background: '#fafafa', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ fontSize: '10px', color: '#333', fontFamily: 'sans-serif', letterSpacing: '2px' }}>
                minimal
            </div>
        </div>
    );
    if (name === "Glitch") return (
        <div style={{ ...base, background: '#000', border: '1px solid #0f0' }}>
            <div style={{
                position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
                color: '#0f0', fontFamily: 'monospace', fontSize: '14px', textShadow: '2px 0 #f00'
            }}>
                ERROR
            </div>
        </div>
    );
    if (name === "Retro") return (
        <div style={{ ...base, background: 'linear-gradient(to bottom, #2b002b, #000033)' }}>
            <div style={{ position: 'absolute', bottom: 0, width: '100%', height: '40%', background: 'linear-gradient(0deg, transparent 24%, rgba(0, 255, 255, .3) 25%, rgba(0, 255, 255, .3) 26%, transparent 27%, transparent 74%, rgba(0, 255, 255, .3) 75%, rgba(0, 255, 255, .3) 76%, transparent 77%, transparent), linear-gradient(90deg, transparent 24%, rgba(0, 255, 255, .3) 25%, rgba(0, 255, 255, .3) 26%, transparent 27%, transparent 74%, rgba(0, 255, 255, .3) 75%, rgba(0, 255, 255, .3) 76%, transparent 77%, transparent)', backgroundSize: '20px 20px', transform: 'perspective(100px) rotateX(60deg)' }} />
            <div style={{ position: 'absolute', top: '30%', width: '100%', textAlign: 'center', color: '#ff00ff', fontSize: '12px', fontWeight: 'bold', textShadow: '0 0 5px #ff00ff' }}>WAVE</div>
        </div>
    );
    return <div style={{ ...base, background: '#ccc' }}>Aa</div>;
};

// ... existing App component code ...

function App() {
    const [topic, setTopic] = useState("");
    const [sceneCount, setSceneCount] = useState(4);
    const [imageStyle, setImageStyle] = useState("Typographic: Bauhaus");
    const [durationMode, setDurationMode] = useState("auto"); // NEW: Duration mode
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [expandedLogs, setExpandedLogs] = useState({});

    // ... useEffect and fetchJobs ...
    useEffect(() => {
        fetchJobs();
        const interval = setInterval(fetchJobs, 2000);
        return () => clearInterval(interval);
    }, []);

    const fetchJobs = async () => {
        try {
            const res = await fetch("http://localhost:8000/jobs");
            const data = await res.json();
            setJobs(data.reverse());
        } catch (error) {
            console.error("Error fetching jobs:", error);
        }
    };

    const createJob = async () => {
        if (!topic) return;
        setLoading(true);
        try {
            await fetch("http://localhost:8000/jobs", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    topic,
                    scene_count: parseInt(sceneCount),
                    image_style: imageStyle,
                    duration_mode: durationMode
                }),
            });
            setTopic("");
            fetchJobs();
        } catch (error) {
            console.error("Error creating job:", error);
        }
        setLoading(false);
    };

    const getVideoUrl = (path) => {
        if (!path) return "";
        const normalized = path.replace(/\\/g, '/');
        const parts = normalized.split('/generated/');
        if (parts.length > 1) {
            return `http://localhost:8000/generated/${parts[1]}`;
        }
        return "";
    };

    const toggleLogs = (jobId) => {
        setExpandedLogs(prev => ({ ...prev, [jobId]: !prev[jobId] }));
    };

    return (
        <div className="container">
            <div className="header">
                <h1>REELAGENT</h1>
                <p>AUTONOMOUS CONTENT ENGINE</p>
            </div>

            <div className="dashboard-grid">
                {/* LEFT COLUMN: CREATION */}
                <div className="input-section glass-panel">
                    <input
                        className="main-input"
                        type="text"
                        placeholder="Enter a topic (e.g., 'The Future of AI')..."
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                    />

                    <div className="input-row">
                        <select
                            className="main-input"
                            value={sceneCount}
                            onChange={(e) => setSceneCount(e.target.value)}
                        >
                            <option value={4}>4 Scenes (Short)</option>
                            <option value={6}>6 Scenes (Medium)</option>
                            <option value={8}>8 Scenes (Long)</option>
                        </select>

                        <select
                            className="main-input"
                            value={durationMode}
                            onChange={(e) => setDurationMode(e.target.value)}
                        >
                            <option value="auto">⏱️ Auto (Natural)</option>
                            <option value="quick_15s">⚡ Quick (~15s)</option>
                            <option value="short_30s">📱 Short (~30s)</option>
                            <option value="medium_60s">🎬 Medium (~60s)</option>
                        </select>
                    </div>

                    <div style={{ marginTop: '1rem' }}>
                        <label style={{ fontSize: '0.9rem', color: '#888', textTransform: 'uppercase', letterSpacing: '1px' }}>Select Style</label>
                        <div className="style-selector">
                            {STYLES.map((style) => (
                                <div
                                    key={style.id}
                                    className={`style-card ${imageStyle === style.id ? 'selected' : ''}`}
                                    onClick={() => setImageStyle(style.id)}
                                >
                                    <div className="style-preview">
                                        <StyleThumbnail name={style.name} />
                                    </div>
                                    <div className="style-name">{style.name}</div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <button
                        className="cta-button"
                        onClick={createJob}
                        disabled={loading || !topic}
                    >
                        {loading ? "INITIALIZING AGENT..." : "GENERATE CONTENT"}
                    </button>
                </div>

                {/* RIGHT COLUMN: PIPELINES */}
                <div className="jobs-container glass-panel">

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                        <h2 style={{ margin: 0, fontFamily: 'Oswald', letterSpacing: '1px' }}>ACTIVE PIPELINES</h2>
                        <span style={{ fontSize: '0.9rem', color: '#888' }}>{jobs.length} Jobs</span>
                    </div>

                    {jobs.map(job => (
                        <div key={job.id} className={`job-item ${job.status.toLowerCase()}`}>
                            <div className="job-header">
                                <div>
                                    <div className="job-title">{job.topic}</div>
                                    <div style={{ fontSize: '0.8rem', color: '#888', marginTop: '4px' }}>
                                        {new Date(job.created_at || Date.now()).toLocaleTimeString()} • {job.image_style.split(': ')[1]}
                                    </div>
                                </div>
                                <span className="status-badge" style={{ color: job.status === 'completed' ? '#00fa9a' : '#ffd700' }}>
                                    {job.status}
                                </span>
                            </div>

                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <button className="logs-toggle" onClick={() => toggleLogs(job.id)}>
                                    {expandedLogs[job.id] ? "Hide Logs" : "Show Process Logs"}
                                </button>
                                {job.video_path && (
                                    <a
                                        href={getVideoUrl(job.video_path)}
                                        target="_blank"
                                        download
                                        className="download-btn"
                                    >
                                        Download Video ⬇️
                                    </a>
                                )}
                            </div>

                            {expandedLogs[job.id] && (
                                <div className="logs-content">
                                    {job.logs && job.logs.map((log, idx) => (
                                        <div key={idx} style={{ marginBottom: '4px' }}>
                                            <span style={{ color: '#555', marginRight: '8px' }}>&gt;</span>
                                            {log}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                    {jobs.length === 0 && (
                        <div style={{ textAlign: 'center', color: '#666', padding: '2rem' }}>
                            No active jobs. Launch a new agent above.
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default App

