#!/bin/bash
# Deploy webclip-installer.py to Oracle Cloud server

SERVER="79.72.18.198"
USER="ubuntu"

echo "📦 Deploying webclip-installer.py..."

# Create temporary deployment package
cat > /tmp/deploy_webclip.sh << 'DEPLOY_SCRIPT'
#!/bin/bash
set -e

echo "Stopping service..."
sudo systemctl stop lara-ota

echo "Backing up old server.py..."
sudo cp /opt/lara-ota/server.py /opt/lara-ota/server.py.backup 2>/dev/null || true

echo "Installing new webclip-installer.py..."
sudo tee /opt/lara-ota/server.py > /dev/null << 'EOF'
#!/usr/bin/env python3
"""
LARA WebClip Installer - Installation without Developer Account
Uses URL schemes and direct download instead of itms-services://
"""

from flask import Flask, request, jsonify, send_file, render_template_string, redirect
import os

app = Flask(__name__)

# GitHub Release IPA URL
IPA_URL = "https://github.com/rooootdev/lara/releases/latest/download/lara.ipa"

HTML_TEMPLATE = """
<!DOCTYPE html>
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
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .logo { text-align: center; font-size: 80px; margin-bottom: 20px; }
        h1 { color: #333; margin-bottom: 10px; text-align: center; }
        .subtitle { color: #666; margin-bottom: 30px; font-size: 14px; text-align: center; }

        .install-option {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            cursor: pointer;
            transition: all 0.3s;
            border: 2px solid transparent;
        }
        .install-option:hover {
            background: #e9ecef;
            border-color: #667eea;
            transform: translateY(-2px);
        }
        .option-icon { font-size: 32px; margin-bottom: 10px; }
        .option-title { font-weight: 600; color: #333; margin-bottom: 5px; }
        .option-desc { font-size: 13px; color: #666; }

        .info-box {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
            font-size: 13px;
        }
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
                <div class="option-desc">
                    Если у тебя установлен Scarlet - нажми сюда.<br>
                    Scarlet автоматически подпишет и установит LARA.
                </div>
            </div>
        </a>

        <a href="apple-magnifier://install?url={{ ipa_url }}">
            <div class="install-option">
                <div class="option-icon">🛒</div>
                <div class="option-title">Установить через TrollStore</div>
                <div class="option-desc">
                    Если у тебя установлен TrollStore - нажми сюда.<br>
                    TrollStore установит LARA навсегда без подписи.
                </div>
            </div>
        </a>

        <a href="esign://import?url={{ ipa_url }}">
            <div class="install-option">
                <div class="option-icon">✍️</div>
                <div class="option-title">Установить через ESign</div>
                <div class="option-desc">
                    Если у тебя установлен ESign - нажми сюда.<br>
                    ESign подпишет с твоим сертификатом.
                </div>
            </div>
        </a>

        <a href="{{ ipa_url }}" download>
            <div class="install-option">
                <div class="option-icon">📥</div>
                <div class="option-title">Скачать IPA напрямую</div>
                <div class="option-desc">
                    Скачай IPA и установи через AltStore/Sideloadly.<br>
                    Требуется компьютер.
                </div>
            </div>
        </a>

        <div class="info-box">
            <strong>ℹ️ Как это работает:</strong>
            • Нажми на любой способ установки<br>
            • Если приложение установлено - оно откроется<br>
            • Если нет - скачай его сначала<br>
            <br>
            <strong>📱 Рекомендуем:</strong>
            • Scarlet (самый простой)<br>
            • TrollStore (если уже установлен)<br>
            • ESign (если есть сертификат)<br>
            <br>
            <strong>🔗 Где скачать:</strong>
            • Scarlet: <a href="https://usescarlet.com" style="color: #667eea;">usescarlet.com</a><br>
            • ESign: <a href="https://esign.yyyue.xyz" style="color: #667eea;">esign.yyyue.xyz</a>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, ipa_url=IPA_URL)

@app.route('/install')
def install():
    """Redirect to main page"""
    return redirect('/')

@app.route('/download')
def download():
    """Direct download endpoint"""
    return redirect(IPA_URL)

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'lara-webclip-installer'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
EOF

echo "Setting permissions..."
sudo chmod +x /opt/lara-ota/server.py

echo "Starting service..."
sudo systemctl start lara-ota

echo "Checking status..."
sleep 2
sudo systemctl status lara-ota --no-pager

echo ""
echo "✅ Deployment complete!"
echo "🌐 Access at: https://liver-vintage-marco-thus.trycloudflare.com"
DEPLOY_SCRIPT

# Copy and execute on server
echo "Uploading deployment script..."
scp -o StrictHostKeyChecking=no /tmp/deploy_webclip.sh $USER@$SERVER:/tmp/ 2>&1 || {
    echo "❌ SSH key not configured. Manual deployment required."
    echo ""
    echo "Run this on the server (79.72.18.198):"
    cat /tmp/deploy_webclip.sh
    exit 1
}

echo "Executing deployment..."
ssh -o StrictHostKeyChecking=no $USER@$SERVER "bash /tmp/deploy_webclip.sh"

echo ""
echo "✅ Done!"
