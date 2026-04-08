import "../globals.css";

export default function Privacy() {
  return (
    <div style={styles.wrapper}>
      <nav style={styles.nav}>
        <a href="/" style={styles.logo}>
          <span style={{ fontSize: 22 }}>📬</span>
          <span style={styles.logoText}>Email Brief</span>
        </a>
      </nav>

      <main style={styles.main}>
        <h1 style={styles.title}>Privacy Policy</h1>
        <p style={styles.updated}>Last updated: April 2026</p>

        <section style={styles.section}>
          <h2 style={styles.h2}>What Email Brief Does</h2>
          <p style={styles.p}>
            Email Brief is an open-source tool that reads your recent Gmail
            messages, generates AI-powered summaries, and prioritizes your inbox.
            It is designed to help you quickly understand which emails need your
            attention.
          </p>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>Data We Access</h2>
          <p style={styles.p}>
            Email Brief requests <strong>read-only</strong> access to your Gmail
            messages. Specifically, we use the{" "}
            <code>gmail.readonly</code> OAuth scope. We <strong>never</strong>:
          </p>
          <ul style={styles.ul}>
            <li>Send emails on your behalf</li>
            <li>Delete or modify any emails</li>
            <li>Access your contacts, calendar, or other Google services</li>
          </ul>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>Where Your Data Is Processed</h2>
          <p style={styles.p}>
            Your email content is processed <strong>locally on your device</strong>{" "}
            (for CLI users) or temporarily in memory on our server (for web
            users). Email content is sent to Google&apos;s Gemini API for
            summarization. We do not store your raw email content on any server.
          </p>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>Data Storage</h2>
          <ul style={styles.ul}>
            <li>
              <strong>OAuth tokens:</strong> Stored locally on your device in a{" "}
              <code>token.json</code> file. Our server processes tokens during
              authentication but does not persist them.
            </li>
            <li>
              <strong>Email summaries:</strong> Stored locally on your device in a
              SQLite database. We do not have access to these summaries.
            </li>
            <li>
              <strong>Account information:</strong> We store your email address
              solely to manage your authentication session. We do not share it
              with third parties.
            </li>
          </ul>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>Third-Party Services</h2>
          <ul style={styles.ul}>
            <li>
              <strong>Google Gmail API:</strong> Used to read your email messages
              (read-only).
            </li>
            <li>
              <strong>Google Gemini API:</strong> Used to generate email summaries.
              Email content is sent to Google for processing. See{" "}
              <a href="https://ai.google.dev/terms">Google AI Terms</a>.
            </li>
          </ul>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>Revoking Access</h2>
          <p style={styles.p}>
            You can revoke Email Brief&apos;s access to your Gmail at any time by
            visiting{" "}
            <a href="https://myaccount.google.com/permissions">
              Google Account Permissions
            </a>{" "}
            and removing Email Brief. You can also delete your local{" "}
            <code>token.json</code> file.
          </p>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>Open Source</h2>
          <p style={styles.p}>
            Email Brief is open source. You can review the complete source code
            on{" "}
            <a href="https://github.com/yourusername/email-brief">GitHub</a> to
            verify exactly how your data is handled.
          </p>
        </section>

        <section style={styles.section}>
          <h2 style={styles.h2}>Contact</h2>
          <p style={styles.p}>
            For any questions about this privacy policy, contact us at{" "}
            <a href="mailto:support@emailbrief.app">support@emailbrief.app</a>.
          </p>
        </section>
      </main>

      <footer style={styles.footer}>
        <p>
          © {new Date().getFullYear()} Email Brief —{" "}
          <a href="/">Home</a> · <a href="/terms">Terms</a>
        </p>
      </footer>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  wrapper: { minHeight: "100vh", display: "flex", flexDirection: "column" },
  nav: {
    borderBottom: "1px solid #e5e7eb",
    background: "#fff",
    padding: "14px 24px",
  },
  logo: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    textDecoration: "none",
    color: "#111827",
  },
  logoText: { fontSize: 18, fontWeight: 700 },
  main: {
    flex: 1,
    maxWidth: 700,
    margin: "0 auto",
    padding: "48px 24px",
  },
  title: {
    fontSize: 32,
    fontWeight: 700,
    marginBottom: 4,
  },
  updated: {
    fontSize: 14,
    color: "#9ca3af",
    marginBottom: 36,
  },
  section: { marginBottom: 28 },
  h2: { fontSize: 18, fontWeight: 600, marginBottom: 8 },
  p: { fontSize: 15, color: "#4b5563", lineHeight: 1.7 },
  ul: {
    fontSize: 15,
    color: "#4b5563",
    lineHeight: 1.7,
    paddingLeft: 24,
  },
  footer: {
    borderTop: "1px solid #e5e7eb",
    padding: "20px 24px",
    textAlign: "center",
    fontSize: 13,
    color: "#9ca3af",
  },
};
