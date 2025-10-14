#!/bin/bash
# health_check.sh: Cross-platform health check for Qdrant and Ollama services
# Works on macOS, Linux, and Windows (Git Bash/WSL)

set -e

# Detect operating system
detect_os() {
    case "$(uname -s)" in
        Darwin*)    echo "macos" ;;
        Linux*)     echo "linux" ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        *)          echo "unknown" ;;
    esac
}

# Colors for output (Windows compatible)
if [[ "$(detect_os)" == "windows" ]]; then
    # Simplified colors for Windows
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
else
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
fi

# Tracking variables
ALL_CHECKS_PASSED=true

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "PASS")
            echo -e "${GREEN}✓${NC} $message"
            ;;
        "FAIL")
            echo -e "${RED}✗${NC} $message"
            ALL_CHECKS_PASSED=false
            ;;
        "WARN")
            echo -e "${YELLOW}⚠${NC} $message"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ${NC} $message"
            ;;
    esac
}

# Function to check if a command exists (cross-platform)
command_exists() {
    if [[ "$(detect_os)" == "windows" ]]; then
        where "$1" >/dev/null 2>&1 || command -v "$1" >/dev/null 2>&1
    else
        command -v "$1" >/dev/null 2>&1
    fi
}

# Function to check if a port is open (cross-platform)
port_is_open() {
    local host=$1
    local port=$2
    local os=$(detect_os)
    
    case $os in
        "windows")
            # Windows methods
            if command_exists powershell; then
                powershell -Command "Test-NetConnection -ComputerName $host -Port $port -InformationLevel Quiet" 2>/dev/null | grep -q "True"
            elif command_exists nc; then
                nc -z "$host" "$port" 2>/dev/null
            else
                # Fallback: try to connect using bash
                timeout 3 bash -c "exec 3<>/dev/tcp/$host/$port && exec 3<&- && exec 3>&-" 2>/dev/null
            fi
            ;;
        *)
            # macOS and Linux methods
            if command_exists nc; then
                nc -z "$host" "$port" 2>/dev/null
            elif command_exists telnet; then
                timeout 3 bash -c "echo '' | telnet $host $port" >/dev/null 2>&1
            else
                timeout 3 bash -c "exec 3<>/dev/tcp/$host/$port && exec 3<&- && exec 3>&-" 2>/dev/null
            fi
            ;;
    esac
}

# Function to get curl command (Windows compatible)
get_curl_cmd() {
    if command_exists curl; then
        echo "curl"
    elif command_exists wget; then
        echo "wget -qO-"
    else
        echo ""
    fi
}

