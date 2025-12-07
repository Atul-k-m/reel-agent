import { useState, useEffect } from 'react'
import './index.css'
import './logs.css'

function App() {
    const [topic, setTopic] = useState("");
    const [sceneCount, setSceneCount] = useState(4);
    const [imageStyle, setImageStyle] = useState("Cinematic");
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(false);

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
                    image_style: imageStyle
                }),
            });
            setTopic("");
            fetchJobs();
        } catch (error) {
            console.error("Error creating job:", error);
        }
        setLoading(false);
    };

    return (
        <div className="container">
            <div className="header">
                <h1>ReelAgent</h1>
                <p>AI Viral Video Generator</p>
            </div>

            <div className="input-section">
                <input
                    className="main-input"
                    type="text"
                    placeholder="Enter a topic (e.g., 'Evolution of AI')..."
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                />

                {/* Customization Options */}
                <div className="options-group">
                    <select
                        className="style-select"
                        value={sceneCount}
                        onChange={(e) => setSceneCount(e.target.value)}
                    >
                        <option value={4}>4 Scenes (Short)</option>
                        <option value={6}>6 Scenes (Medium)</option>
                        <option value={8}>8 Scenes (Long)</option>
                    </select>

                    <select
                        className="style-select"
                        value={imageStyle}
                        onChange={(e) => setImageStyle(e.target.value)}
                    >
                        <option value="Cinematic">Cinematic</option>
                        <option value="Studio Ghibli">Studio Ghibli</option>
                        <option value="Anime">Anime</option>
                        <option value="Cyberpunk">Cyberpunk</option>
                        <option value="Realistic">Realistic Photos</option>
                        <option value="Digital Art">Digital Art</option>
                    </select>
                </div>

                <button
                    className="cta-button"
                    onClick={createJob}
                    disabled={loading || !topic}
                >
                    {loading ? "Creating..." : "Generate Reel"}
                </button>
            </div>

            <div className="jobs-list">
                <h2>Active Pipelines</h2>
                {jobs.map(job => (
                    <div key={job.id} className="job-card">
                        <div className="job-header">
                            <h3>{job.topic}</h3>
                            <span className={`status-badge ${job.status.toLowerCase()}`}>{job.status}</span>
                        </div>

                        <div className="logs-container">
                            {job.logs && job.logs.map((log, idx) => (
                                <div key={idx} className="log-line">{log}</div>
                            ))}
                        </div>

                        <div className="progress-track">
                            {job.video_path && (
                                <div style={{ marginTop: '1rem', color: '#00ff88' }}>
                                    ✨ Video Ready: {job.video_path}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {jobs.length === 0 && <div className="empty-state">No active jobs. Start one above.</div>}
            </div>
        </div>
    )
}

export default App
