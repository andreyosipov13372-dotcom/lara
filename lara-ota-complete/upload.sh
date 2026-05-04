#!/bin/bash
# One-click deployment to Oracle Cloud server
# Uploads all files and runs deployment automatically

set -e

SERVER="ubuntu@79.72.18.198"
SSH_KEY="/home/orkenlk/Загрузки/ssh-key-2026-04-29 (1).key"
REMOTE_DIR="~/lara-ota-deploy"

echo "=========================================="
echo "📤 LARA OTA - Automated Deployment"
echo "=========================================="
echo ""

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH key not found: $SSH_KEY"
    exit 1
fi

echo "🔗 Connecting to Oracle Cloud: $SERVER"
echo ""

# Test connection
echo "Testing SSH connection..."
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 $SERVER "echo 'Connection OK'" 2>/dev/null; then
    echo "❌ Cannot connect to server"
    exit 1
fi
echo "✅ Connection successful"
echo ""

# Create remote directory
echo "📁 Creating remote directory..."
ssh -i "$SSH_KEY" $SERVER "mkdir -p $REMOTE_DIR"

# Upload files
echo "📤 Uploading server files..."
scp -i "$SSH_KEY" server.py $SERVER:$REMOTE_DIR/
scp -i "$SSH_KEY" deploy.sh $SERVER:$REMOTE_DIR/
scp -i "$SSH_KEY" requirements.txt $SERVER:$REMOTE_DIR/

echo "✅ Files uploaded"
echo ""

# Make deploy script executable and run it
echo "🚀 Running deployment on server..."
echo "This will take 2-3 minutes..."
echo ""

ssh -i "$SSH_KEY" $SERVER << 'ENDSSH'
cd ~/lara-ota-deploy
chmod +x deploy.sh

# Copy server.py to /opt/lara-ota
sudo mkdir -p /opt/lara-ota
sudo cp server.py /opt/lara-ota/

# Run deployment
sudo ./deploy.sh
ENDSSH

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "🌐 Server is running at: http://79.72.18.198"
echo ""
echo "📋 Next: Upload your Apple ID certificate"
echo ""
echo "Run these commands:"
echo "  scp -i '$SSH_KEY' cert.p12 $SERVER:/opt/lara-ota/certs/"
echo "  scp -i '$SSH_KEY' profile.mobileprovision $SERVER:/opt/lara-ota/certs/"
echo ""
echo "Then setup Cloudflare Tunnel:"
echo "  ssh -i '$SSH_KEY' $SERVER"
echo "  cloudflared tunnel login"
echo ""
echo "📊 Check status:"
echo "  ssh -i '$SSH_KEY' $SERVER 'sudo systemctl status lara-ota'"
echo ""
