import "../../globals.css";

export default function AuthError({
  searchParams,
}: {
  searchParams: Promise<{ message?: string }>;
}) {
  return (
    <div style={styles.wrapper}>
      <div style={styles.card}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>❌</div>
        <h1 style={styles.title}>Connection Failed</h1>
        <p style={styles.desc}>
          Something went wrong while connecting your Gmail account. Please try
          again.
        </p>
        <a href="/" style={styles.button}>
          ← Back to Home
        </a>
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
    background: "#fef2f2",
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
    color: "#dc2626",
    marginBottom: 8,
  },
  desc: {
    fontSize: 15,
    color: "#6b7280",
    lineHeight: 1.5,
    marginBottom: 24,
  },
  button: {
    display: "inline-block",
    padding: "10px 24px",
    background: "#111827",
    color: "#fff",
    borderRadius: 8,
    textDecoration: "none",
    fontSize: 14,
    fontWeight: 500,
  },
};
