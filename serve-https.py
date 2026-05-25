#!/usr/bin/env python3
"""Serve this folder over HTTPS for iPhone camera testing on your LAN."""

import http.server
import os
import socket
import ssl
import subprocess
import sys

PORT = 8443
DIR = os.path.dirname(os.path.abspath(__file__))
CERT = os.path.join(DIR, "local-cert.pem")
KEY = os.path.join(DIR, "local-key.pem")


def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.0.0.1", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def ensure_cert(ip):
    if os.path.isfile(CERT) and os.path.isfile(KEY):
        return
    print("Creating a self-signed certificate (first run only)...")
    subprocess.check_call(
        [
            "openssl",
            "req",
            "-x509",
            "-newkey",
            "rsa:2048",
            "-keyout",
            KEY,
            "-out",
            CERT,
            "-days",
            "365",
            "-nodes",
            "-subj",
            f"/CN={ip}",
            "-addext",
            f"subjectAltName=IP:{ip},IP:127.0.0.1,DNS:localhost",
        ],
        cwd=DIR,
    )


def main():
    ip = local_ip()
    ensure_cert(ip)

    os.chdir(DIR)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = http.server.HTTPServer(("0.0.0.0", PORT), handler)

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(CERT, KEY)
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

    print(f"Serving HTTPS on port {PORT}")
    print(f"On your iPhone (same Wi-Fi), open:\n  https://{ip}:{PORT}/")
    print("Safari will warn about the certificate — tap Advanced → Proceed / Visit.")
    print("Press Ctrl+C to stop.")
    httpd.serve_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
        sys.exit(0)