# Function to check Qdrant
check_qdrant() {
    echo ""
    echo "=== Qdrant Vector Database ==="
    
    # Check if Qdrant is running on default port 6333
    if port_is_open "127.0.0.1" "6333"; then
        print_status "PASS" "Qdrant is running on port 6333"
        
        # Try to get Qdrant info
        local curl_cmd=$(get_curl_cmd)
        if [[ -n "$curl_cmd" ]]; then
            if [[ "$curl_cmd" == "curl" ]]; then
                local response=$(curl -s -w "%{http_code}" http://127.0.0.1:6333/ 2>/dev/null)
                local http_code="${response: -3}"
                local body="${response%???}"
            else
                # Using wget
                local body=$(wget -qO- http://127.0.0.1:6333/ 2>/dev/null)
                local http_code="200" # Assume success if wget doesn't fail
            fi
            
            if [[ "$http_code" == "200" ]] || [[ "$curl_cmd" == "wget" && -n "$body" ]]; then
                print_status "PASS" "Qdrant API is responding"
                
                # Try to get version info
                local qdrant_version=$(echo "$body" | grep -o '"version":"[^"]*"' | cut -d'"' -f4 2>/dev/null || echo "")
                if [[ -n "$qdrant_version" ]]; then
                    print_status "INFO" "Qdrant version: $qdrant_version"
                fi
                
                # Check collections
                if [[ "$curl_cmd" == "curl" ]]; then
                    local collections=$(curl -s http://127.0.0.1:6333/collections 2>/dev/null | grep -o '"name":"[^"]*"' | cut -d'"' -f4 2>/dev/null || echo "")
                else
                    local collections=$(wget -qO- http://127.0.0.1:6333/collections 2>/dev/null | grep -o '"name":"[^"]*"' | cut -d'"' -f4 2>/dev/null || echo "")
                fi
                
                if [[ -n "$collections" ]]; then
                    print_status "INFO" "Available collections: $(echo $collections | tr '\n' ' ')"
                else
                    print_status "INFO" "No collections found (normal for fresh installation)"
                fi
            else
                print_status "WARN" "Qdrant port is open but API returned HTTP $http_code"
            fi
        else
            print_status "WARN" "Neither curl nor wget available, cannot test Qdrant API"
        fi
    else
        print_status "FAIL" "Qdrant is not running on port 6333"
        local os=$(detect_os)
        case $os in
            "windows")
                print_status "INFO" "To start Qdrant on Windows:"
                print_status "INFO" "  - Using Docker Desktop: docker-compose up -d"
                print_status "INFO" "  - Using WSL: Run this script in WSL environment"
                ;;
            *)
                print_status "INFO" "To start Qdrant: docker-compose up -d"
                ;;
        esac
        
        # Check if docker-compose.yml exists
        if [[ -f "docker-compose.yml" ]]; then
            print_status "INFO" "docker-compose.yml found in current directory"
        else
            print_status "WARN" "docker-compose.yml not found in current directory"
        fi
    fi
}

# Function to check Ollama
check_ollama() {
    echo ""
    echo "=== Ollama ==="
    
    if command_exists ollama; then
        local ollama_version=$(ollama --version 2>&1 | head -n1 | sed 's/ollama version is //' || echo "unknown")
        print_status "PASS" "Ollama is installed (version: $ollama_version)"
        
        # Check if Ollama service is running
        if port_is_open "127.0.0.1" "11434"; then
            print_status "PASS" "Ollama service is running on port 11434"
            
            # Test API connectivity
            local curl_cmd=$(get_curl_cmd)
            if [[ -n "$curl_cmd" ]]; then
                if [[ "$curl_cmd" == "curl" ]]; then
                    local api_response=$(curl -s -w "%{http_code}" http://127.0.0.1:11434/api/tags 2>/dev/null)
                    local http_code="${api_response: -3}"
                else
                    local api_response=$(wget -qO- http://127.0.0.1:11434/api/tags 2>/dev/null)
                    local http_code="200" # Assume success if wget doesn't fail
                fi
                
                if [[ "$http_code" == "200" ]] || [[ "$curl_cmd" == "wget" && -n "$api_response" ]]; then
                    print_status "PASS" "Ollama API is responding"
                else
                    print_status "WARN" "Ollama service is running but API returned HTTP $http_code"
                fi
            fi
            
            # Check for required models
            echo ""
            echo "=== Ollama Models ==="
            
            local models_output=$(ollama list 2>/dev/null)
            if [[ $? -eq 0 && -n "$models_output" ]]; then
                local models=$(echo "$models_output" | tail -n +2 | awk '{print $1}' | grep -v '^$')
                
                if [[ -n "$models" ]]; then
                    print_status "INFO" "Available models:"
                    echo "$models" | while IFS= read -r model; do
                        if [[ -n "$model" && "$model" != "NAME" ]]; then
                            echo "  - $model"
                        fi
                    done
                    echo ""
                    
                    # Check for specific required models
                    local required_models=("mxbai-embed-large" "llama3.2")
                    for required_model in "${required_models[@]}"; do
                        local found=false
                        while IFS= read -r model; do
                            if [[ "$model" == "$required_model"* ]]; then
                                print_status "PASS" "Required model '$required_model' is available"
                                found=true
                                break
                            fi
                        done <<< "$models"
                        
                        if [[ "$found" == false ]]; then
                            print_status "FAIL" "Required model '$required_model' is not available"
                            print_status "INFO" "To install: ollama pull $required_model"
                        fi
                    done
                else
                    print_status "WARN" "No models found"
                    print_status "INFO" "To install required models:"
                    print_status "INFO" "  ollama pull mxbai-embed-large"
                    print_status "INFO" "  ollama pull llama3.2"
                fi
            else
                print_status "WARN" "Unable to list models (ollama list failed)"
                print_status "INFO" "To install required models:"
                print_status "INFO" "  ollama pull mxbai-embed-large"
                print_status "INFO" "  ollama pull llama3.2"
            fi
        else
            print_status "FAIL" "Ollama service is not running on port 11434"
            local os=$(detect_os)
            case $os in
                "windows")
                    print_status "INFO" "To start Ollama on Windows:"
                    print_status "INFO" "  - Run: ollama serve"
                    print_status "INFO" "  - Or start Ollama from Start Menu"
                    ;;
                *)
                    print_status "INFO" "To start Ollama: ollama serve"
                    ;;
            esac
        fi
    else
        print_status "FAIL" "Ollama is not installed"
        local os=$(detect_os)
        case $os in
            "windows")
                print_status "INFO" "To install Ollama on Windows:"
                print_status "INFO" "  - Download from: https://ollama.ai/download"
                print_status "INFO" "  - Or run: ./install_ollama.sh in Git Bash/WSL"
                ;;
            *)
                print_status "INFO" "To install Ollama, run: ./install_ollama.sh"
                ;;
        esac
    fi
}

# Function to provide recommendations
provide_recommendations() {
    echo ""
    echo "=== Summary ==="
    
    local os=$(detect_os)
    print_status "INFO" "Operating System: $os"
    
    if [[ "$ALL_CHECKS_PASSED" == true ]]; then
        print_status "PASS" "All checks passed! Your RAG system is ready to use."
        echo ""
        echo "🚀 Quick start commands:"
        echo "  1. Prepare vector store: python3 prepare_vector_store.py"
        echo "  2. Run the application: python3 app.py"
        echo "  3. Ask questions: python3 ask.py 'Your question here'"
    else
        print_status "WARN" "Some checks failed. Please address the issues above."
        echo ""
        echo "🔧 Common fixes:"
        case $os in
            "windows")
                echo "  - Start Qdrant: docker-compose up -d (requires Docker Desktop)"
                echo "  - Start Ollama: ollama serve (or from Start Menu)"
                echo "  - Pull models: ollama pull mxbai-embed-large && ollama pull llama3.2"
                echo "  - For better compatibility, consider using WSL (Windows Subsystem for Linux)"
                ;;
            *)
                echo "  - Start Qdrant: docker-compose up -d"
                echo "  - Start Ollama: ollama serve"
                echo "  - Pull models: ollama pull mxbai-embed-large && ollama pull llama3.2"
                ;;
        esac
    fi
}

# Main function
main() {
    echo "RAG System Health Check (Cross-Platform)"
    echo "========================================"
    echo "Checking Qdrant and Ollama services..."
    
    check_qdrant
    check_ollama
    provide_recommendations
    
    echo ""
    if [[ "$ALL_CHECKS_PASSED" == true ]]; then
        echo -e "${GREEN}🎉 Health check completed successfully!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Health check found issues that need attention.${NC}"
        exit 1
    fi
}

# Run the health check
main "$@"