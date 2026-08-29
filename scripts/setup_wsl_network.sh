#!/bin/bash
# File: setup_wsl_network.sh
# Purpose: Setup WSL mirrored networking mode automatically

echo "🔧 Setting up WSL mirrored networking..."

# Create .wslconfig in Windows user profile
WSL_CONFIG="/mnt/c/Users/$USER/.wslconfig"

# Check if running in WSL
if ! grep -q Microsoft /proc/version; then
    echo "❌ This script must be run in WSL (Windows Subsystem for Linux)"
    exit 1
fi

# Create the config file
cat > "$WSL_CONFIG" << EOF
[wsl2]
networkingMode=mirrored
EOF

echo "✅ Created .wslconfig at: $WSL_CONFIG"

# Restart WSL
echo "🔄 Restarting WSL..."
cmd.exe /c "wsl --shutdown"

echo "✅ Done! Please restart your WSL terminal."
echo "📝 To verify, run: ip addr show eth0"
