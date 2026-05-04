#!/bin/bash
# Simple installation script

echo "Installing zsign..."
cd /tmp
wget -q https://github.com/zhlynn/zsign/releases/download/1.1.2/zsign-linux-x86_64.zip || exit 1
unzip -o -q zsign-linux-x86_64.zip || exit 1
sudo mv zsign /usr/local/bin/ || exit 1
sudo chmod +x /usr/local/bin/zsign || exit 1
rm -f zsign-linux-x86_64.zip

echo "Setting up directories..."
sudo mkdir -p /opt/lara-ota/{uploads,signed,certs,logs}
sudo chown -R ubuntu:ubuntu /opt/lara-ota

echo "Copying files..."
sudo cp ~/lara-ota-deploy/server.py /opt/lara-ota/

echo "Installing Python packages..."
cd /opt/lara-ota
python3 -m venv venv
source venv/bin/activate
pip install -q Flask Werkzeug gunicorn requests

echo "Creating systemd service..."
sudo tee /etc/systemd/system/lara-ota.service > /dev/null << 'EOF'
[Unit]
Description=LARA OTA Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/lara-ota
Environment="PATH=/opt/lara-ota/venv/bin"
ExecStart=/opt/lara-ota/venv/bin/gunicorn --bind 127.0.0.1:8080 --workers 4 --timeout 120 server:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable lara-ota
sudo systemctl start lara-ota

echo "Done!"
sudo systemctl status lara-ota --no-pager
