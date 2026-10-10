import { useEffect, useState } from "react";

import {
  Activity,
  Bot,
  BrainCircuit,
  ChevronRight,
  CircleDot,
  Code2,
  Database,
  FileCode2,
  GitBranch,
  LayoutDashboard,
  Network,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  Terminal,
  Zap,
} from "lucide-react";

import "./App.css";


function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [activeView, setActiveView] = useState("Dashboard");

  const [graphData, setGraphData] = useState(null);
  const [graphLoading, setGraphLoading] = useState(false);
  const [graphError, setGraphError] = useState("");


  // =====================================================
  // NAVIGATION
  // =====================================================

  const goToSection = (view, id, focusChat = false) => {
    setActiveView(view);

    const element = document.getElementById(id);

    if (element) {
      element.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }

    if (focusChat) {
      setTimeout(() => {
        document.querySelector(".chat-input input")?.focus();
      }, 450);
    }
  };


  // =====================================================
  // LOAD KNOWLEDGE GRAPH
  // =====================================================

  const loadGraph = async () => {
    setGraphLoading(true);
    setGraphError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/graph"
      );

      if (!response.ok) {
        throw new Error("Graph request failed");
      }

      const data = await response.json();

      setGraphData(data);
    } catch (err) {
      console.error(err);

      setGraphError(
        "Unable to load the knowledge graph. Make sure FastAPI and Neo4j are running."
      );
    } finally {
      setGraphLoading(false);
    }
  };


  // Load graph when application starts
  useEffect(() => {
    loadGraph();
  }, []);


  // =====================================================
  // ASK FASTAPI
  // =====================================================

  const askQuestion = async () => {
    if (!question.trim()) {
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/ask",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            question: question,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Backend request failed");
      }

      const data = await response.json();

      setResult(data);

    } catch (err) {
      console.error(err);

      setError(
        "Unable to connect to the backend. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  };


  // =====================================================
  // ENTER KEY
  // =====================================================

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      askQuestion();
    }
  };


  // =====================================================
  // SUGGESTED QUESTION
  // =====================================================

  const useSuggestion = (text) => {
    setQuestion(text);

    setTimeout(() => {
      document.querySelector(".chat-input input")?.focus();
    }, 100);
  };


  // =====================================================
  // GRAPH DATA
  // =====================================================

  const relationships = graphData?.relationships || [];

  const nodes = [];

  relationships.forEach((rel) => {
    const sourceId = `${rel.source_type}:${rel.source}`;
    const targetId = `${rel.target_type}:${rel.target}`;

    if (
      !nodes.some(
        (node) => node.id === sourceId
      )
    ) {
      nodes.push({
        id: sourceId,
        name: rel.source,
        type: rel.source_type,
      });
    }

    if (
      !nodes.some(
        (node) => node.id === targetId
      )
    ) {
      nodes.push({
        id: targetId,
        name: rel.target,
        type: rel.target_type,
      });
    }
  });


  const relationshipCount = relationships.length;

  const uniqueNodes = nodes.length;


  // =====================================================
  // GRAPH POSITION
  // =====================================================

  const getNodePosition = (index) => {
    const positions = [
      { x: 100, y: 90 },
      { x: 300, y: 90 },
      { x: 500, y: 90 },
      { x: 700, y: 90 },

      { x: 100, y: 230 },
      { x: 300, y: 230 },
      { x: 500, y: 230 },
      { x: 700, y: 230 },

      { x: 100, y: 370 },
      { x: 300, y: 370 },
      { x: 500, y: 370 },
      { x: 700, y: 370 },
    ];

    return (
      positions[index] || {
        x: 100 + (index % 4) * 200,
        y: 90 + Math.floor(index / 4) * 140,
      }
    );
  };


  const getNodeIndex = (type, name) => {
    return nodes.findIndex(
      (node) =>
        node.type === type &&
        node.name === name
    );
  };


  const getNodeClass = (type) => {
    if (type === "File") {
      return "kg-file";
    }

    if (type === "Class") {
      return "kg-class";
    }

    if (type === "Method") {
      return "kg-method";
    }

    if (type === "Function") {
      return "kg-function";
    }

    return "kg-other";
  };


  // =====================================================
  // RETURN
  // =====================================================

  return (
    <div className="app">

      {/* =================================================
          BACKGROUND
          ================================================= */}

      <div className="background">

        <div className="glow glow-one"></div>

        <div className="glow glow-two"></div>

        <div className="grid"></div>

      </div>


      {/* =================================================
          SIDEBAR
          ================================================= */}

      <aside className="sidebar">

        <div className="brand">

          <div className="brand-icon">
            <BrainCircuit size={24} />
          </div>

          <div>
            <h2>CodeMind</h2>

            <span>
              AI REVERSE ENGINEERING
            </span>
          </div>

        </div>


        <div className="menu-label">
          WORKSPACE
        </div>


        <nav>

          <div
            className={`nav-item ${
              activeView === "Dashboard"
                ? "active"
                : ""
            }`}
            onClick={() =>
              goToSection(
                "Dashboard",
                "dashboard-top"
              )
            }
          >
            <LayoutDashboard size={19} />

            <span>
              Dashboard
            </span>
          </div>


          <div
            className={`nav-item ${
              activeView === "Code Explorer"
                ? "active"
                : ""
            }`}
            onClick={() =>
              goToSection(
                "Code Explorer",
                "architecture-section"
              )
            }
          >
            <FileCode2 size={19} />

            <span>
              Code Explorer
            </span>
          </div>


          <div
            className={`nav-item ${
              activeView === "Semantic Search"
                ? "active"
                : ""
            }`}
            onClick={() =>
              goToSection(
                "Semantic Search",
                "assistant-section",
                true
              )
            }
          >
            <Search size={19} />

            <span>
              Semantic Search
            </span>
          </div>


          <div
            className={`nav-item ${
              activeView === "AI Assistant"
                ? "active"
                : ""
            }`}
            onClick={() =>
              goToSection(
                "AI Assistant",
                "assistant-section",
                true
              )
            }
          >
            <Bot size={19} />

            <span>
              AI Assistant
            </span>
          </div>


          <div
            className={`nav-item ${
              activeView === "Architecture Graph"
                ? "active"
                : ""
            }`}
            onClick={() =>
              goToSection(
                "Architecture Graph",
                "architecture-section"
              )
            }
          >
            <Network size={19} />

            <span>
              Architecture Graph
            </span>
          </div>


          <div
            className={`nav-item ${
              activeView === "Knowledge Graph"
                ? "active"
                : ""
            }`}
            onClick={() =>
              goToSection(
                "Knowledge Graph",
                "knowledge-graph-section"
              )
            }
          >
            <Database size={19} />

            <span>
              Knowledge Graph
            </span>
          </div>


          <div
            className={`nav-item ${
              activeView === "Reports"
                ? "active"
                : ""
            }`}
            onClick={() =>
              goToSection(
                "Reports",
                "activity-section"
              )
            }
          >
            <Activity size={19} />

            <span>
              Reports
            </span>
          </div>

        </nav>


        <div className="sidebar-bottom">

          <div className="system-status">

            <div className="status-dot"></div>

            <div>

              <strong>
                System Online
              </strong>

              <span>
                All services operational
              </span>

            </div>

          </div>


          <div
            className={`nav-item ${
              activeView === "Settings"
                ? "active"
                : ""
            }`}
            onClick={() =>
              goToSection(
                "Settings",
                "dashboard-top"
              )
            }
          >
            <Settings size={19} />

            <span>
              Settings
            </span>

          </div>

        </div>

      </aside>


      {/* =================================================
          MAIN
          ================================================= */}

      <main
        className="main"
        id="dashboard-top"
      >


        {/* =================================================
            TOP BAR
            ================================================= */}

        <header className="topbar">

          <div className="breadcrumb">

            <Terminal size={17} />

            <span>
              AI Software Reverse Engineering
            </span>

            <ChevronRight size={15} />

            <span className="muted">
              Dashboard
            </span>

          </div>


          <div className="top-actions">

            <div className="system-pill">

              <span className="system-dot"></span>

              <span>
                Local AI
              </span>

            </div>

          </div>

        </header>


        {/* =================================================
            HERO
            ================================================= */}

        <section className="hero">

          <div>

            <span className="eyebrow">
              SOFTWARE INTELLIGENCE PLATFORM
            </span>

            <h1>
              Understand your
              <span> codebase.</span>
            </h1>

            <p>
              Analyze legacy software,
              reconstruct architecture,
              explore dependencies and
              ask questions using AI.
            </p>

          </div>


          <div className="hero-badge">

            <Zap size={18} />

            <div>

              <strong>
                AI Powered
              </strong>

              <span>
                Vector + Graph RAG
              </span>

            </div>

          </div>

        </section>


        {/* =================================================
            STAT CARDS
            ================================================= */}

        <section className="stats-grid">

          <StatCard
            icon={<FileCode2 />}
            title="Source Files"
            value="3"
            subtitle="Python files analyzed"
          />

          <StatCard
            icon={<Network />}
            title="Graph Nodes"
            value={uniqueNodes || "12"}
            subtitle="Knowledge graph"
            active
          />

          <StatCard
            icon={<GitBranch />}
            title="Relationships"
            value={relationshipCount || "17"}
            subtitle="Dependencies mapped"
          />

          <StatCard
            icon={<BrainCircuit />}
            title="AI Model"
            value="Qwen3"
            subtitle="8B local model"
          />

        </section>


        {/* =================================================
            ARCHITECTURE OVERVIEW
            ================================================= */}

        <section
          className="panel architecture-panel"
          id="architecture-section"
        >

          <div className="panel-header">

            <div>

              <span className="panel-label">
                CODEBASE
              </span>

              <h3>
                Architecture Overview
              </h3>

            </div>


            <button
              className="icon-button"
              onClick={() =>
                goToSection(
                  "Knowledge Graph",
                  "knowledge-graph-section"
                )
              }
            >
              <Network size={17} />
            </button>

          </div>


          <div className="architecture-content">

            <div className="architecture-node node-main">

              <FileCode2 size={18} />

              <span>
                main.py
              </span>

            </div>


            <div className="connection connection-one"></div>


            <div className="architecture-node node-payment">

              <Code2 size={17} />

              <span>
                PaymentService
              </span>

            </div>


            <div className="connection connection-two"></div>


            <div className="architecture-node node-user">

              <ShieldCheck size={17} />

              <span>
                UserService
              </span>

            </div>


            <div className="graph-line line-one"></div>

            <div className="graph-line line-two"></div>

          </div>


          <div className="panel-footer">

            <span>

              <CircleDot size={11} />

              Live knowledge graph

            </span>


            <button
              onClick={() =>
                goToSection(
                  "Knowledge Graph",
                  "knowledge-graph-section"
                )
              }
            >
              View full graph

              <ChevronRight size={14} />

            </button>

          </div>

        </section>


        {/* =================================================
            KNOWLEDGE GRAPH
            ================================================= */}

        <section
          className="panel knowledge-graph-panel"
          id="knowledge-graph-section"
        >

          <div className="panel-header">

            <div>

              <span className="panel-label">
                NEO4J
              </span>

              <h3>
                Knowledge Graph
              </h3>

            </div>


            <button
              className="icon-button"
              onClick={loadGraph}
            >
              <Database size={17} />
            </button>

          </div>


          <div className="knowledge-graph-visual">


            {/* GRAPH SUMMARY */}

            <div className="graph-summary">

              <div>

                <strong>
                  {uniqueNodes}
                </strong>

                <span>
                  Nodes
                </span>

              </div>


              <div>

                <strong>
                  {relationshipCount}
                </strong>

                <span>
                  Relationships
                </span>

              </div>


              <div>

                <strong>
                  Neo4j
                </strong>

                <span>
                  Live Graph
                </span>

              </div>

            </div>


            {/* LOADING */}

            {graphLoading && (

              <div className="graph-loading">

                <Database size={22} />

                <span>
                  Loading knowledge graph...
                </span>

              </div>

            )}


            {/* ERROR */}

            {graphError && (

              <div className="graph-error">

                <span>
                  {graphError}
                </span>

                <button
                  onClick={loadGraph}
                >
                  Retry
                </button>

              </div>

            )}


            {/* GRAPH */}

            {!graphLoading &&
              !graphError &&
              graphData && (

                <>

                  <div className="graph-canvas">

                    <svg
                      className="graph-lines"
                      viewBox="0 0 800 450"
                      preserveAspectRatio="none"
                    >

                      {relationships.map(
                        (rel, index) => {

                          const sourceIndex =
                            getNodeIndex(
                              rel.source_type,
                              rel.source
                            );

                          const targetIndex =
                            getNodeIndex(
                              rel.target_type,
                              rel.target
                            );

                          const source =
                            getNodePosition(
                              sourceIndex
                            );

                          const target =
                            getNodePosition(
                              targetIndex
                            );

                          return (
                            <g
                              key={`${rel.source}-${rel.target}-${rel.relationship}-${index}`}
                            >

                              <line
                                x1={source.x}
                                y1={source.y}
                                x2={target.x}
                                y2={target.y}
                              />

                            </g>
                          );

                        }
                      )}

                    </svg>


                    {/* NODES */}

                    {nodes.map(
                      (node, index) => {

                        const position =
                          getNodePosition(index);

                        return (

                          <div
                            key={node.id}
                            className={`kg-node ${getNodeClass(
                              node.type
                            )}`}
                            style={{
                              left: `${(position.x / 800) * 100}%`,
                              top: `${(position.y / 450) * 100}%`,
                            }}
                            title={`${node.type}: ${node.name}`}
                          >

                            <div className="kg-node-icon">

                              {node.type === "File" && (
                                <FileCode2 size={16} />
                              )}

                              {node.type === "Class" && (
                                <Database size={16} />
                              )}

                              {node.type === "Function" && (
                                <Code2 size={16} />
                              )}

                              {node.type === "Method" && (
                                <GitBranch size={16} />
                              )}

                            </div>


                            <strong>
                              {node.name}
                            </strong>


                            <span>
                              {node.type}
                            </span>

                          </div>

                        );

                      }
                    )}

                  </div>


                  {/* LEGEND */}

                  <div className="graph-legend">

                    <span>

                      <i className="legend-dot file-dot"></i>

                      File

                    </span>


                    <span>

                      <i className="legend-dot class-dot"></i>

                      Class

                    </span>


                    <span>

                      <i className="legend-dot method-dot"></i>

                      Method / Function

                    </span>


                    <span>

                      <i className="legend-line"></i>

                      Relationship

                    </span>

                  </div>


                  {/* RELATIONSHIP INFORMATION */}

                  <div className="relationship-info">

                    <div className="relationship-title">

                      <span>
                        LIVE NEO4J RELATIONSHIPS
                      </span>

                      <strong>
                        {relationshipCount}
                      </strong>

                    </div>


                    <div className="relationship-list">

                      {relationships.map(
                        (rel, index) => (

                          <div
                            className="relationship-item"
                            key={`${rel.source}-${rel.target}-${index}`}
                          >

                            <span className="relationship-source">
                              {rel.source}
                            </span>

                            <span className="relationship-arrow">
                              →
                            </span>

                            <span className="relationship-type">
                              {rel.relationship}
                            </span>

                            <span className="relationship-arrow">
                              →
                            </span>

                            <span className="relationship-target">
                              {rel.target}
                            </span>

                          </div>

                        )
                      )}

                    </div>

                  </div>

                </>

              )}

          </div>


          <div className="panel-footer">

            <span>

              <CircleDot size={11} />

              Connected to Neo4j

            </span>


            <button
              onClick={loadGraph}
            >

              Refresh graph

              <ChevronRight size={14} />

            </button>

          </div>

        </section>


        {/* =================================================
            AI ASSISTANT
            ================================================= */}

        <section
          className="panel assistant"
          id="assistant-section"
        >

          <div className="panel-header">

            <div>

              <span className="panel-label">
                RAG ENGINE
              </span>

              <h3>
                AI Assistant
              </h3>

            </div>


            <div className="ai-icon">

              <Bot size={18} />

            </div>

          </div>


          <div className="assistant-content">


            {/* AI MESSAGE */}

            <div className="ai-message">

              <div className="ai-avatar">

                <Sparkles size={15} />

              </div>


              <div>

                <strong>
                  CodeMind AI
                </strong>

                <p>
                  Ask me anything about your
                  codebase. I use semantic search
                  and the knowledge graph to find
                  relevant context.
                </p>

              </div>

            </div>


            {/* SUGGESTIONS */}

            <div
              className="suggestion"
              onClick={() =>
                useSuggestion(
                  "Which function validates the user?"
                )
              }
            >

              <Search size={15} />

              <span>
                Which function validates the user?
              </span>

            </div>


            <div
              className="suggestion"
              onClick={() =>
                useSuggestion(
                  "Who calls make_payment?"
                )
              }
            >

              <GitBranch size={15} />

              <span>
                Who calls make_payment?
              </span>

            </div>


            <div
              className="suggestion"
              onClick={() =>
                useSuggestion(
                  "Where is user validation performed?"
                )
              }
            >

              <ShieldCheck size={15} />

              <span>
                Where is user validation performed?
              </span>

            </div>


            {/* CHAT INPUT */}

            <div className="chat-input">

              <input
                type="text"
                value={question}
                placeholder="Ask a question about your code..."
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                onKeyDown={handleKeyDown}
              />


              <button
                onClick={askQuestion}
                disabled={loading}
              >

                {loading ? (
                  "..."
                ) : (
                  <>
                    Ask AI
                    <ChevronRight size={15} />
                  </>
                )}

              </button>

            </div>


            {/* ERROR */}

            {error && (

              <div className="error-message">
                {error}
              </div>

            )}


            {/* AI RESULT */}

            {result && (

              <div className="ai-result">

                <div className="result-header">

                  <div>

                    <span className="panel-label">
                      AI RESPONSE
                    </span>

                    <h4>
                      Analysis complete
                    </h4>

                  </div>

                  <Sparkles size={18} />

                </div>


                <div className="answer-box">

                  <p>
                    {result.answer}
                  </p>

                </div>


                <div className="result-grid">

                  <div>

                    <span>
                      FILE
                    </span>

                    <strong>
                      {result.file}
                    </strong>

                  </div>


                  <div>

                    <span>
                      ELEMENT
                    </span>

                    <strong>
                      {result.name}
                    </strong>

                  </div>


                  <div>

                    <span>
                      TYPE
                    </span>

                    <strong>
                      {result.type}
                    </strong>

                  </div>


                  <div>

                    <span>
                      SIMILARITY
                    </span>

                    <strong>
                      {Number(
                        result.similarity
                      ).toFixed(3)}
                    </strong>

                  </div>

                </div>


                {/* CALLED BY */}

                <div className="result-section">

                  <span className="panel-label">
                    CALLED BY
                  </span>

                  <div className="tag-list">

                    {result.called_by?.length ? (

                      result.called_by.map(
                        (item, index) => (

                          <span
                            className="result-tag"
                            key={index}
                          >
                            {item}
                          </span>

                        )
                      )

                    ) : (

                      <span className="muted">
                        No callers found
                      </span>

                    )}

                  </div>

                </div>


                {/* CALLS */}

                <div className="result-section">

                  <span className="panel-label">
                    CALLS
                  </span>

                  <div className="tag-list">

                    {result.calls?.length ? (

                      result.calls.map(
                        (item, index) => (

                          <span
                            className="result-tag"
                            key={index}
                          >
                            {item}
                          </span>

                        )
                      )

                    ) : (

                      <span className="muted">
                        No outgoing calls
                      </span>

                    )}

                  </div>

                </div>


                {/* CODE */}

                <div className="result-section">

                  <span className="panel-label">
                    SOURCE CODE
                  </span>

                  <pre className="code-result">
                    {result.code}
                  </pre>

                </div>

              </div>

            )}

          </div>

        </section>


        {/* =================================================
            PIPELINE
            ================================================= */}

        <section className="panel pipeline-panel">

          <div className="panel-header">

            <div>

              <span className="panel-label">
                PROCESSING PIPELINE
              </span>

              <h3>
                Code Intelligence Flow
              </h3>

            </div>

          </div>


          <div className="pipeline">

            <PipelineItem
              icon={<Code2 />}
              title="Source Code"
              subtitle="Python project"
            />


            <div className="pipeline-arrow">
              →
            </div>


            <PipelineItem
              icon={<Search />}
              title="Parser"
              subtitle="Tree-sitter"
            />


            <div className="pipeline-arrow">
              →
            </div>


            <PipelineItem
              icon={<Database />}
              title="Knowledge Graph"
              subtitle="Neo4j"
            />


            <div className="pipeline-arrow">
              →
            </div>


            <PipelineItem
              icon={<BrainCircuit />}
              title="RAG"
              subtitle="Vector + Graph"
            />


            <div className="pipeline-arrow">
              →
            </div>


            <PipelineItem
              icon={<Bot />}
              title="AI"
              subtitle="Qwen3:8B"
            />

          </div>

        </section>


        {/* =================================================
            RECENT ACTIVITY
            ================================================= */}

        <section
          className="panel activity-panel"
          id="activity-section"
        >

          <div className="panel-header">

            <div>

              <span className="panel-label">
                ANALYSIS
              </span>

              <h3>
                Recent Code Intelligence
              </h3>

            </div>


            <button className="view-all">

              View all

              <ChevronRight size={15} />

            </button>

          </div>


          <div className="activity-list">

            <ActivityRow
              icon={<ShieldCheck />}
              title="User validation discovered"
              file="sample_project/user.py"
              type="Method"
            />


            <ActivityRow
              icon={<GitBranch />}
              title="Payment dependency mapped"
              file="sample_project/payment.py"
              type="Dependency"
            />


            <ActivityRow
              icon={<Code2 />}
              title="Main execution flow analyzed"
              file="sample_project/main.py"
              type="Function"
            />

          </div>

        </section>


        {/* =================================================
            FOOTER
            ================================================= */}

        <footer>

          <span>
            CodeMind AI
          </span>

          <span>
            •
          </span>

          <span>
            Graph + Vector RAG
          </span>

          <span>
            •
          </span>

          <span>
            Local AI
          </span>

        </footer>

      </main>

    </div>
  );
}


