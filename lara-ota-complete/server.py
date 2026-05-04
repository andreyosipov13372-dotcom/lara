#!/usr/bin/env python3
"""
LARA OTA Server - Complete automated IPA signing and installation
Runs on Oracle Cloud with Cloudflare Tunnel
"""

from flask import Flask, request, jsonify, send_file, render_template_string, Response
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
import logging
import threading
import time
import json

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BASE_DIR = '/opt/lara-ota'
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
SIGNED_FOLDER = os.path.join(BASE_DIR, 'signed')
CERT_DIR = os.path.join(BASE_DIR, 'certs')
IPA_URL = 'https://github.com/andreyosipov13372-dotcom/lara/releases/latest/download/lara.ipa'

# Create directories
for directory in [UPLOAD_FOLDER, SIGNED_FOLDER, CERT_DIR]:
    os.makedirs(directory, exist_ok=True)

# Global signing status
signing_status = {
    'progress': 0,
    'message': 'Готов к работе',
    'signing': False,
    'signed_ipa': None,
    'error': None
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>LARA OTA Installer</title>
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
        .logo {
            text-align: center;
            font-size: 80px;
            margin-bottom: 20px;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
            text-align: center;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
            text-align: center;
        }
        .status {
            background: #f0f0f0;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 14px;
            text-align: center;
        }
        .status.success { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
        .status.info { background: #d1ecf1; color: #0c5460; }
        .status.warning { background: #fff3cd; color: #856404; }
        button {
            width: 100%;
            padding: 15px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 10px;
            transition: all 0.3s;
        }
        button:hover { background: #5568d3; transform: translateY(-2px); }
        button:active { transform: translateY(0); }
        button:disabled { background: #ccc; cursor: not-allowed; transform: none; }
        button.success { background: #28a745; }
        button.success:hover { background: #218838; }
        .progress {
            width: 100%;
            height: 8px;
            background: #f0f0f0;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 20px;
            display: none;
        }
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            width: 0%;
            transition: width 0.3s;
            animation: shimmer 2s infinite;
        }
        @keyframes shimmer {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        .info-box {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            font-size: 13px;
            color: #666;
        }
        .info-box strong { color: #333; display: block; margin-bottom: 8px; }
        .info-box ul { margin-left: 20px; margin-top: 8px; }
        .info-box li { margin-bottom: 5px; }
        .log {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            max-height: 200px;
            overflow-y: auto;
            margin-top: 20px;
            display: none;
        }
        .log-line { margin-bottom: 3px; }
        .log-line.error { color: #f48771; }
        .log-line.success { color: #89d185; }
        .log-line.info { color: #6cb6ff; }
        .spinner {
            display: inline-block;
            width: 14px;
            height: 14px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 8px;
            vertical-align: middle;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🚀</div>
        <h1>LARA OTA Installer</h1>
        <p class="subtitle">TrollStore установщик с автоподписью</p>

        <div id="status" class="status info">
            Готов к установке
        </div>

        <div class="progress" id="progress">
            <div class="progress-bar" id="progressBar"></div>
        </div>

        <button id="signBtn" onclick="startSigning()">
            📝 Подписать и скачать IPA
        </button>

        <button id="installBtn" onclick="installOTA()" style="display:none;">
            ✅ Установить через OTA
        </button>

        <div class="info-box">
            <strong>ℹ️ Как установить:</strong>
            <ul>
                <li>Нажми "Подписать и скачать IPA"</li>
                <li>Дождись подписи (~30 сек)</li>
                <li>Нажми "Установить через OTA"</li>
                <li>Подтверди установку в iOS</li>
            </ul>
            <strong style="margin-top: 10px;">📱 Поддержка:</strong>
            <ul>
                <li>iOS 17.0 - 17.6.1</li>
                <li>iPhone X и новее</li>
                <li>Работает 7 дней</li>
            </ul>
        </div>

        <div id="log" class="log"></div>
    </div>

    <script>
        let statusCheckInterval = null;

        function addLog(msg, type = 'info') {
            const log = document.getElementById('log');
            log.style.display = 'block';
            const line = document.createElement('div');
            line.className = 'log-line ' + type;
            line.textContent = new Date().toLocaleTimeString() + ' - ' + msg;
            log.appendChild(line);
            log.scrollTop = log.scrollHeight;
        }

        function setStatus(msg, type) {
            const status = document.getElementById('status');
            status.innerHTML = msg;
            status.className = 'status ' + type;
        }

        function setProgress(percent) {
            const progress = document.getElementById('progress');
            const bar = document.getElementById('progressBar');
            if (percent > 0) {
                progress.style.display = 'block';
                bar.style.width = percent + '%';
            } else {
                progress.style.display = 'none';
            }
        }

        async function startSigning() {
            const btn = document.getElementById('signBtn');
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span>Подписываю...';

            setStatus('<span class="spinner"></span>Начинаю подпись...', 'info');
            addLog('Запуск процесса подписи', 'info');

            try {
                const response = await fetch('/api/sign', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });

                const data = await response.json();

                if (data.success) {
                    // Start polling for status
                    startStatusPolling();
                } else {
                    throw new Error(data.error || 'Ошибка подписи');
                }
            } catch (error) {
                setStatus('❌ Ошибка: ' + error.message, 'error');
                addLog('ERROR: ' + error.message, 'error');
                btn.disabled = false;
                btn.innerHTML = '🔄 Попробовать снова';
                setProgress(0);
            }
        }

        function startStatusPolling() {
            if (statusCheckInterval) clearInterval(statusCheckInterval);

            statusCheckInterval = setInterval(async () => {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();

                    setProgress(data.progress);

                    if (data.message) {
                        setStatus('<span class="spinner"></span>' + data.message, 'info');
                        addLog(data.message, 'info');
                    }

                    if (data.error) {
                        clearInterval(statusCheckInterval);
                        setStatus('❌ ' + data.error, 'error');
                        addLog('ERROR: ' + data.error, 'error');
                        document.getElementById('signBtn').disabled = false;
                        document.getElementById('signBtn').innerHTML = '🔄 Попробовать снова';
                        setProgress(0);
                    }

                    if (data.progress >= 100 && data.signed_ipa) {
                        clearInterval(statusCheckInterval);
                        setStatus('✅ Подпись завершена!', 'success');
                        addLog('Подпись успешно завершена!', 'success');
                        setProgress(100);

                        document.getElementById('signBtn').style.display = 'none';
                        document.getElementById('installBtn').style.display = 'block';
                    }
                } catch (e) {
                    console.error('Status check failed:', e);
                }
            }, 1000);
        }

        function installOTA() {
            setStatus('📲 Открываю установщик iOS...', 'info');
            addLog('Перенаправление на itms-services', 'info');

            const manifestUrl = window.location.origin + '/manifest.plist';
            window.location.href = 'itms-services://?action=download-manifest&url=' + encodeURIComponent(manifestUrl);

            setTimeout(() => {
                setStatus('✅ Если установка не началась, попробуй еще раз', 'warning');
            }, 3000);
        }

        // Check if already signed on page load
        window.addEventListener('load', async () => {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                if (data.signed_ipa && data.progress >= 100) {
                    setStatus('✅ IPA уже подписана и готова', 'success');
                    document.getElementById('signBtn').style.display = 'none';
                    document.getElementById('installBtn').style.display = 'block';
                    setProgress(100);
                }
            } catch (e) {}
        });
    </script>
</body>
</html>
"""

MANIFEST_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>items</key>
    <array>
        <dict>
            <key>assets</key>
            <array>
                <dict>
                    <key>kind</key>
                    <string>software-package</string>
                    <key>url</key>
                    <string>{IPA_URL}</string>
                </dict>
            </array>
            <key>metadata</key>
            <dict>
                <key>bundle-identifier</key>
                <string>com.lara.app</string>
                <key>bundle-version</key>
                <string>1.0</string>
                <key>kind</key>
                <string>software</string>
                <key>title</key>
                <string>LARA</string>
                <key>subtitle</key>
                <string>TrollStore Installer</string>
            </dict>
        </dict>
    </array>
</dict>
</plist>
"""

def update_status(progress, message, error=None, signed_ipa=None):
    """Update global signing status"""
    global signing_status
    signing_status['progress'] = progress
    signing_status['message'] = message
    if error:
        signing_status['error'] = error
        signing_status['signing'] = False
    if signed_ipa:
        signing_status['signed_ipa'] = signed_ipa
    logger.info(f"Status: {progress}% - {message}")

def sign_ipa_background():
    """Background task to sign IPA"""
    global signing_status

    try:
        signing_status['signing'] = True
        signing_status['error'] = None

        update_status(10, 'Скачивание LARA IPA...')

        # Download IPA
        ipa_path = os.path.join(UPLOAD_FOLDER, 'lara.ipa')
        result = subprocess.run(
            ['wget', '-O', ipa_path, IPA_URL, '--timeout=60', '--tries=3'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f'Не удалось скачать IPA: {result.stderr}')

        if not os.path.exists(ipa_path) or os.path.getsize(ipa_path) < 1000000:
            raise Exception('Скачанный файл поврежден или слишком мал')

        update_status(40, 'IPA скачана, начинаю подпись...')

        # Sign with zsign
        signed_path = os.path.join(SIGNED_FOLDER, 'lara-signed.ipa')
        cert_path = os.path.join(CERT_DIR, 'cert.p12')
        profile_path = os.path.join(CERT_DIR, 'profile.mobileprovision')

        # Check if cert exists
        if not os.path.exists(cert_path):
            raise Exception('Сертификат не найден. Загрузите cert.p12 в ' + CERT_DIR)

        if not os.path.exists(profile_path):
            raise Exception('Профиль не найден. Загрузите profile.mobileprovision в ' + CERT_DIR)

        update_status(60, 'Подписываю IPA...')

        # Run zsign
        result = subprocess.run(
            ['zsign', '-k', cert_path, '-m', profile_path, '-o', signed_path, '-z', '9', ipa_path],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            raise Exception(f'Ошибка zsign: {result.stderr}')

        if not os.path.exists(signed_path):
            raise Exception('Подписанный IPA не создан')

        update_status(90, 'Проверка подписи...')

        # Verify signed IPA
        if os.path.getsize(signed_path) < 1000000:
            raise Exception('Подписанный IPA слишком мал')

        update_status(100, 'Подпись завершена!', signed_ipa=signed_path)
        signing_status['signing'] = False

    except Exception as e:
        logger.error(f"Signing error: {e}")
        update_status(0, '', error=str(e))
        signing_status['signing'] = False

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/manifest.plist')
def manifest():
    """iOS OTA manifest"""
    signed_ipa_url = request.host_url.rstrip('/') + '/download/signed'
    manifest_content = MANIFEST_TEMPLATE.format(IPA_URL=signed_ipa_url)
    return Response(manifest_content, mimetype='application/xml')

@app.route('/api/status')
def status():
    """Get signing status"""
    return jsonify(signing_status)

@app.route('/api/sign', methods=['POST'])
def sign():
    """Start signing process"""
    global signing_status

    if signing_status['signing']:
        return jsonify({'success': False, 'error': 'Подпись уже выполняется'})

    # Reset status
    signing_status = {
        'progress': 0,
        'message': 'Начинаю...',
        'signing': True,
        'signed_ipa': None,
        'error': None
    }

    # Start background signing
    thread = threading.Thread(target=sign_ipa_background)
    thread.daemon = True
    thread.start()

    return jsonify({'success': True})

@app.route('/download/signed')
def download_signed():
    """Download signed IPA"""
    signed_path = os.path.join(SIGNED_FOLDER, 'lara-signed.ipa')
    if os.path.exists(signed_path):
        return send_file(
            signed_path,
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name='lara.ipa'
        )
    return jsonify({'error': 'Signed IPA not found'}), 404

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'service': 'lara-ota-server',
        'signing': signing_status['signing'],
        'signed': signing_status['signed_ipa'] is not None
    })

if __name__ == '__main__':
    logger.info("Starting LARA OTA Server...")
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
