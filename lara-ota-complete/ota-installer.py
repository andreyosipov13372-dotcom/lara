#!/usr/bin/env python3
"""
LARA OTA Installer - Free certificate OTA installation
Works directly from Safari without external apps
"""

from flask import Flask, request, jsonify, send_file, render_template_string, redirect
import os
import subprocess
import tempfile
import shutil
import threading
import time
import secrets

app = Flask(__name__)

# Store signing jobs
signing_jobs = {}

# GitHub IPA URL - from your repo
IPA_URL = "https://github.com/andreyosipov13372-dotcom/lara/releases/latest/download/lara.ipa"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
        .logo { text-align: center; font-size: 80px; margin-bottom: 20px; }
        h1 { color: #333; margin-bottom: 10px; text-align: center; }
        .subtitle { color: #666; margin-bottom: 30px; font-size: 14px; text-align: center; }

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
        }
        button:hover { background: #5568d3; }
        button:disabled { background: #ccc; cursor: not-allowed; }

        .status {
            background: #f0f0f0;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 14px;
            text-align: center;
            display: none;
        }
        .status.success { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
        .status.info { background: #d1ecf1; color: #0c5460; }

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
        }

        .info-box {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            font-size: 13px;
        }
        .info-box strong { display: block; margin-bottom: 8px; }

        .spinner {
            display: inline-block;
            width: 14px;
            height: 14px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 8px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        #installBtn { display: none; background: #28a745; }
        #installBtn:hover { background: #218838; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🚀</div>
        <h1>LARA OTA Installer</h1>
        <p class="subtitle">Установка прямо из Safari</p>

        <div id="status" class="status"></div>

        <div class="progress" id="progress">
            <div class="progress-bar" id="progressBar"></div>
        </div>

        <button id="signBtn" onclick="startSigning()">
            📦 Подготовить установку
        </button>

        <button id="installBtn" onclick="installOTA()">
            ✅ Установить через OTA
        </button>

        <button id="downloadBtn" onclick="downloadIPA()" style="display: none; background: #28a745;">
            📥 Скачать подписанный IPA
        </button>

        <div class="info-box">
            <strong>ℹ️ Как это работает:</strong>
            • Нажми "Подготовить установку"<br>
            • Сервер подпишет IPA бесплатным сертификатом<br>
            • Нажми "Установить LARA"<br>
            • iOS установит приложение через OTA<br>
            <br>
            <strong>📱 Требования:</strong>
            • iPhone X или новее<br>
            • iOS 17.0 - 17.6.1<br>
            • Открыто в Safari (не Chrome/Firefox)<br>
            <br>
            <strong>⚠️ Важно:</strong>
            • Подпись действует 7 дней<br>
            • После истечения - переустанови<br>
            • Работает БЕЗ компьютера<br>
            • Работает БЕЗ Developer аккаунта
        </div>
    </div>

    <script>
        let jobId = null;
        let statusInterval = null;

        function setStatus(msg, type) {
            const status = document.getElementById('status');
            status.innerHTML = msg;
            status.className = 'status ' + type;
            status.style.display = 'block';
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
            btn.innerHTML = '<span class="spinner"></span>Подготовка...';

            setStatus('<span class="spinner"></span>Скачивание и подпись IPA...', 'info');
            setProgress(10);

            try {
                const response = await fetch('/api/sign', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });

                const data = await response.json();

                if (data.success) {
                    jobId = data.job_id;
                    startStatusPolling();
                } else {
                    throw new Error(data.error || 'Ошибка подписи');
                }
            } catch (error) {
                setStatus('❌ ' + error.message, 'error');
                btn.disabled = false;
                btn.innerHTML = '🔄 Попробовать снова';
                setProgress(0);
            }
        }

        function startStatusPolling() {
            if (statusInterval) clearInterval(statusInterval);

            statusInterval = setInterval(async () => {
                try {
                    const response = await fetch('/api/status/' + jobId);
                    const data = await response.json();

                    setProgress(data.progress);

                    if (data.message) {
                        setStatus('<span class="spinner"></span>' + data.message, 'info');
                    }

                    if (data.error) {
                        clearInterval(statusInterval);
                        setStatus('❌ ' + data.error, 'error');
                        document.getElementById('signBtn').disabled = false;
                        document.getElementById('signBtn').innerHTML = '🔄 Попробовать снова';
                        setProgress(0);
                    }

                    if (data.status === 'completed') {
                        clearInterval(statusInterval);
                        setStatus('✅ Готово к установке!', 'success');
                        setProgress(100);
                        document.getElementById('signBtn').style.display = 'none';
                        document.getElementById('installBtn').style.display = 'block';
                        document.getElementById('downloadBtn').style.display = 'block';
                    }
                } catch (e) {
                    console.error('Status check failed:', e);
                }
            }, 1000);
        }

        function installOTA() {
            window.location.href = '/api/install/' + jobId;
        }

        function downloadIPA() {
            window.location.href = '/api/download/' + jobId;
        }
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
                    <string>{ipa_url}</string>
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
            </dict>
        </dict>
    </array>
</dict>
</plist>
"""

def sign_ipa_background(job_id):
    """Background signing task"""
    try:
        job = signing_jobs[job_id]
        job['progress'] = 10
        job['message'] = 'Скачивание LARA IPA...'

        # Download IPA
        ipa_path = f'/opt/lara-ota/signed/lara_{job_id}.ipa'
        result = subprocess.run(
            ['/usr/bin/wget', '-O', ipa_path, IPA_URL, '--timeout=60', '--tries=3'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f'Не удалось скачать IPA: {result.stderr}')

        job['progress'] = 40
        job['message'] = 'Подпись с бесплатным сертификатом...'

        # Sign with zsign (ad-hoc signing)
        signed_path = f'/opt/lara-ota/signed/lara_signed_{job_id}.ipa'
        result = subprocess.run(
            ['/usr/local/bin/zsign', '-a', '-o', signed_path, ipa_path],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            raise Exception(f'Ошибка подписи: {result.stderr}')

        job['progress'] = 90
        job['message'] = 'Проверка подписи...'

        if not os.path.exists(signed_path) or os.path.getsize(signed_path) < 1000000:
            raise Exception('Подписанный IPA поврежден')

        job['progress'] = 100
        job['message'] = 'Готово!'
        job['status'] = 'completed'
        job['signed_path'] = signed_path

        # Cleanup original
        os.remove(ipa_path)

    except Exception as e:
        job['status'] = 'failed'
        job['error'] = str(e)
        job['progress'] = 0

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/sign', methods=['POST'])
def sign():
    # Create job
    job_id = secrets.token_urlsafe(16)
    signing_jobs[job_id] = {
        'status': 'signing',
        'progress': 0,
        'message': 'Начинаю...',
        'error': None,
        'signed_path': None
    }

    # Start background signing
    thread = threading.Thread(target=sign_ipa_background, args=(job_id,))
    thread.daemon = True
    thread.start()

    return jsonify({'success': True, 'job_id': job_id})

@app.route('/api/status/<job_id>')
def status(job_id):
    job = signing_jobs.get(job_id, {})
    return jsonify(job)

@app.route('/api/download/<job_id>')
def download(job_id):
    job = signing_jobs.get(job_id)
    if not job or job['status'] != 'completed':
        return jsonify({'error': 'IPA not ready'}), 404

    signed_path = job['signed_path']
    if not os.path.exists(signed_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(
        signed_path,
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name='lara_signed.ipa'
    )

@app.route('/api/install/<job_id>')
def install(job_id):
    job = signing_jobs.get(job_id)
    if not job or job['status'] != 'completed':
        return jsonify({'error': 'IPA not ready'}), 404

    # Generate manifest.plist
    base_url = request.url_root.rstrip('/')
    ipa_url = f'{base_url}/api/download/{job_id}'

    manifest = MANIFEST_TEMPLATE.format(ipa_url=ipa_url)
    manifest_path = f'/opt/lara-ota/signed/manifest_{job_id}.plist'

    with open(manifest_path, 'w') as f:
        f.write(manifest)

    # Redirect to itms-services://
    manifest_url = f'{base_url}/api/manifest/{job_id}'
    itms_url = f'itms-services://?action=download-manifest&url={manifest_url}'

    return redirect(itms_url)

@app.route('/api/manifest/<job_id>')
def manifest(job_id):
    manifest_path = f'/opt/lara-ota/signed/manifest_{job_id}.plist'
    if not os.path.exists(manifest_path):
        return jsonify({'error': 'Manifest not found'}), 404

    return send_file(
        manifest_path,
        mimetype='application/xml',
        as_attachment=False
    )

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'lara-ota-installer'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
