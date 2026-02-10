"""
Infrastructure — Security Scanners Package
============================================
Passive-only security assessment modules.  Each scanner performs a single
responsibility (HTTP headers, SSL/TLS, DNS, etc.) and returns a structured
dictionary that higher layers combine.

**Ethical note:** all scanners are passive — no payloads, no port scanning,
no exploitation.  They analyse publicly available information only.
"""
