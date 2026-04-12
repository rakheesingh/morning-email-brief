"""
Demo: Before vs After ASC token optimization in email-brief.
Run: python3 -m email_brief.demo_asc
"""
import sys
sys.path.insert(0, "/Users/rasingh/open-source/asc")

from asc.pipeline import ASCPipeline

SAMPLE_EMAILS = [
    "URGENT: Production API is returning 500 errors for all customer requests. Database connection pool exhausted. Need your help to scale up instances ASAP before the 3 PM SLA deadline.",
    "Hi Sarah, the Q2 budget proposal needs your sign-off by end of week. I've attached the updated spreadsheet with the marketing allocations. Let me know if you have questions.",
    "Dear Customer, Rs.2500.00 has been debited from account 9474 to VPA merchant@upi on 08-04-26. Your UPI transaction reference number is 609495804513. If you did not authorize this, call 1800-xxx.",
    "Your HDFC Bank account statement for March 2026 is ready. Log in to net banking to view and download your statement. This is an automated message.",
    "Transaction alert from IDFC FIRST Bank. Your A/C XXXXXXX6013 has been debited by INR 80.00 on 08/04/2026 18:38. New balance is INR 57314.50CR.",
    "Weekly newsletter: Top 10 React patterns every developer should know. Plus: TypeScript 6.0 features, cloud cost optimization tips. Unsubscribe here.",
    "50% off on all electronics! Myntra Fashion Carnival is LIVE. Shop now and get additional 10% cashback. Offer valid till midnight. Unsubscribe from promotional emails.",
    "Doctors discovered a hole in my newborn's intestine. Please help us save our baby. Donate now at milaap.org. Every rupee counts. Share this with your friends.",
    "Your daily horoscope for Sagittarius: The stars align for financial growth today. Lucky color: blue. Lucky number: 7. Read more at tarot.com.",
    "Canada Immigration: April Draw Predictions. CRS threshold dropping - act before it rises. Get your free eligibility assessment today. Unsubscribe.",
    "Rakhee, check out these 14 matches recommended for you today! Manish Kumar, 30 yrs, B.Tech, Software Professional. View profile on BharatMatrimony.com.",
    "Sprint planning meeting moved from 2 PM to 4 PM today. New agenda includes Q3 roadmap discussion. Please review the attached priorities document before the meeting.",
    "Re: PR #482 - Need your review before deploy. The migration script is ready but I found a potential race condition in the connection pooling. Can you take a look today?",
    "Hi team, the client demo is tomorrow at 10 AM. We need to fix the dashboard loading issue before then. Assigning this as P0. Who can pick this up?",
    "Akshaya Tritiya offers are live! Get up to Rs 20000 off on plain gold jewellery at BlueStone. Free shipping. Shop now. Unsubscribe.",
]

KNOWN_PATTERNS = [
    "Your order has been shipped and will arrive in 3-5 business days",
    "Your payment has been processed successfully",
    "Monthly bank statement is now available",
    "Transaction alert debited from account",
    "Weekly newsletter digest unsubscribe",
    "Promotional offer sale discount unsubscribe",
    "Dear Customer notification automated message",
]


