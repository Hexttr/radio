#!/bin/bash
# Pirate Radio AI - Oracle ARM Setup Script
# Run this on a fresh Oracle Cloud ARM instance (Ubuntu 22.04+)

set -e

echo "🏴‍☠️ Pirate Radio AI - Setup Script"
echo "===================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}Warning: Running as root. Consider using a non-root user.${NC}"
fi

# Update system
echo -e "${GREEN}[1/7] Updating system...${NC}"
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo -e "${GREEN}[2/7] Installing dependencies...${NC}"
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    ffmpeg \
    git \
    curl \
    htop

# Install Docker (optional but recommended)
echo -e "${GREEN}[3/7] Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${YELLOW}Docker installed. You may need to log out and back in for group changes.${NC}"
else
    echo "Docker already installed"
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    sudo apt install -y docker-compose-plugin
fi

# Clone repository (or create directory if local)
echo -e "${GREEN}[4/7] Setting up project...${NC}"
PROJECT_DIR="$HOME/pirate-radio-ai"

if [ -d "$PROJECT_DIR" ]; then
    echo "Project directory exists, updating..."
    cd "$PROJECT_DIR"
else
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    echo "Created project directory at $PROJECT_DIR"
fi

# Create Python virtual environment
echo -e "${GREEN}[5/7] Setting up Python environment...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt 2>/dev/null || echo "requirements.txt not found, skipping..."

# Create directories
echo -e "${GREEN}[6/7] Creating directories...${NC}"
mkdir -p music output cache

# Setup environment file
echo -e "${GREEN}[7/7] Setting up configuration...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}Created .env from .env.example${NC}"
        echo -e "${YELLOW}Please edit .env and add your GROQ_API_KEY${NC}"
    fi
fi

# Setup systemd service (optional)
echo ""
echo -e "${GREEN}Do you want to install as a systemd service? (y/n)${NC}"
read -r INSTALL_SERVICE

if [ "$INSTALL_SERVICE" = "y" ]; then
    sudo tee /etc/systemd/system/pirate-radio.service > /dev/null <<EOF
[Unit]
Description=Pirate Radio AI
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$PROJECT_DIR/venv/bin/python -m src.radio
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable pirate-radio
    echo -e "${GREEN}Systemd service installed!${NC}"
    echo "Start with: sudo systemctl start pirate-radio"
    echo "View logs: sudo journalctl -u pirate-radio -f"
fi

# Open firewall port
echo ""
echo -e "${GREEN}Opening firewall port 8080...${NC}"
sudo iptables -I INPUT -p tcp --dport 8080 -j ACCEPT
# Make iptables rules persistent
echo iptables-persistent iptables-persistent/autosave_v4 boolean true | sudo debconf-set-selections
echo iptables-persistent iptables-persistent/autosave_v6 boolean true | sudo debconf-set-selections
sudo apt install -y iptables-persistent

# Done!
echo ""
echo "===================================="
echo -e "${GREEN}🏴‍☠️ Setup Complete!${NC}"
echo "===================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GROQ_API_KEY"
echo "   Get one free at: https://console.groq.com"
echo ""
echo "2. Add music files to the 'music' directory"
echo "   (MP3, WAV, or OGG files)"
echo ""
echo "3. Start the radio:"
echo "   Option A (Direct): source venv/bin/activate && python -m src.radio"
echo "   Option B (Docker): docker-compose up -d"
echo "   Option C (Service): sudo systemctl start pirate-radio"
echo ""
echo "4. Listen at: http://$(hostname -I | awk '{print $1}'):8080"
echo ""
echo -e "${YELLOW}Note: On Oracle Cloud, also open port 8080 in the VCN Security List!${NC}"
