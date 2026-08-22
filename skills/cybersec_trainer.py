"""
Layra CyberSecurity Training Module
=====================================
Ethical hacking & cybersecurity training tools.
⚠️  AUTHORIZED USE ONLY — Sirf apne ya authorized systems pe use karo.
"""

import logging
import subprocess
import socket
import json
import urllib.request
import urllib.parse
from datetime import datetime

logger = logging.getLogger("layra.cybersec")

WARNING = """
⚠️  ETHICAL USE ONLY
━━━━━━━━━━━━━━━━━━━━━
Yeh tools sirf authorized systems pe use karo.
Bina permission ke kisi ka bhi scan karna ILLEGAL hai.
IT Act 2000, Section 66 — 3 saal jail + ₹5 lakh fine.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


def run_cmd(cmd: str, timeout: int = 30) -> str:
    """Run a shell command safely."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, timeout=timeout
        )
        return result.stdout.strip() or result.stderr.strip() or "No output"
    except subprocess.TimeoutExpired:
        return "⏱️ Command timed out"
    except Exception as e:
        return f"Error: {e}"


class CyberSecTrainer:
    """
    Ethical Hacking Training Tools for Cyber Trainers.
    All tools are for educational & authorized use only.
    """

    # ==========================================
    # Phase 1: RECONNAISSANCE (Recon)
    # ==========================================

    @staticmethod
    def explain_recon() -> str:
        """Explain the Reconnaissance phase of ethical hacking."""
        return """
🔍 PHASE 1 — RECONNAISSANCE (Recon)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hacking ka pehla aur sabse important step.
Target ke baare mein maximum information collect karna.

📚 2 Types:
  1. PASSIVE Recon — Target ko pata nahi chalta
     • WHOIS lookup
     • DNS records
     • Google dorking
     • Social media OSINT
     • Shodan search

  2. ACTIVE Recon — Direct contact with target
     • Ping / traceroute
     • Port scanning (nmap)
     • Banner grabbing
     • OS fingerprinting

🎯 Attacker ka goal:
  • IP addresses dhundhna
  • Open ports & services
  • OS aur software versions
  • Employee names, emails
  • Vulnerabilities identify karna

✅ Tools: nmap, whois, dig, theHarvester, Maltego, Shodan
"""

    @staticmethod
    def whois_lookup(domain: str) -> str:
        """
        WHOIS lookup — domain registration info dekhna.
        Passive recon technique.
        """
        logger.info(f"🔍 WHOIS lookup: {domain}")
        result = run_cmd(f"whois {domain} 2>/dev/null | head -40")
        if not result or "not found" in result.lower():
            # Fallback: online API
            try:
                url = f"https://api.whoisjson.com/v1/{domain}"
                req = urllib.request.Request(url, headers={"User-Agent": "Layra/1.0"})
                data = json.loads(urllib.request.urlopen(req, timeout=8).read())
                registrar = data.get("registrar", "Unknown")
                created = data.get("created", "Unknown")
                expires = data.get("expires", "Unknown")
                return (
                    f"🌐 WHOIS: {domain}\n"
                    f"Registrar: {registrar}\n"
                    f"Created: {created}\n"
                    f"Expires: {expires}"
                )
            except Exception:
                pass
        return f"🌐 WHOIS Lookup — {domain}\n{'━'*40}\n{result}"

    @staticmethod
    def dns_lookup(domain: str) -> str:
        """
        DNS Records lookup — A, MX, NS, TXT records.
        Passive recon — shows server infrastructure.
        """
        logger.info(f"🔍 DNS lookup: {domain}")
        results = [f"📡 DNS Records — {domain}", "━" * 40]

        record_types = {
            "A": "IPv4 Address (web server)",
            "AAAA": "IPv6 Address",
            "MX": "Mail Server",
            "NS": "Name Servers",
            "TXT": "TXT Records (SPF, DKIM, verification)",
            "CNAME": "Canonical Name (aliases)",
        }

        for rtype, description in record_types.items():
            out = run_cmd(f"dig +short {rtype} {domain} 2>/dev/null")
            if out and out != "No output":
                results.append(f"\n🔹 {rtype} ({description}):")
                for line in out.split('\n')[:5]:  # Max 5 lines per type
                    results.append(f"   {line}")

        if len(results) == 2:
            return f"No DNS records found for {domain}"
        return "\n".join(results)

    @staticmethod
    def ip_info(ip_or_domain: str) -> str:
        """
        IP Geolocation & ASN info.
        Shows where a server is located.
        """
        logger.info(f"🔍 IP info: {ip_or_domain}")
        try:
            # Resolve domain to IP first
            try:
                ip = socket.gethostbyname(ip_or_domain)
            except Exception:
                ip = ip_or_domain

            url = f"https://ipapi.co/{ip}/json/"
            req = urllib.request.Request(url, headers={"User-Agent": "Layra/1.0"})
            data = json.loads(urllib.request.urlopen(req, timeout=8).read())

            return (
                f"🌍 IP Information — {ip}\n"
                f"{'━'*40}\n"
                f"🏳️  Country:  {data.get('country_name', 'Unknown')} ({data.get('country_code', '')})\n"
                f"🏙️  City:     {data.get('city', 'Unknown')}, {data.get('region', '')}\n"
                f"🏢 ISP/Org:  {data.get('org', 'Unknown')}\n"
                f"🔌 ASN:      {data.get('asn', 'Unknown')}\n"
                f"📍 Coords:   {data.get('latitude', '')}, {data.get('longitude', '')}\n"
                f"⏰ Timezone: {data.get('timezone', 'Unknown')}"
            )
        except Exception as e:
            return f"IP info failed: {e}"

    @staticmethod
    def port_scan(target: str, scan_type: str = "basic") -> str:
        """
        Port scanning using nmap.
        scan_type: 'basic' (top 100), 'full' (all ports), 'service' (version detection)
        ⚠️ Only scan systems you own or have permission to scan!
        """
        logger.info(f"🔍 Port scan: {target} ({scan_type})")

        # Warn if scanning external IP
        try:
            ip = socket.gethostbyname(target)
            is_private = (
                ip.startswith("192.168.") or
                ip.startswith("10.") or
                ip.startswith("172.") or
                ip == "127.0.0.1" or
                ip == "localhost"
            )
        except Exception:
            is_private = False

        warning = ""
        if not is_private:
            warning = "⚠️  External IP detected — only scan with WRITTEN permission!\n\n"

        # Check if nmap is installed
        nmap_check = run_cmd("which nmap")
        if not nmap_check or "not found" in nmap_check.lower():
            return (
                f"{warning}"
                "❌ nmap not installed.\n"
                "Install karo: brew install nmap\n\n"
                "Manual alternative:\n"
                f"nc -zv {target} 80 443 22 21 25 2>/dev/null"
            )

        # Build nmap command based on type
        if scan_type == "basic":
            cmd = f"nmap -F --open {target} 2>/dev/null"
            desc = "Top 100 ports"
        elif scan_type == "service":
            cmd = f"nmap -sV --open -T4 {target} 2>/dev/null"
            desc = "Service version detection"
        elif scan_type == "os":
            cmd = f"sudo nmap -O --open {target} 2>/dev/null"
            desc = "OS fingerprinting"
        else:
            cmd = f"nmap -F --open {target} 2>/dev/null"
            desc = "Basic scan"

        result = run_cmd(cmd, timeout=60)
        return (
            f"{warning}"
            f"🔍 Port Scan — {target} ({desc})\n"
            f"{'━'*40}\n"
            f"{result}\n\n"
            f"📚 Teaching Note:\n"
            f"Open ports = Potential entry points\n"
            f"Each open port = Running service = Possible vulnerability"
        )

    @staticmethod
    def ping_host(target: str) -> str:
        """Ping a host — basic connectivity check."""
        result = run_cmd(f"ping -c 4 {target} 2>/dev/null")
        return f"📡 Ping — {target}\n{'━'*40}\n{result}"

    @staticmethod
    def traceroute(target: str) -> str:
        """
        Traceroute — shows the path packets take to reach destination.
        Useful for network mapping.
        """
        logger.info(f"🔍 Traceroute: {target}")
        result = run_cmd(f"traceroute -m 15 {target} 2>/dev/null", timeout=30)
        return (
            f"🗺️  Traceroute — {target}\n"
            f"{'━'*40}\n"
            f"{result}\n\n"
            f"📚 Teaching Note:\n"
            f"Har hop = Ek router/gateway\n"
            f"Network topology samajhne mein help karta hai"
        )

    @staticmethod
    def banner_grab(target: str, port: int = 80) -> str:
        """
        Banner Grabbing — service version information collect karna.
        Active recon technique.
        """
        logger.info(f"🔍 Banner grab: {target}:{port}")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((target, port))

            # Send HTTP request for web servers
            if port in [80, 8080, 8000]:
                sock.send(b"HEAD / HTTP/1.0\r\nHost: " + target.encode() + b"\r\n\r\n")
            else:
                sock.send(b"\r\n")

            banner = sock.recv(1024).decode(errors='ignore')
            sock.close()

            return (
                f"🏷️  Banner Grab — {target}:{port}\n"
                f"{'━'*40}\n"
                f"{banner[:500]}\n\n"
                f"📚 Teaching Note:\n"
                f"Banner = Service ki identity\n"
                f"Version pata chal jaye toh CVE search kar sakte hain"
            )
        except Exception as e:
            return f"Banner grab failed for {target}:{port} — {e}"

    @staticmethod
    def subdomain_finder(domain: str) -> str:
        """
        Common subdomains dhundhna using DNS brute force.
        Passive/Active recon.
        """
        logger.info(f"🔍 Subdomain finder: {domain}")
        common_subdomains = [
            "www", "mail", "ftp", "admin", "login", "api",
            "dev", "staging", "test", "portal", "vpn",
            "cdn", "blog", "shop", "secure", "app", "mx",
            "ns1", "ns2", "remote", "dashboard", "beta"
        ]

        found = []
        results = [f"🔎 Subdomain Scan — {domain}", "━" * 40]

        for sub in common_subdomains:
            full_domain = f"{sub}.{domain}"
            try:
                ip = socket.gethostbyname(full_domain)
                found.append(full_domain)
                results.append(f"✅ {full_domain} → {ip}")
            except socket.gaierror:
                pass  # Subdomain doesn't exist

        if not found:
            results.append("❌ No common subdomains found.")
        else:
            results.append(f"\n📊 Found: {len(found)} subdomains")

        results.append(
            "\n📚 Teaching Note:\n"
            "Subdomains = Alag alag attack surfaces\n"
            "Dev/staging subdomains aksar less secured hote hain"
        )
        return "\n".join(results)

    # ==========================================
    # Educational Content
    # ==========================================

    @staticmethod
    def hacking_phases() -> str:
        """Explain all 5 phases of ethical hacking."""
        return """
🎓 ETHICAL HACKING — 5 PHASES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣  RECONNAISSANCE (Recon)
   Target ki information gather karna
   Tools: nmap, whois, theHarvester, Shodan
   Types: Passive (safe) & Active (direct contact)

2️⃣  SCANNING & ENUMERATION
   Open ports, services, vulnerabilities dhundhna
   Tools: nmap, Nessus, OpenVAS, Nikto
   Goal: Attack surface map karna

3️⃣  GAINING ACCESS (Exploitation)
   Vulnerabilities exploit karna
   Tools: Metasploit, SQLmap, Burp Suite
   Techniques: SQLi, XSS, Buffer Overflow, Phishing

4️⃣  MAINTAINING ACCESS
   Persistence establish karna (backdoors, rootkits)
   Goal: Future access ke liye entry point rakhna
   ⚠️ Yeh phase ILLEGAL hai bina permission ke

5️⃣  CLEARING TRACKS
   Evidence mitaana (log deletion etc.)
   ⚠️ Yeh bhi ILLEGAL hai unauthorized systems pe

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📜 LEGAL FRAMEWORK:
• Penetration Testing = Written permission MANDATORY
• Bug Bounty = Company ka program join karo
• CTF = Legal practice environment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    @staticmethod
    def common_attack_types() -> str:
        """Explain common attack types for training."""
        return """
