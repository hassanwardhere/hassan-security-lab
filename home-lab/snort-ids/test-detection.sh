#!/bin/bash
#------------------------------------------------------------------------------
# Snort IDS Detection Testing Script
# Project: Home Lab IDS
# Author: Hassan Abdulahi Hassan
# Description: Test Snort IDS detection capabilities
#------------------------------------------------------------------------------

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TARGET_IP="${1:-127.0.0.1}"
LOG_FILE="/mnt/hdd/snort/logs/alert.json"

# Functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

check_prerequisites() {
    print_header "CHECKING PREREQUISITES"
    
    # Check if running as root for certain tests
    if [ "$EUID" -ne 0 ]; then
        print_warning "Not running as root - some tests may fail"
    fi
    
    # Check for required tools
    command -v nmap >/dev/null 2>&1 || { print_error "nmap not found. Install with: sudo apt install nmap"; exit 1; }
    command -v curl >/dev/null 2>&1 || { print_error "curl not found. Install with: sudo apt install curl"; exit 1; }
    
    # Check if Snort is running
    if docker ps | grep -q snort-ids; then
        print_success "Snort IDS container is running"
    else
        print_error "Snort IDS container is not running. Start with: docker-compose up -d"
        exit 1
    fi
    
    # Check log directory
    if [ -d "/mnt/hdd/snort/logs" ]; then
        print_success "Log directory exists"
    else
        print_error "Log directory not found at /mnt/hdd/snort/logs"
        exit 1
    fi
    
    print_success "Prerequisites check complete"
}

test_port_scans() {
    print_header "TESTING PORT SCAN DETECTION"
    
    print_info "Testing SYN Scan..."
    sudo nmap -sS -p 1-50 --open $TARGET_IP -oN /dev/null 2>&1 || true
    sleep 2
    
    print_info "Testing FIN Scan..."
    sudo nmap -sF -p 1-50 $TARGET_IP -oN /dev/null 2>&1 || true
    sleep 2
    
    print_info "Testing NULL Scan..."
    sudo nmap -sN -p 1-50 $TARGET_IP -oN /dev/null 2>&1 || true
    sleep 2
    
    print_info "Testing XMAS Scan..."
    sudo nmap -sX -p 1-50 $TARGET_IP -oN /dev/null 2>&1 || true
    sleep 2
    
    print_info "Testing ACK Scan..."
    sudo nmap -sA -p 1-50 $TARGET_IP -oN /dev/null 2>&1 || true
    sleep 2
    
    print_success "Port scan tests completed"
}

test_web_attacks() {
    print_header "TESTING WEB ATTACK DETECTION"
    
    # SQL Injection tests
    print_info "Testing SQL Injection - UNION SELECT..."
    curl -s "http://$TARGET_IP/test.php?id=1%27%20UNION%20SELECT%20*%20FROM%20users--" -o /dev/null || true
    sleep 1
    
    print_info "Testing SQL Injection - OR 1=1..."
    curl -s "http://$TARGET_IP/test.php?id=1%27%20OR%20%271%27=%271" -o /dev/null || true
    sleep 1
    
    print_info "Testing SQL Injection - SLEEP..."
    curl -s "http://$TARGET_IP/test.php?id=1%27%20AND%20SLEEP(5)--" -o /dev/null || true
    sleep 1
    
    # XSS tests
    print_info "Testing XSS - Script tag..."
    curl -s "http://$TARGET_IP/search.php?q=%3Cscript%3Ealert(1)%3C/script%3E" -o /dev/null || true
    sleep 1
    
    print_info "Testing XSS - onEvent handler..."
    curl -s "http://$TARGET_IP/search.php?q=%3Cimg%20src=x%20onerror=alert(1)%3E" -o /dev/null || true
    sleep 1
    
    print_info "Testing XSS - JavaScript protocol..."
    curl -s "http://$TARGET_IP/redirect?url=javascript:alert(1)" -o /dev/null || true
    sleep 1
    
    # Directory Traversal
    print_info "Testing Directory Traversal..."
    curl -s "http://$TARGET_IP/page.php?file=../../../etc/passwd" -o /dev/null || true
    sleep 1
    
    print_success "Web attack tests completed"
}

test_ssh_attacks() {
    print_header "TESTING SSH BRUTE FORCE DETECTION"
    
    print_info "Simulating SSH connection attempts..."
    for i in {1..7}; do
        ssh -o ConnectTimeout=2 -o BatchMode=yes test@$TARGET_IP 2>/dev/null || true
        sleep 1
    done
    
    print_success "SSH brute force simulation completed"
}

check_alerts() {
    print_header "CHECKING GENERATED ALERTS"
    
    sleep 3
    
    if [ -f "$LOG_FILE" ]; then
        print_success "Alert log file exists"
        
        # Count alerts
        ALERT_COUNT=$(wc -l < "$LOG_FILE" 2>/dev/null || echo "0")
        print_info "Total alerts in log: $ALERT_COUNT"
        
        # Show recent alerts
        if [ "$ALERT_COUNT" -gt 0 ]; then
            print_info "Recent alerts:"
            tail -n 20 "$LOG_FILE" | while read line; do
                echo "  - $line"
            done
        fi
    else
        print_warning "Alert log file not found at $LOG_FILE"
        print_info "Note: Alerts may take a few minutes to appear"
    fi
}

show_summary() {
    print_header "TEST SUMMARY"
    
    echo -e "Target IP: ${GREEN}$TARGET_IP${NC}"
    echo -e "Log File: ${GREEN}$LOG_FILE${NC}"
    echo -e ""
    echo -e "Tests Performed:"
    echo -e "  ${GREEN}•${NC} Port Scan Detection (SYN, FIN, NULL, XMAS, ACK)"
    echo -e "  ${GREEN}•${NC} SQL Injection Detection"
    echo -e "  ${GREEN}•${NC} XSS Detection"
    echo -e "  ${GREEN}•${NC} Directory Traversal Detection"
    echo -e "  ${GREEN}•${NC} SSH Brute Force Simulation"
    echo -e ""
    echo -e "To monitor alerts in real-time:"
    echo -e "  ${YELLOW}tail -f $LOG_FILE${NC}"
    echo -e ""
    echo -e "To view all alerts:"
    echo -e "  ${YELLOW}cat $LOG_FILE | jq .${NC}"
}

# Main execution
main() {
    print_header "SNORT IDS DETECTION TEST"
    echo -e "Target: ${YELLOW}$TARGET_IP${NC}"
    echo -e "Date: $(date)"
    echo ""
    
    check_prerequisites
    test_port_scans
    test_web_attacks
    test_ssh_attacks
    check_alerts
    show_summary
    
    print_header "TESTING COMPLETE"
}

# Run main function
main