#!/bin/bash
# install_ollama.sh: Cross-platform Ollama installer for macOS, Linux, and Windows

set -e

# Function to detect operating system
detect_os() {
    case "$(uname -s)" in
        Darwin*)    echo "macos" ;;
        Linux*)     echo "linux" ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        *)          echo "unknown" ;;
    esac
}

# Function to install on macOS
install_macos() {
    echo "Installing Ollama on macOS..."
    
    if command -v brew &> /dev/null; then
        echo "Using Homebrew to install Ollama..."
        brew install ollama
    else
        echo "Homebrew not found. Installing using the official installer..."
        echo "Downloading Ollama installer..."
        curl -fsSL https://ollama.ai/install.sh | sh
        
        # Check if ollama is in PATH after installation
        if ! command -v ollama &> /dev/null; then
            echo ""
            echo "⚠️  Ollama installed but not found in PATH"
            echo "Setting up PATH configuration..."
            
            # Common installation locations
            POSSIBLE_PATHS=(
                "/usr/local/bin/ollama"
                "/opt/ollama/bin/ollama"
                "$HOME/.ollama/bin/ollama"
                "/usr/bin/ollama"
            )
            
            OLLAMA_PATH=""
            for path in "${POSSIBLE_PATHS[@]}"; do
                if [[ -f "$path" ]]; then
                    OLLAMA_PATH="$(dirname "$path")"
                    echo "✓ Found Ollama at: $path"
                    break
                fi
            done
            
            if [[ -n "$OLLAMA_PATH" ]]; then
                # Add to PATH in shell configuration files
                SHELL_CONFIGS=(
                    "$HOME/.bashrc"
                    "$HOME/.bash_profile" 
                    "$HOME/.zshrc"
                    "$HOME/.profile"
                )
                
                echo "Adding Ollama to PATH..."
                for config in "${SHELL_CONFIGS[@]}"; do
                    if [[ -f "$config" ]]; then
                        # Check if PATH is already configured
                        if ! grep -q "ollama" "$config" 2>/dev/null; then
                            echo "export PATH=\"$OLLAMA_PATH:\$PATH\"" >> "$config"
                            echo "✓ Updated $config"
                        fi
                    fi
                done
                
                # Make ollama executable
                chmod +x "$OLLAMA_PATH/ollama" 2>/dev/null || true
                
                echo ""
                echo "📝 PATH Setup Complete!"
                echo "Please run one of the following to refresh your shell:"
                echo "  source ~/.bashrc"
                echo "  source ~/.zshrc" 
                echo "  # Or simply restart your terminal"
                echo ""
                echo "Alternatively, you can run Ollama directly with:"
                echo "  $OLLAMA_PATH/ollama serve"
            else
                echo "❌ Could not locate Ollama installation"
                echo "You may need to manually add Ollama to your PATH"
                echo "Check these locations:"
                for path in "${POSSIBLE_PATHS[@]}"; do
                    echo "  $path"
                done
            fi
        else
            echo "✅ Ollama is properly installed and available in PATH"
        fi
    fi
}

# Function to install on Linux
install_linux() {
    echo "Installing Ollama on Linux..."
    
    # Try package managers first
    if command -v curl &> /dev/null; then
        echo "Using the official installer..."
        curl -fsSL https://ollama.ai/install.sh | sh
    elif command -v wget &> /dev/null; then
        echo "Using wget to download installer..."
        wget -qO- https://ollama.ai/install.sh | sh
    else
        echo "Error: Neither curl nor wget found. Please install one of them first."
        echo "Ubuntu/Debian: sudo apt install curl"
        echo "CentOS/RHEL: sudo yum install curl"
        echo "Fedora: sudo dnf install curl"
        exit 1
    fi
    
    # Check if ollama is in PATH after installation
    if ! command -v ollama &> /dev/null; then
        echo ""
        echo "⚠️  Ollama installed but not found in PATH"
        echo "Setting up PATH configuration..."
        
        # Common installation locations on Linux
        POSSIBLE_PATHS=(
            "/usr/local/bin/ollama"
            "/usr/bin/ollama"
            "/opt/ollama/bin/ollama"
            "$HOME/.local/bin/ollama"
            "$HOME/bin/ollama"
        )
        
        OLLAMA_PATH=""
        for path in "${POSSIBLE_PATHS[@]}"; do
            if [[ -f "$path" ]]; then
                OLLAMA_PATH="$(dirname "$path")"
                echo "✓ Found Ollama at: $path"
                break
            fi
        done
        
        if [[ -n "$OLLAMA_PATH" ]]; then
            # Add to PATH in shell configuration files
            SHELL_CONFIGS=(
                "$HOME/.bashrc"
                "$HOME/.bash_profile"
                "$HOME/.zshrc"
                "$HOME/.profile"
            )
            
            echo "Adding Ollama to PATH..."
            for config in "${SHELL_CONFIGS[@]}"; do
                if [[ -f "$config" ]]; then
                    # Check if PATH is already configured
                    if ! grep -q "$OLLAMA_PATH" "$config" 2>/dev/null; then
                        echo "export PATH=\"$OLLAMA_PATH:\$PATH\"" >> "$config"
                        echo "✓ Updated $config"
                    fi
                fi
            done
            
            # Make ollama executable
            chmod +x "$OLLAMA_PATH/ollama" 2>/dev/null || true
            
            echo ""
            echo "📝 PATH Setup Complete!"
            echo "Please run one of the following to refresh your shell:"
            echo "  source ~/.bashrc"
            echo "  source ~/.zshrc"
            echo "  # Or simply restart your terminal"
            echo ""
            echo "Alternatively, you can run Ollama directly with:"
            echo "  $OLLAMA_PATH/ollama serve"
        else
            echo "❌ Could not locate Ollama installation"
            echo "You may need to manually add Ollama to your PATH"
        fi
    else
        echo "✅ Ollama is properly installed and available in PATH"
    fi
}

# Function to install on Windows
install_windows() {
    echo "Installing Ollama on Windows..."
    echo ""
    echo "For Windows, please follow these steps:"
    echo "1. Visit https://ollama.ai/download"
    echo "2. Download the Windows installer (Ollama-windows-amd64.zip)"
    echo "3. Extract the zip file"
    echo "4. Run the installer as administrator"
    echo ""
    echo "Alternatively, if you have Windows Subsystem for Linux (WSL), you can:"
    echo "1. Install WSL if not already installed"
    echo "2. Run this script from within WSL"
    echo ""
    echo "Or if you have Chocolatey package manager:"
    echo "  choco install ollama"
    echo ""
    echo "Or if you have Scoop package manager:"
    echo "  scoop install ollama"
}

# Main installation logic
main() {
    echo "Ollama Cross-Platform Installer"
    echo "==============================="
    
    OS=$(detect_os)
    echo "Detected operating system: $OS"
    echo ""
    
    case $OS in
        macos)
            install_macos
            ;;
        linux)
            install_linux
            ;;
        windows)
            install_windows
            ;;
        unknown)
            echo "Error: Unsupported operating system."
            echo "This script supports macOS, Linux, and Windows."
            echo "Please visit https://ollama.ai/download for manual installation."
            exit 1
            ;;
    esac
    
    echo ""
    echo "Installation completed!"
    echo ""
    echo "Next steps:"
    echo "1. Start the Ollama service: ollama serve"
    echo "2. In another terminal, pull a model: ollama pull llama2"
    echo "3. Start chatting: ollama run llama2"
    echo ""
    echo "For more information, visit: https://github.com/jmorganca/ollama"
}

# Run the main function
main
