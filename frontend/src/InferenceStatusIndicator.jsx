import { useState, useEffect, useRef } from "react";

const STATUS_COLORS = {
  scaledToZero: { bg: "#ececec", text: "#888888" },
  pending: { bg: "#FFDE99", text: "#E68600" },
  initializing: { bg: "#E6C0FF", text: "#7E26C9" },
  running: { bg: "#ADEFBA", text: "#17803A" },
  paused: { bg: "#D0D0D0", text: "#555555" },
  closed: { bg: "#f2f2f2", text: "#888" },
  error: { bg: "#ffcfd1", text: "#D32F2F" },
  loading: { bg: "#F3F3FF", text: "#6C7CA1" },
};

function Spinner({ color = "#888" }) {
  return (
    <span
      style={{
        display: "inline-block",
        width: 20,
        height: 20,
        marginRight: 10,
        border: `3px solid ${color}44`,
        borderTop: `3px solid ${color}`,
        borderRadius: "50%",
        animation: "spin 1s linear infinite",
        verticalAlign: "middle",
      }}
    />
  );
}

export function InferenceStatusIndicator() {
  const [status, setStatus] = useState("loading");
  const wsRef = useRef(null);
  useEffect(() => {
    const ws = new window.WebSocket(
      "ws://192.168.178.22:8000/inference/ws/status",
    );
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.status) setStatus(data.status);
      } catch (_) {}
    };
    ws.onclose = () => setStatus("closed");
    ws.onerror = () => setStatus("error");
    return () => {
      ws.close();
    };
  }, []);

  const { bg, text } = STATUS_COLORS[status] || STATUS_COLORS["loading"];

  async function handleResume() {
    try {
      const res = await fetch("http://192.168.178.22:8000/inference/resume");
      // Optionally: check for status etc
      if (!res.ok) throw new Error(await res.text());
      // Optionally: refresh status here, but websocket should update soon
    } catch (err) {
      alert("Resume failed: " + err.message);
    }
  }

  async function handlePause() {
    try {
      const res = await fetch("http://192.168.178.22:8000/inference/pause");
      // Optionally: check for status etc
      if (!res.ok) throw new Error(await res.text());
      // Optionally: refresh status here, but websocket should update soon
    } catch (err) {
      alert("Pause failed: " + err.message);
    }
  }

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: bg,
        color: text,
        borderRadius: 16,
        minWidth: 160,
        minHeight: 40,
        padding: "8px 24px",
        fontWeight: 500,
        fontSize: "1.1em",
        boxShadow: "0 2px 8px #0001",
        margin: 4,
        letterSpacing: 1,
      }}
    >
      {status === "initializing" && <Spinner color={text} />}
      <span style={{ margin: "0 auto", fontWeight: 600, color: text }}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
      <style>
        {`
          @keyframes spin { 100% { transform: rotate(360deg); } }
        `}
      </style>
      {status === "paused" ? (
        <button
          onClick={handleResume}
          style={{
            marginLeft: 16,
            padding: "6px 12px",
            borderRadius: 8,
            border: "none",
            background: "#E68600",
            color: "white",
            fontWeight: 600,
          }}
        >
          Resume
        </button>
      ) : (
        <button
          onClick={handlePause}
          style={{
            marginLeft: 16,
            padding: "6px 12px",
            borderRadius: 8,
            border: "none",
            background: "#888",
            color: "white",
            fontWeight: 600,
          }}
        >
          Pause
        </button>
      )}
    </div>
  );
}