// =====================================================
// STATISTIC CARD
// =====================================================

function StatCard({
  icon,
  title,
  value,
  subtitle,
  active,
}) {

  return (

    <div
      className={`stat-card ${
        active ? "active" : ""
      }`}
    >

      <div className="stat-icon">
        {icon}
      </div>


      <div className="stat-info">

        <span>
          {title}
        </span>

        <strong>
          {value}
        </strong>

        <small>
          {subtitle}
        </small>

      </div>

    </div>

  );
}


// =====================================================
// PIPELINE ITEM
// =====================================================

function PipelineItem({
  icon,
  title,
  subtitle,
}) {

  return (

    <div className="pipeline-item">

      <div className="pipeline-icon">
        {icon}
      </div>

      <strong>
        {title}
      </strong>

      <span>
        {subtitle}
      </span>

    </div>

  );
}


// =====================================================
// ACTIVITY ROW
// =====================================================

function ActivityRow({
  icon,
  title,
  file,
  type,
}) {

  return (

    <div className="activity-row">

      <div className="activity-icon">
        {icon}
      </div>


      <div className="activity-info">

        <strong>
          {title}
        </strong>

        <span>
          {file}
        </span>

      </div>


      <div className="activity-type">
        {type}
      </div>


      <ChevronRight
        size={16}
        className="activity-arrow"
      />

    </div>

  );
}


export default App;