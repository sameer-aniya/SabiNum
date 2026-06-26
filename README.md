Installation

No external dependencies. Just Python 3.10+.

git clone https://github.com/yourusername/sabinum.git
cd sabinum
python sabinum.py --help


Usage

 python sabinum.py -d <domain> -w <wordlist> [options]

Arguments

FlagLongDescriptionDefault-d--domainTarget domain (e.g. example.com)Required-w--wordlistPath to wordlist file (one word per line)Required-t--threadsNumber of concurrent threads20-T--timeoutDNS resolution timeout in seconds3-o--outputSave results to CSV fileNone


Examples

Basic scan:

 python sabinum.py -d example.com -w wordlist.txt

Fast scan with more threads:

python sabinum.py -d example.com -w wordlist.txt -t 100

Save results to file:

 python sabinum.py -d example.com -w wordlist.txt -o results.csv

Full options:

python sabinum.py -d example.com -w wordlist.txt -t 50 -T 5 -o output.csv


Output

  ╔══════════════════════════════════╗
  ║   SabiNum v1.0                   ║
  ║   Subdomain Enumeration Tool     ║
  ╚══════════════════════════════════╝

[*] Target   : example.com
[*] Words    : 5000
[*] Threads  : 50
[*] Timeout  : 3s
[*] Started  : 14:32:01
───────────────────────────────────────────────────────

  [+] www.example.com                              93.184.216.34
  [+] mail.example.com                             93.184.216.35
  [+] dev.example.com                              93.184.216.36

[########......................] 45%  2250/5000  312/s  found:3

───────────────────────────────────────────────────────
[✓] Scan complete in 8.3s
[✓] 3 subdomain(s) found out of 5000 checked

  FOUND SUBDOMAINS:
  #     Subdomain                                      IP Address
  ────  ─────────────────────────────────────────────  ───────────────
  1     www.example.com                                93.184.216.34
  2     mail.example.com                               93.184.216.35
  3     dev.example.com                                93.184.216.36


Wordlists

You can use any standard subdomain wordlist. Recommended sources:


SecLists - DNS
Assetnote Wordlists



Notes


Only performs passive DNS resolution — no active port scanning
Respects rate limits implicitly via thread/timeout controls
Use only on domains you own or have permission to test



License

MIT License — use freely, contribute openly.
