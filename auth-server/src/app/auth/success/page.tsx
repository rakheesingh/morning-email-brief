import "../../globals.css";

export default function AuthSuccess() {
  return (
    <div style={styles.wrapper}>
      <div style={styles.card}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>✅</div>
        <h1 style={styles.title}>Gmail Connected!</h1>
        <p style={styles.desc}>
          Your account is linked. You can close this tab and return to the
          terminal.
        </p>
        <p style={styles.hint}>
          Run <code style={styles.code}>email-brief</code> to get your first
          briefing.
        </p>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  wrapper: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "linear-gradient(135deg, #f0fdf4, #ecfdf5)",
  },
  card: {
    textAlign: "center",
    padding: "48px 40px",
    background: "#fff",
    borderRadius: 16,
    boxShadow: "0 4px 24px rgba(0,0,0,0.08)",
    maxWidth: 420,
  },
  title: {
    fontSize: 24,
    fontWeight: 700,
    color: "#059669",
    marginBottom: 8,
  },
  desc: {
    fontSize: 15,
    color: "#6b7280",
    lineHeight: 1.5,
    marginBottom: 16,
  },
  hint: {
    fontSize: 14,
    color: "#9ca3af",
  },
  code: {
    background: "#f3f4f6",
    padding: "2px 8px",
    borderRadius: 4,
    fontSize: 13,
  },
};
