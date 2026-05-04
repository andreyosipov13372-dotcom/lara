#!/bin/bash
# Complete automated deployment script for LARA OTA Server
# Installs everything needed on Oracle Cloud Ubuntu server

set -e

echo "=========================================="
echo "🚀 LARA OTA Server - Full Deployment"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    log_warn "Running as root. This is OK for initial setup."
fi

# Update system
log_info "Updating system packages..."
sudo apt-get update -qq
sudo apt-get upgrade -y -qq

# Install dependencies
log_info "Installing dependencies..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    curl \
    unzip \
    git \
    build-essential \
    libssl-dev \
    nginx

# Install zsign
log_info "Installing zsign for IPA signing..."
cd /tmp
if [ ! -f "/usr/local/bin/zsign" ]; then
    wget -q https://github.com/zhlynn/zsign/releases/download/1.1.2/zsign-linux-x86_64.zip
    unzip -q zsign-linux-x86_64.zip
    sudo mv zsign /usr/local/bin/
    sudo chmod +x /usr/local/bin/zsign
    rm -f zsign-linux-x86_64.zip
    log_info "zsign installed successfully"
else
    log_info "zsign already installed"
fi

# Create application directory
log_info "Creating application directory..."
sudo mkdir -p /opt/lara-ota
sudo chown -R $USER:$USER /opt/lara-ota

# Copy server files
log_info "Setting up server files..."
cd /opt/lara-ota

# Create Python virtual environment
log_info "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
log_info "Installing Python packages..."
pip install --upgrade pip -q
pip install Flask==3.0.0 Werkzeug==3.0.1 gunicorn==21.2.0 requests==2.31.0 -q

# Create directories
mkdir -p uploads signed certs logs

# Create systemd service
log_info "Creating systemd service..."
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
StandardOutput=append:/opt/lara-ota/logs/server.log
StandardError=append:/opt/lara-ota/logs/error.log

[Install]
WantedBy=multi-user.target
EOF

# Configure nginx as reverse proxy
log_info "Configuring nginx..."
sudo tee /etc/nginx/sites-available/lara-ota > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 200M;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/lara-ota /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Install Cloudflare Tunnel
log_info "Installing Cloudflare Tunnel..."
if [ ! -f "/usr/local/bin/cloudflared" ]; then
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo dpkg -i cloudflared-linux-amd64.deb
    rm -f cloudflared-linux-amd64.deb
    log_info "Cloudflare Tunnel installed"
else
    log_info "Cloudflare Tunnel already installed"
fi

# Enable and start service
log_info "Starting LARA OTA service..."
sudo systemctl daemon-reload
sudo systemctl enable lara-ota
sudo systemctl start lara-ota

# Wait for service to start
sleep 3

# Check service status
if sudo systemctl is-active --quiet lara-ota; then
    log_info "✅ LARA OTA service is running"
else
    log_error "❌ LARA OTA service failed to start"
    sudo journalctl -u lara-ota -n 20
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1️⃣  Upload Apple ID Certificate:"
echo "   scp cert.p12 ubuntu@79.72.18.198:/opt/lara-ota/certs/"
echo "   scp profile.mobileprovision ubuntu@79.72.18.198:/opt/lara-ota/certs/"
echo ""
echo "2️⃣  Setup Cloudflare Tunnel:"
echo "   cloudflared tunnel login"
echo "   cloudflared tunnel create lara-ota"
echo "   cloudflared tunnel route dns lara-ota lara.yourdomain.com"
echo ""
echo "3️⃣  Create tunnel config:"
echo "   sudo mkdir -p /etc/cloudflared"
echo "   sudo nano /etc/cloudflared/config.yml"
echo ""
echo "   Add this content:"
echo "   ---"
echo "   tunnel: <TUNNEL-ID>"
echo "   credentials-file: /root/.cloudflared/<TUNNEL-ID>.json"
echo "   ingress:"
echo "     - hostname: lara.yourdomain.com"
echo "       service: http://localhost:80"
echo "     - service: http_status:404"
echo ""
echo "4️⃣  Start Cloudflare Tunnel:"
echo "   sudo cloudflared service install"
echo "   sudo systemctl start cloudflared"
echo "   sudo systemctl enable cloudflared"
echo ""
echo "📊 Useful Commands:"
echo "   Status:  sudo systemctl status lara-ota"
echo "   Logs:    sudo journalctl -u lara-ota -f"
echo "   Restart: sudo systemctl restart lara-ota"
echo "   Health:  curl http://localhost/health"
echo ""
echo "🌐 Local test: http://$(hostname -I | awk '{print $1}')"
echo ""