⚔️  COMMON ATTACK TYPES (Educational)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 WEB ATTACKS:
  • SQL Injection — Database query manipulate karna
    Example: ' OR 1=1 --
  • XSS (Cross-Site Scripting) — Malicious JS inject karna
  • CSRF — User ki identity se request bhejwana
  • File Upload Bypass — Malicious file upload karna

🔌 NETWORK ATTACKS:
  • MITM (Man-in-the-Middle) — Traffic intercept karna
  • ARP Spoofing — Network mein khud ko router banana
  • DNS Spoofing — DNS responses manipulate karna
  • DoS/DDoS — Service ko unavailable banana

🔐 PASSWORD ATTACKS:
  • Brute Force — Sab combinations try karna
  • Dictionary Attack — Common passwords try karna
  • Credential Stuffing — Leaked passwords use karna
  • Rainbow Table — Pre-computed hash lookup

🧠 SOCIAL ENGINEERING:
  • Phishing — Fake emails/websites
  • Pretexting — Fake identity banake info lena
  • Baiting — Infected USB/files

📱 SYSTEM ATTACKS:
  • Buffer Overflow — Memory boundary exceed karna
  • Privilege Escalation — Low → High privileges
  • Rootkit — Deep system access hide karna

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️  DEFENSE: Each attack ka ek defense hai!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    @staticmethod
    def ctf_resources() -> str:
        """CTF practice platforms for students."""
        return """
🏆 CTF & PRACTICE PLATFORMS (Legal & Free)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 BEGINNER:
  • TryHackMe.com — Guided rooms, step-by-step
  • PicoCTF.org — Students ke liye best
  • HackThisSite.org — Classic challenges

🟡 INTERMEDIATE:
  • HackTheBox.com — Real-world machines
  • VulnHub.com — Downloadable VMs
  • PortSwigger Web Academy — Web security free course

🔴 ADVANCED:
  • PentesterLab.com — Pro web pentesting
  • SANS CTF — Professional level
  • DEF CON CTF — World's toughest

📚 FREE CERTIFICATIONS:
  • CEH (EC-Council)
  • OSCP (Offensive Security) ← Industry gold standard
  • CompTIA Security+
  • Google Cybersecurity Certificate (Coursera — FREE)

🛠️  MUST-LEARN TOOLS:
  • Kali Linux — Ethical hacking OS
  • Burp Suite — Web app testing
  • Metasploit — Exploitation framework
  • Wireshark — Packet analysis
  • Nmap — Port scanning
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


# ============================================================
# PRACTICAL TOOLS — CyberSecPractical
# ============================================================

class CyberSecPractical:
    """
    Hands-on practical cybersecurity training tools.
    Educational & authorized use only.
    """

    # ==========================================
    # Password Analysis
    # ==========================================

    @staticmethod
    def check_password_strength(password: str) -> str:
        """Analyze password strength and explain why."""
        import re
        score = 0
        feedback = []
        issues = []

        if len(password) >= 8:   score += 1
        else: issues.append("❌ 8+ characters chahiye")

        if len(password) >= 12:  score += 1
        else: issues.append("⚠️  12+ characters aur better hoga")

        if len(password) >= 16:  score += 1

        if re.search(r'[A-Z]', password): score += 1
        else: issues.append("❌ Uppercase letter missing (A-Z)")

        if re.search(r'[a-z]', password): score += 1
        else: issues.append("❌ Lowercase letter missing (a-z)")

        if re.search(r'\d', password): score += 1
        else: issues.append("❌ Number missing (0-9)")

        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password): score += 2
        else: issues.append("❌ Special character missing (!@#$...)")

        common_passwords = ['password', '123456', 'admin', 'qwerty', 'letmein', 'welcome', 'monkey']
        if password.lower() in common_passwords:
            score = 0
            issues.append("🔴 COMMON PASSWORD — immediately change karo!")

        # Score mapping
        if score <= 2:   strength = "🔴 WEAK"
        elif score <= 4: strength = "🟡 MEDIUM"
        elif score <= 6: strength = "🟢 STRONG"
        else:            strength = "💪 VERY STRONG"

        # Time to crack estimate
        charset = 0
        if re.search(r'[a-z]', password): charset += 26
        if re.search(r'[A-Z]', password): charset += 26
        if re.search(r'\d', password): charset += 10
        if re.search(r'[!@#$%^&*]', password): charset += 32

        combinations = charset ** len(password) if charset > 0 else 0
        if combinations > 10**18:   crack_time = "Billions of years"
        elif combinations > 10**12: crack_time = "Thousands of years"
        elif combinations > 10**9:  crack_time = "Several years"
        elif combinations > 10**6:  crack_time = "Hours to days"
        else:                        crack_time = "Minutes or less"

        result = [
            f"🔐 Password Strength Analysis",
            f"{'━'*40}",
            f"Password: {'*' * len(password)} ({len(password)} chars)",
            f"Strength: {strength} (Score: {score}/8)",
            f"Crack Time: ~{crack_time}",
        ]
        if issues:
            result.append(f"\n📋 Issues:")
            result.extend(f"  {i}" for i in issues)

        result.append(f"\n📚 Teaching Note:")
        result.append("Brute force = Har combination try karna")
        result.append(f"Combinations possible: {combinations:,.0f}")
        return "\n".join(result)

    @staticmethod
    def generate_hash(text: str) -> str:
        """Generate multiple hash types for given text — for teaching."""
        import hashlib
        return (
            f"🔑 Hash Generation — '{text}'\n"
            f"{'━'*40}\n"
            f"MD5:    {hashlib.md5(text.encode()).hexdigest()}\n"
            f"SHA1:   {hashlib.sha1(text.encode()).hexdigest()}\n"
            f"SHA256: {hashlib.sha256(text.encode()).hexdigest()}\n"
            f"SHA512: {hashlib.sha512(text.encode()).hexdigest()[:64]}...\n\n"
            f"📚 Teaching Note:\n"
            f"• MD5/SHA1 — BROKEN, collision attacks possible\n"
            f"• SHA256/SHA512 — Current standard\n"
            f"• Passwords NEVER store in MD5! Use bcrypt/argon2"
        )

    @staticmethod
    def identify_hash(hash_str: str) -> str:
        """Identify hash type by length and format."""
        h = hash_str.strip().lower()
        length = len(h)
        import re

        is_hex = bool(re.match(r'^[0-9a-f]+$', h))

        if length == 32 and is_hex:
            htype = "MD5 (128-bit) — Weak, avoid!"
        elif length == 40 and is_hex:
            htype = "SHA1 (160-bit) — Weak, avoid!"
        elif length == 56 and is_hex:
            htype = "SHA224"
        elif length == 64 and is_hex:
            htype = "SHA256 — Good"
        elif length == 96 and is_hex:
            htype = "SHA384"
        elif length == 128 and is_hex:
            htype = "SHA512 — Very good"
        elif h.startswith('$2b$') or h.startswith('$2a$'):
            htype = "bcrypt — Password hashing, excellent!"
        elif h.startswith('$argon2'):
            htype = "Argon2 — Best for passwords!"
        elif h.startswith('$6$'):
            htype = "SHA512-crypt (Linux /etc/shadow)"
        elif h.startswith('$1$'):
            htype = "MD5-crypt — Weak!"
        else:
            htype = f"Unknown format (length: {length})"

        return (
            f"🔍 Hash Identification\n"
            f"{'━'*40}\n"
            f"Hash: {hash_str[:50]}...\n"
            f"Type: {htype}\n\n"
            f"📚 Use hashid or hash-identifier tool for more"
        )

    # ==========================================
    # Web Security Tools
    # ==========================================

    @staticmethod
    def check_http_headers(url: str) -> str:
        """Analyze security headers of a website — OWASP check."""
        import urllib.request, ssl
        if not url.startswith('http'):
            url = 'https://' + url

        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req, timeout=8, context=ctx)
            headers = dict(response.headers)

            security_headers = {
                'Strict-Transport-Security': ('HSTS — HTTPS enforce karta hai', True),
                'Content-Security-Policy': ('CSP — XSS attacks rokta hai', True),
                'X-Frame-Options': ('Clickjacking rokta hai', True),
                'X-Content-Type-Options': ('MIME sniffing rokta hai', True),
                'Referrer-Policy': ('Referrer info control karta hai', False),
                'Permissions-Policy': ('Browser features control', False),
                'X-XSS-Protection': ('Old XSS protection (deprecated)', False),
                'Server': ('Server info leak karta hai (remove karo!)', False),
            }

            results = [f"🛡️  Security Headers — {url}", "━"*45]
            missing_critical = []

            for header, (desc, is_critical) in security_headers.items():
                found = next((v for k, v in headers.items() if k.lower() == header.lower()), None)
                if found:
                    status = "✅"
                    results.append(f"{status} {header}: {found[:60]}")
                else:
                    status = "🔴" if is_critical else "⚠️ "
                    results.append(f"{status} {header}: MISSING — {desc}")
                    if is_critical:
                        missing_critical.append(header)

            results.append(f"\n📊 Security Score: {(len(security_headers) - len(missing_critical))}/{len(security_headers)}")
            if missing_critical:
                results.append(f"⚠️  Critical missing: {', '.join(missing_critical)}")
            results.append("\n📚 OWASP Secure Headers Project: owasp.org/www-project-secure-headers/")
            return "\n".join(results)
        except Exception as e:
            return f"Header check failed for {url}: {e}"

    @staticmethod
    def check_ssl_certificate(domain: str) -> str:
        """Check SSL/TLS certificate details."""
        import ssl, socket
        from datetime import datetime

        domain = domain.replace('https://', '').replace('http://', '').split('/')[0]
        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
                s.settimeout(8)
                s.connect((domain, 443))
                cert = s.getpeercert()

            subject = dict(x[0] for x in cert.get('subject', []))
            issuer = dict(x[0] for x in cert.get('issuer', []))
            san = [x[1] for x in cert.get('subjectAltName', [])]

            not_after = cert.get('notAfter', '')
            try:
                expiry = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                days_left = (expiry - datetime.now()).days
                expiry_str = f"{expiry.strftime('%d %b %Y')} ({days_left} days left)"
                expiry_icon = "✅" if days_left > 30 else ("⚠️" if days_left > 0 else "🔴 EXPIRED!")
            except Exception:
                expiry_str = not_after
                expiry_icon = "❓"

            return (
                f"🔒 SSL Certificate — {domain}\n"
                f"{'━'*40}\n"
                f"Common Name: {subject.get('commonName', 'N/A')}\n"
                f"Issuer: {issuer.get('organizationName', 'N/A')}\n"
                f"Expiry: {expiry_icon} {expiry_str}\n"
                f"Protocol: {s.version() if hasattr(s, 'version') else 'TLS'}\n"
                f"SANs: {', '.join(san[:5])}\n\n"
                f"📚 Teaching Note:\n"
                f"• Self-signed = Browser warning\n"
                f"• Expired cert = Man-in-Middle risk\n"
                f"• TLS 1.0/1.1 = Vulnerable, upgrade to 1.3"
            )
        except Exception as e:
            return f"SSL check failed for {domain}: {e}"

    @staticmethod
    def google_dork(query_type: str, target: str = "") -> str:
        """Generate Google Dork queries for OSINT."""
        dorks = {
            "files": [
                f'site:{target} filetype:pdf',
                f'site:{target} filetype:xlsx OR filetype:csv',
                f'site:{target} filetype:sql',
                f'site:{target} filetype:log',
                f'site:{target} filetype:env OR filetype:config',
            ],
            "login": [
                f'site:{target} inurl:login OR inurl:admin OR inurl:signin',
                f'site:{target} intitle:"login" OR intitle:"admin panel"',
                f'site:{target} inurl:wp-admin',
                f'site:{target} inurl:phpmyadmin',
            ],
            "errors": [
                f'site:{target} "SQL syntax" OR "mysql_fetch" OR "ORA-"',
                f'site:{target} "Warning: mysql" OR "PHP Error"',
                f'site:{target} intitle:"Index of /"',
            ],
            "sensitive": [
                f'site:{target} "password" filetype:txt',
                f'site:{target} inurl:".git" OR inurl:".env"',
                f'"@{target}" email list',
                f'site:{target} "confidential" OR "internal use only"',
            ],
            "cameras": [
                'inurl:"/view/index.shtml"',
                'intitle:"webcamXP 5" inurl:8080',
                'intitle:"IP Camera" inurl:LvAppl',
            ],
        }

        results = [f"🔍 Google Dork Queries — {query_type.upper()}", "━"*45]

        if query_type.lower() in dorks:
            results.append(f"Target: {target or 'any'}\n")
            for dork in dorks[query_type.lower()]:
                results.append(f"  {dork}")
                search_url = f"https://google.com/search?q={urllib.parse.quote(dork)}"
                results.append(f"  🔗 {search_url[:80]}")
                results.append("")
        else:
            types = list(dorks.keys())
            results.append(f"Available types: {', '.join(types)}")

        results.append("📚 Teaching Note:")
        results.append("Google Dorks = Sensitive info publicly indexed hai")
        results.append("Apni site ke liye run karo, dusron ki nahi!")
        return "\n".join(results)

    # ==========================================
    # Email Security
    # ==========================================

    @staticmethod
    def analyze_email_headers(headers_text: str) -> str:
        """Analyze email headers to detect phishing."""
        import re
        lines = headers_text.strip().split('\n')
        analysis = ["📧 Email Header Analysis", "━"*40]
        warnings = []

        # Extract key headers
        from_addr = next((l for l in lines if l.lower().startswith('from:')), '')
        reply_to = next((l for l in lines if l.lower().startswith('reply-to:')), '')
        received = [l for l in lines if l.lower().startswith('received:')]
        spf = next((l for l in lines if 'spf' in l.lower()), '')
        dkim = next((l for l in lines if 'dkim' in l.lower()), '')

        if from_addr:
            analysis.append(f"From: {from_addr[5:].strip()}")
        if reply_to:
            analysis.append(f"Reply-To: {reply_to[9:].strip()}")
            if from_addr and reply_to:
                from_domain = re.search(r'@([\w.]+)', from_addr)
                reply_domain = re.search(r'@([\w.]+)', reply_to)
                if from_domain and reply_domain and from_domain.group(1) != reply_domain.group(1):
                    warnings.append("🔴 Reply-To domain differs from From domain — PHISHING SIGN!")

        if received:
            analysis.append(f"\nHops (email ka safar):")
            for i, hop in enumerate(received[:5]):
                analysis.append(f"  Hop {i+1}: {hop[9:60].strip()}")

        if 'pass' in spf.lower():
            analysis.append("✅ SPF: PASS")
        elif spf:
            warnings.append("⚠️  SPF check failed — email spoofed ho sakta hai")

        if 'pass' in dkim.lower():
            analysis.append("✅ DKIM: PASS")
        elif dkim:
            warnings.append("⚠️  DKIM check failed — content tampered ho sakta hai")

        if warnings:
            analysis.append("\n🚨 WARNINGS:")
            analysis.extend(warnings)
        else:
            analysis.append("\n✅ No obvious phishing indicators found")

        analysis.append("\n📚 Teaching Note:")
        analysis.append("Phishing signs: Different reply-to, SPF fail, urgent language")
        return "\n".join(analysis)

    @staticmethod
    def check_email_spf_dkim(domain: str) -> str:
        """Check SPF and DKIM records for a domain."""
        results = [f"📧 Email Security Check — {domain}", "━"*40]

        spf = run_cmd(f"dig +short TXT {domain} | grep spf")
        if spf:
            results.append(f"✅ SPF Record Found:\n  {spf}")
            if 'fail' in spf:   results.append("  ⚠️  Hard fail policy — good!")
            elif 'softfail' in spf: results.append("  ⚠️  Soft fail — strengthen karo")
            elif 'all' in spf:  results.append("  ✅ Policy set")
        else:
            results.append("🔴 SPF Record: MISSING — Email spoofing possible!")

        dkim = run_cmd(f"dig +short TXT default._domainkey.{domain}")
        if dkim and 'v=DKIM' in dkim:
            results.append(f"\n✅ DKIM Found (default selector)")
        else:
            results.append(f"\n⚠️  DKIM: Not found on default selector")

        dmarc = run_cmd(f"dig +short TXT _dmarc.{domain}")
        if dmarc:
            results.append(f"\n✅ DMARC Found:\n  {dmarc}")
        else:
            results.append(f"\n🔴 DMARC: MISSING — Spoofing protection incomplete!")

        results.append("\n📚 SPF + DKIM + DMARC = Email spoofing se bachav ka trifecta")
        return "\n".join(results)

    # ==========================================
    # Encoding / Decoding Tools
    # ==========================================

    @staticmethod
    def encode_decode(text: str, operation: str = "all") -> str:
        """Encode/decode text in various formats."""
        import base64

        results = [f"🔄 Encoding Tools — '{text[:30]}'", "━"*40]

        try:
            if operation in ["encode", "all"]:
                results.append("📤 ENCODE:")
                results.append(f"  Base64:  {base64.b64encode(text.encode()).decode()}")
                results.append(f"  URL:     {urllib.parse.quote(text)}")
                results.append(f"  Hex:     {text.encode().hex()}")
                results.append(f"  ROT13:   {text.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', 'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'))}")
                results.append(f"  Binary:  {' '.join(format(ord(c), '08b') for c in text[:20])}")

            if operation in ["decode", "all"]:
                results.append("\n📥 DECODE attempts:")
                try:
                    results.append(f"  Base64→: {base64.b64decode(text).decode(errors='ignore')}")
                except Exception:
                    pass
                try:
                    results.append(f"  URL→:    {urllib.parse.unquote(text)}")
                except Exception:
                    pass
                try:
                    if all(c in '0123456789abcdefABCDEF' for c in text) and len(text) % 2 == 0:
                        results.append(f"  Hex→:    {bytes.fromhex(text).decode(errors='ignore')}")
                except Exception:
                    pass

        except Exception as e:
            results.append(f"Error: {e}")

        results.append("\n📚 Attackers use encoding to bypass WAF/filters")
        return "\n".join(results)

    # ==========================================
    # OSINT Tools
    # ==========================================

    @staticmethod
    def username_osint(username: str) -> str:
        """Check username across platforms — OSINT."""
        platforms = {
            "GitHub":    f"https://github.com/{username}",
            "Twitter/X": f"https://twitter.com/{username}",
            "Instagram": f"https://instagram.com/{username}",
            "LinkedIn":  f"https://linkedin.com/in/{username}",
            "Reddit":    f"https://reddit.com/user/{username}",
            "YouTube":   f"https://youtube.com/@{username}",
            "TikTok":    f"https://tiktok.com/@{username}",
            "HackTheBox":f"https://hackthebox.com/profile/{username}",
            "TryHackMe": f"https://tryhackme.com/p/{username}",
        }
        results = [f"🕵️  Username OSINT — '{username}'", "━"*40]
        results.append("Check these URLs (manual verification needed):\n")
        for platform, url in platforms.items():
            results.append(f"  📌 {platform:12} {url}")

        results.append("\n🛠️  Advanced Tool: sherlock")
        results.append("  pip install sherlock-project")
        results.append(f"  sherlock {username}")
        results.append("\n📚 Username reuse = Common OPSEC mistake")
        return "\n".join(results)

    @staticmethod
    def email_osint(email: str) -> str:
        """Email OSINT — check breach status and info."""
        import re
        domain = email.split('@')[-1] if '@' in email else email
        username = email.split('@')[0] if '@' in email else email

        results = [f"📧 Email OSINT — {email}", "━"*40]

        # Basic validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            results.append("⚠️  Invalid email format")
        else:
            results.append(f"✅ Valid email format")

        # Check domain MX records
        mx = run_cmd(f"dig +short MX {domain}")
        if mx:
            results.append(f"✅ Mail server exists: {mx[:60]}")
        else:
            results.append(f"⚠️  No MX record for {domain} — possibly fake")

        results.append(f"\n🔍 Manual OSINT steps:")
        results.append(f"  1. Have I Been Pwned: https://haveibeenpwned.com")
        results.append(f"     (Search: {email})")
        results.append(f"  2. Hunter.io: https://hunter.io/email-verifier")
        results.append(f"  3. Google Dork: \"{email}\" site:pastebin.com")
        results.append(f"  4. LinkedIn search: {username}")

        results.append(f"\n📚 Breach databases mein emails = Credential stuffing attacks ka source")
        return "\n".join(results)

    # ==========================================
    # Local Lab Guide
    # ==========================================

    @staticmethod
    def setup_lab_guide() -> str:
        """Complete guide for setting up a hacking lab."""
        return """