def main():
    print("\n" + "=" * 70)
    print("  BEFORE vs AFTER: ASC Token Optimization")
    print("=" * 70)

    # --- BEFORE: No compression ---
    before_tokens = sum(len(e.split()) for e in SAMPLE_EMAILS)
    print(f"\n  BEFORE (no compression):")
    print(f"  Emails: {len(SAMPLE_EMAILS)}")
    print(f"  Total tokens sent to LLM: {before_tokens}")
    print(f"  LLM API calls needed: 1 (all in one prompt)")

    # --- AFTER: With ASC ---
    pipeline = ASCPipeline(task="classification")
    pipeline.fit(KNOWN_PATTERNS)

    result = pipeline.compress(items=SAMPLE_EMAILS)

    print(f"\n  AFTER (with ASC, Run 1 — cold cache):")
    print(f"  Emails: {result.stats['total_items']}")
    print(f"  Cache hits (skipped entirely): {result.stats['cache_hits']}")
    print(f"  Tokens BEFORE compression: {result.stats['original_tokens']}")
    print(f"  Tokens AFTER compression: {result.stats['final_tokens']}")
    print(f"  Tokens saved: {result.stats['tokens_saved']}")
    print(f"  Compression: {result.stats['compression_ratio']:.1%}")

    # --- Per-email breakdown ---
    print(f"\n  {'#':<3} {'Entropy':>8} {'Level':>8} {'Original':>9} {'After':>7} {'Saved':>7}  Source")
    print(f"  {'-'*3} {'-'*8} {'-'*8} {'-'*9} {'-'*7} {'-'*7}  {'-'*10}")

    for i, item in enumerate(result.items):
        orig = len(item.original_text.split())
        if item.source == "cache":
            after = 0
        elif item.mask_result:
            after = item.mask_result.compressed_tokens
        else:
            after = orig
        saved = orig - after
        print(f"  {i+1:<3} {item.entropy.score:>8.3f} {item.entropy.level:>8} {orig:>8} t {after:>6} t {saved:>6} t  {item.source}")

    # --- Feed back results and run again ---
    fake_results = [
        {"priority": "urgent"}, {"priority": "important"}, {"priority": "fyi"},
        {"priority": "fyi"}, {"priority": "fyi"}, {"priority": "low"},
        {"priority": "low"}, {"priority": "low"}, {"priority": "low"},
        {"priority": "low"}, {"priority": "low"}, {"priority": "important"},
        {"priority": "important"}, {"priority": "urgent"}, {"priority": "low"},
    ]
    pipeline.feedback(items=SAMPLE_EMAILS, results=fake_results, confidence=0.9)

    result2 = pipeline.compress(items=SAMPLE_EMAILS)

    print(f"\n  AFTER (with ASC, Run 2 — warm cache):")
    print(f"  Cache hits: {result2.stats['cache_hits']} / {result2.stats['total_items']}")
    print(f"  Tokens BEFORE: {result2.stats['original_tokens']}")
    print(f"  Tokens AFTER: {result2.stats['final_tokens']}")
    print(f"  Compression: {result2.stats['compression_ratio']:.1%}")

    # --- Mixed workload ---
    new_emails = [
        "CRITICAL: SSL cert expiring in 2 hours. All HTTPS will fail. Fix now.",
        "Your Zomato order is out for delivery. Track it live in the app.",
        "New course on Udemy: Master Docker in 24 hours. 95% off today only. Unsubscribe.",
    ]
    mixed = SAMPLE_EMAILS[:5] + new_emails
    result3 = pipeline.compress(items=mixed)

    print(f"\n  AFTER (with ASC, Run 3 — mixed: 5 cached + 3 new):")
    print(f"  Cache hits: {result3.stats['cache_hits']} / {result3.stats['total_items']}")
    print(f"  Tokens BEFORE: {result3.stats['original_tokens']}")
    print(f"  Tokens AFTER: {result3.stats['final_tokens']}")
    print(f"  Compression: {result3.stats['compression_ratio']:.1%}")

    # --- Final comparison ---
    print(f"\n  {'='*60}")
    print(f"  SUMMARY: Token Usage Comparison")
    print(f"  {'='*60}")
    print(f"  {'Scenario':<35} {'Tokens':>8} {'Savings':>10}")
    print(f"  {'-'*35} {'-'*8} {'-'*10}")
    print(f"  {'Without ASC (baseline)':<35} {before_tokens:>8}       -")
    print(f"  {'With ASC (cold cache)':<35} {result.stats['final_tokens']:>8} {result.stats['compression_ratio']:>9.1%}")
    print(f"  {'With ASC (warm cache)':<35} {result2.stats['final_tokens']:>8} {result2.stats['compression_ratio']:>9.1%}")
    print(f"  {'With ASC (mixed workload)':<35} {result3.stats['final_tokens']:>8} {result3.stats['compression_ratio']:>9.1%}")
    print()


if __name__ == "__main__":
    main()
