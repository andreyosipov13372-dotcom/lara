#!/bin/bash
# Setup automatic IPA signing with free Apple ID

echo "Installing ios-signer-service..."

# Install dependencies
sudo apt-get update -qq
sudo apt-get install -y docker.io docker-compose

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker ubuntu

# Create directory for signer service
mkdir -p ~/ios-signer
cd ~/ios-signer

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3'
services:
  builder:
    image: signtools/ios-signer-service:latest
    container_name: ios-signer
    environment:
      - BUILDER_KEY=changeme123
    ports:
      - "8090:8080"
    volumes:
      - ./data:/data
    restart: unless-stopped
EOF

# Start service
docker-compose up -d

echo ""
echo "✅ ios-signer-service installed!"
echo ""
echo "Access at: http://localhost:8090"
echo "Builder Key: changeme123"
echo ""
echo "Next steps:"
echo "1. Open http://79.72.18.198:8090 in browser"
echo "2. Sign in with your Apple ID"
echo "3. Upload LARA IPA"
echo "4. Download signed IPA"