🏠 ETHICAL HACKING LAB SETUP GUIDE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 STEP 1: Kali Linux VM
  • Download: kali.org/get-kali
  • VirtualBox ya VMware pe install karo
  • 50GB disk, 4GB RAM recommended
  • Host-Only Adapter use karo (isolated network)

📌 STEP 2: Vulnerable Target VMs (Legal targets!)
  • Metasploitable2 — Classic vulnerable Linux
    Download: sourceforge.net/projects/metasploitable/
  • DVWA (Damn Vulnerable Web App)
    docker run -d -p 80:80 vulnerables/web-dvwa
  • VulnHub.com — 100s of VMs
  • TryHackMe OpenVPN — Cloud practice

📌 STEP 3: Essential Tools (Kali mein pre-installed)
  🔍 Recon:     nmap, theHarvester, maltego, shodan
  🌐 Web:       burpsuite, nikto, sqlmap, gobuster
  🔐 Password:  hashcat, john, hydra, medusa
  🕵️  MITM:     wireshark, ettercap, bettercap
  💥 Exploit:   metasploit, searchsploit

📌 STEP 4: Lab Network Topology
  ┌─────────────┐     ┌──────────────────┐
  │  Kali Linux │────▶│ Metasploitable2  │
  │ (Attacker)  │     │   (Victim)       │
  └─────────────┘     └──────────────────┘
       │                      │
  ┌────▼──────────────────────▼──────┐
  │     Host-Only Network (isolated) │
  │         192.168.56.0/24          │
  └──────────────────────────────────┘

