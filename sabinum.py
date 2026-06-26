#!/usr/bin/env python3
# =============================================================
#  SabiNum - Subdomain Enumeration Tool
#  Usage: python sabinum.py -d example.com -w wordlist.txt
# =============================================================

import argparse
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

BANNER = """
  ╔══════════════════════════════════╗
  ║   SabiNum v1.0                   ║
  ║   Subdomain Enumeration Tool     ║
  ╚══════════════════════════════════╝
"""


def resolve(subdomain: str, timeout: int) -> dict | None:
    """
    Try to resolve a subdomain via DNS.
    Returns a result dict on success, or None if not found.
    """
    try:
        socket.setdefaulttimeout(timeout)
        ip = socket.gethostbyname(subdomain)
        return {"subdomain": subdomain, "ip": ip}
    except (socket.gaierror, socket.timeout):
        return None


def load_wordlist(path: str) -> list[str]:
    """Load subdomain prefixes from a text file (one per line)."""
    p = Path(path)
    if not p.exists():
        print(f"[!] Wordlist not found: {path}")
        sys.exit(1)
    words = [line.strip() for line in p.read_text().splitlines() if line.strip()]
    if not words:
        print(f"[!] Wordlist is empty: {path}")
        sys.exit(1)
    return words


def scan(domain: str, wordlist: list[str], threads: int, timeout: int) -> list[dict]:
    """
    Enumerate subdomains using concurrent DNS resolution.
    Prints live progress and returns a list of found subdomains.
    """
    found = []
    total = len(wordlist)
    start = time.time()

    print(f"[*] Target   : {domain}")
    print(f"[*] Words    : {total}")
    print(f"[*] Threads  : {threads}")
    print(f"[*] Timeout  : {timeout}s")
    print(f"[*] Started  : {datetime.now().strftime('%H:%M:%S')}")
    print("─" * 55)

    subdomains = [f"{word}.{domain}" for word in wordlist]

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(resolve, sub, timeout): sub for sub in subdomains}
        done = 0

        for future in as_completed(futures):
            done += 1
            result = future.result()

            elapsed = time.time() - start
            rate = int(done / max(elapsed, 0.1))
            bar_filled = int(done / total * 30)
            bar = "#" * bar_filled + "." * (30 - bar_filled)
            pct = int(done / total * 100)

            # Overwrite the progress line
            print(
                f"\r[{bar}] {pct:3d}%  {done}/{total}  {rate}/s  found:{len(found)}",
                end="",
                flush=True,
            )

            if result:
                found.append(result)
                # Print found result on a new line above the progress bar
                print()
                print(f"  [+] {result['subdomain']:<45} {result['ip']}")

    elapsed = time.time() - start
    print(f"\n{'─' * 55}")
    print(f"[✓] Scan complete in {elapsed:.1f}s")
    print(f"[✓] {len(found)} subdomain(s) found out of {total} checked")

    return found


def save_results(results: list[dict], output_path: str) -> None:
    """Save found subdomains to a file (CSV format: subdomain,ip)."""
    out = Path(output_path)
    lines = [f"{r['subdomain']},{r['ip']}" for r in results]
    out.write_text("\n".join(lines) + "\n")
    print(f"[*] Results saved to: {out}")


def print_summary(results: list[dict]) -> None:
    """Print a formatted summary table of found subdomains."""
    if not results:
        print("\n[-] No subdomains found.")
        return

    print("\n  FOUND SUBDOMAINS:")
    print(f"  {'#':<4}  {'Subdomain':<45}  {'IP Address'}")
    print(f"  {'─'*4}  {'─'*45}  {'─'*15}")
    for i, r in enumerate(results, 1):
        print(f"  {i:<4}  {r['subdomain']:<45}  {r['ip']}")


def main():
    print(BANNER)

    parser = argparse.ArgumentParser(
        description="SabiNum - Fast subdomain enumeration via DNS brute-force",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-d", "--domain",
        required=True,
        help="Target domain (e.g. example.com)"
    )
    parser.add_argument(
        "-w", "--wordlist",
        required=True,
        help="Path to subdomain wordlist (one word per line)"
    )
    parser.add_argument(
        "-t", "--threads",
        default=20,
        type=int,
        help="Number of concurrent threads (default: 20)"
    )
    parser.add_argument(
        "-T", "--timeout",
        default=3,
        type=int,
        help="DNS resolution timeout in seconds (default: 3)"
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Save results to file as CSV (subdomain,ip)"
    )

    args = parser.parse_args()

    # Validate inputs
    if args.threads < 1 or args.threads > 500:
        print("[!] Threads must be between 1 and 500")
        sys.exit(1)

    if args.timeout < 1 or args.timeout > 60:
        print("[!] Timeout must be between 1 and 60 seconds")
        sys.exit(1)

    # Strip leading dot or http(s) from domain if provided
    domain = args.domain.strip().lstrip(".")
    if domain.startswith("http://") or domain.startswith("https://"):
        domain = domain.split("//", 1)[1].rstrip("/")

    wordlist = load_wordlist(args.wordlist)
    results = scan(domain, wordlist, args.threads, args.timeout)

    print_summary(results)

    if args.output and results:
        save_results(results, args.output)


if __name__ == "__main__":
    main()
