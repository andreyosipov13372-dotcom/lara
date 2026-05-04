#!/usr/bin/env python3
"""
Remote deployment script - deploys webclip-installer.py to Oracle Cloud server
Uses HTTP POST to update the server without SSH
"""

import requests
import time

SERVER_URL = "http://79.72.18.198:8080"
CLOUDFLARE_URL = "https://liver-vintage-marco-thus.trycloudflare.com"

WEBCLIP_CODE = '''#!/usr/bin/env python3
from flask import Flask, render_template_string, redirect, jsonify
app = Flask(__name__)
IPA_URL = "https://github.com/rooootdev/lara/releases/latest/download/lara.ipa"

HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LARA Installer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px;
        }
        .container { background: white; border-radius: 20px; padding: 40px; max-width: 500px; width: 100%; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        .logo { text-align: center; font-size: 80px; margin-bottom: 20px; }
        h1 { color: #333; margin-bottom: 10px; text-align: center; }
        .subtitle { color: #666; margin-bottom: 30px; font-size: 14px; text-align: center; }
        .install-option { background: #f8f9fa; border-radius: 12px; padding: 20px; margin-bottom: 15px; cursor: pointer; transition: all 0.3s; border: 2px solid transparent; }
        .install-option:hover { background: #e9ecef; border-color: #667eea; transform: translateY(-2px); }
        .option-icon { font-size: 32px; margin-bottom: 10px; }
        .option-title { font-weight: 600; color: #333; margin-bottom: 5px; }
        .option-desc { font-size: 13px; color: #666; }
        .info-box { background: #fff3cd; border: 1px solid #ffc107; border-radius: 10px; padding: 15px; margin-top: 20px; font-size: 13px; }
        .info-box strong { display: block; margin-bottom: 8px; }
        a { text-decoration: none; color: inherit; display: block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🚀</div>
        <h1>LARA Installer</h1>
        <p class="subtitle">Выбери способ установки</p>
        <a href="scarlet://install={{ ipa_url }}">
            <div class="install-option">
                <div class="option-icon">🔴</div>
                <div class="option-title">Установить через Scarlet</div>
                <div class="option-desc">Если у тебя установлен Scarlet - нажми сюда.<br>Scarlet автоматически подпишет и установит LARA.</div>
            </div>
        </a>
        <a href="apple-magnifier://install?url={{ ipa_url }}">
            <div class="install-option">
                <div class="option-icon">🛒</div>
                <div class="option-title">Установить через TrollStore</div>
                <div class="option-desc">Если у тебя установлен TrollStore - нажми сюда.<br>TrollStore установит LARA навсегда без подписи.</div>
            </div>
        </a>
        <a href="esign://import?url={{ ipa_url }}">
            <div class="install-option">
                <div class="option-icon">✍️</div>
                <div class="option-title">Установить через ESign</div>
                <div class="option-desc">Если у тебя установлен ESign - нажми сюда.<br>ESign подпишет с твоим сертификатом.</div>
            </div>
        </a>
        <a href="{{ ipa_url }}" download>
            <div class="install-option">
                <div class="option-icon">📥</div>
                <div class="option-title">Скачать IPA напрямую</div>
                <div class="option-desc">Скачай IPA и установи через AltStore/Sideloadly.<br>Требуется компьютер.</div>
            </div>
        </a>
        <div class="info-box">
            <strong>ℹ️ Как это работает:</strong>
            • Нажми на любой способ установки<br>
            • Если приложение установлено - оно откроется<br>
            • Если нет - скачай его сначала<br><br>
            <strong>📱 Рекомендуем:</strong>
            • Scarlet (самый простой)<br>
            • TrollStore (если уже установлен)<br>
            • ESign (если есть сертификат)<br><br>
            <strong>🔗 Где скачать:</strong>
            • Scarlet: <a href="https://usescarlet.com" style="color: #667eea;">usescarlet.com</a><br>
            • ESign: <a href="https://esign.yyyue.xyz" style="color: #667eea;">esign.yyyue.xyz</a>
        </div>
    </div>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML, ipa_url=IPA_URL)

@app.route('/install')
def install():
    return redirect('/')

@app.route('/download')
def download():
    return redirect(IPA_URL)

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'lara-webclip-installer'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
'''

def check_server():
    """Check if server is responding"""
    try:
        r = requests.get(f"{SERVER_URL}/health", timeout=5)
        return r.status_code == 200
    except:
        return False

def main():
    print("🚀 Deploying webclip-installer.py to Oracle Cloud...")
    print(f"Server: {SERVER_URL}")
    print(f"Cloudflare: {CLOUDFLARE_URL}")
    print()

    # Check server
    print("Checking server status...")
    if not check_server():
        print("❌ Server not responding")
        print("Manual deployment required - see MANUAL_DEPLOY.md")
        return

    print("✅ Server is online")
    print()
    print("⚠️  Cannot deploy via HTTP - server doesn't have deployment endpoint")
    print()
    print("📋 Manual deployment instructions:")
    print()
    print("1. Connect to server:")
    print("   ssh ubuntu@79.72.18.198")
    print()
    print("2. Run update script:")
    print("   curl -o /tmp/update.sh https://raw.githubusercontent.com/andreyosipov13372-dotcom/lara/main/lara-ota-complete/update-server.sh")
    print("   chmod +x /tmp/update.sh")
    print("   sudo /tmp/update.sh")
    print()
    print("3. Verify:")
    print(f"   curl {CLOUDFLARE_URL}/health")
    print()

if __name__ == '__main__':
    main()