📌 STEP 5: Practice Path
  Week 1-2: Nmap, WHOIS, DNS — Recon
  Week 3-4: Metasploit basics — Exploitation
  Week 5-6: Burp Suite — Web hacking
  Week 7-8: Privilege escalation
  Week 9+:  CTF challenges (TryHackMe, HTB)

⚠️  REMEMBER: Sirf apne lab mein practice karo!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    @staticmethod
    def sql_injection_demo() -> str:
        """SQL Injection — theory + payloads for teaching."""
        return """
💉 SQL INJECTION — Practical Guide
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 WHAT IS IT?
  User input mein SQL code inject karna
  Ye code database pe execute ho jaata hai

🔬 EXAMPLE — Vulnerable Login Code:
  query = "SELECT * FROM users WHERE 
           username='" + username + "' 
           AND password='" + password + "'"

🎯 PAYLOADS (DVWA ya CTF pe try karo):

  1. Authentication Bypass:
     Username: admin' --
     Password: anything
     ❌ Query banta hai: ... WHERE username='admin' --' AND password='...'
     ✅ -- se baaki query comment ho jaati hai!

  2. UNION Based:
     ' UNION SELECT 1,2,3 --
     ' UNION SELECT username,password,3 FROM users --

  3. Boolean Based (Blind):
     ' AND 1=1 --   (True — data aata hai)
     ' AND 1=2 --   (False — data nahi aata)

  4. Time Based (Blind):
     ' AND SLEEP(5) --   (5 sec delay = vulnerable!)

🛠️  TOOL: sqlmap (automated)
  sqlmap -u "http://target/login?id=1" --dbs
  ⚠️  Sirf authorized sites pe!

🛡️  DEFENSE:
  ✅ Prepared Statements (Parameterized Queries)
  ✅ Input validation & sanitization
  ✅ WAF (Web Application Firewall)
  ✅ Least privilege database user

🔗 Practice: DVWA, WebGoat, HackTheBox
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
