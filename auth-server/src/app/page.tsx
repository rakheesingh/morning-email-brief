import "./globals.css";

export default function Home() {
  return (
    <div style={styles.wrapper}>
      {/* Nav */}
      <nav style={styles.nav}>
        <div style={styles.navInner}>
          <div style={styles.logoRow}>
            <div style={styles.logoIcon}>📬</div>
            <span style={styles.logoText}>Email Brief</span>
          </div>
          <div style={styles.navLinks}>
            <a href="/privacy" style={styles.navLink}>
              Privacy
            </a>
            <a href="/terms" style={styles.navLink}>
              Terms
            </a>
            <a
              href="https://github.com/yourusername/email-brief"
              style={styles.navLink}
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main style={styles.main}>
        {/* Left: Value prop */}
        <div style={styles.left}>
          <h1 style={styles.heading}>
            Your inbox,
            <br />
            <span style={styles.headingAccent}>summarized by AI.</span>
          </h1>
          <p style={styles.subheading}>
            Email Brief reads your latest emails, summarizes each one in a
            sentence, and tells you which to reply to first. Powered by Google
            Gemini. Free and open source.
          </p>

          <div style={styles.features}>
            <div style={styles.feature}>
              <span style={styles.featureIcon}>⚡</span>
              <div>
                <strong>50 emails in seconds</strong>
                <p style={styles.featureDesc}>
                  AI reads and prioritizes your unread inbox instantly.
                </p>
              </div>
            </div>
            <div style={styles.feature}>
              <span style={styles.featureIcon}>🔒</span>
              <div>
                <strong>Private by design</strong>
                <p style={styles.featureDesc}>
                  Your emails never leave your machine. Tokens stored locally.
                </p>
              </div>
            </div>
            <div style={styles.feature}>
              <span style={styles.featureIcon}>🎯</span>
              <div>
                <strong>Smart prioritization</strong>
                <p style={styles.featureDesc}>
                  Urgent, important, FYI, or low priority — sorted for you.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Auth card */}
        <div style={styles.right}>
          <div style={styles.card}>
            <div style={styles.cardLogoRow}>
              <div style={styles.cardLogo}>📬</div>
              <h2 style={styles.cardTitle}>Email Brief</h2>
            </div>
            <p style={styles.cardDesc}>
              Connect your Gmail to get your AI-powered email briefing.
            </p>

            <a href="/api/auth/login" style={styles.googleBtn}>
              <svg
                width="20"
                height="20"
                viewBox="0 0 48 48"
                style={{ flexShrink: 0 }}
              >
                <path
                  fill="#EA4335"
                  d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"
                />
                <path
                  fill="#4285F4"
                  d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"
                />
                <path
                  fill="#FBBC05"
                  d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"
                />
                <path
                  fill="#34A853"
                  d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"
                />
              </svg>
              <span>Sign in with Google</span>
            </a>

            <div style={styles.cardDivider}></div>

            <p style={styles.cardFootnote}>
              We only request <strong>read-only</strong> access to your emails.
              We never send, delete, or modify anything. Your data stays on your
              device.
            </p>

            <div style={styles.cardLinks}>
              <a href="/privacy" style={styles.cardLink}>
                Privacy Policy
              </a>
              <span style={styles.cardLinkDot}>·</span>
              <a href="/terms" style={styles.cardLink}>
                Terms of Service
              </a>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer style={styles.footer}>
        <p>
          © {new Date().getFullYear()} Email Brief — Open source on{" "}
          <a href="https://github.com/yourusername/email-brief">GitHub</a>
        </p>
      </footer>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  wrapper: {
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
  },

  // Nav
  nav: {
    borderBottom: "1px solid #e5e7eb",
    background: "#ffffff",
  },
  navInner: {
    maxWidth: 1100,
    margin: "0 auto",
    padding: "14px 24px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  logoRow: {
    display: "flex",
    alignItems: "center",
    gap: 10,
  },
  logoIcon: {
    fontSize: 26,
  },
  logoText: {
    fontSize: 18,
    fontWeight: 700,
    color: "#111827",
    letterSpacing: "-0.3px",
  },
  navLinks: {
    display: "flex",
    gap: 24,
  },
  navLink: {
    fontSize: 14,
    color: "#6b7280",
    textDecoration: "none",
    fontWeight: 500,
  },

  // Main
  main: {
    flex: 1,
    maxWidth: 1100,
    margin: "0 auto",
    padding: "64px 24px",
    display: "flex",
    alignItems: "center",
    gap: 64,
    flexWrap: "wrap" as const,
  },

  // Left
  left: {
    flex: 1,
    minWidth: 320,
  },
  heading: {
    fontSize: 42,
    fontWeight: 700,
    lineHeight: 1.15,
    letterSpacing: "-0.5px",
    color: "#111827",
  },
  headingAccent: {
    color: "#2563eb",
  },
  subheading: {
    fontSize: 17,
    color: "#6b7280",
    lineHeight: 1.6,
    marginTop: 16,
    maxWidth: 480,
  },
  features: {
    marginTop: 36,
    display: "flex",
    flexDirection: "column",
    gap: 20,
  },
  feature: {
    display: "flex",
    gap: 14,
    alignItems: "flex-start",
  },
  featureIcon: {
    fontSize: 22,
    marginTop: 2,
  },
  featureDesc: {
    fontSize: 14,
    color: "#6b7280",
    marginTop: 2,
  },

  // Right (card)
  right: {
    flexShrink: 0,
    width: 400,
  },
  card: {
    background: "#ffffff",
    border: "1px solid #e5e7eb",
    borderRadius: 16,
    padding: "36px 32px",
    boxShadow: "0 1px 3px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.06)",
  },
  cardLogoRow: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    marginBottom: 8,
  },
  cardLogo: {
    fontSize: 28,
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: 700,
    color: "#111827",
  },
  cardDesc: {
    fontSize: 15,
    color: "#6b7280",
    lineHeight: 1.5,
    marginBottom: 24,
  },

  // Google button
  googleBtn: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
    width: "100%",
    padding: "12px 20px",
    background: "#ffffff",
    border: "1px solid #dadce0",
    borderRadius: 8,
    fontSize: 15,
    fontWeight: 500,
    color: "#3c4043",
    cursor: "pointer",
    textDecoration: "none",
    transition: "box-shadow 0.2s, background 0.2s",
    boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
  },

  cardDivider: {
    height: 1,
    background: "#e5e7eb",
    margin: "24px 0",
  },

  cardFootnote: {
    fontSize: 13,
    color: "#9ca3af",
    lineHeight: 1.5,
    textAlign: "center" as const,
  },

  cardLinks: {
    display: "flex",
    justifyContent: "center",
    gap: 6,
    marginTop: 16,
  },
  cardLink: {
    fontSize: 12,
    color: "#9ca3af",
  },
  cardLinkDot: {
    fontSize: 12,
    color: "#d1d5db",
  },

  // Footer
  footer: {
    borderTop: "1px solid #e5e7eb",
    padding: "20px 24px",
    textAlign: "center" as const,
    fontSize: 13,
    color: "#9ca3af",
  },
};
