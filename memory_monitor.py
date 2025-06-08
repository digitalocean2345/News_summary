#!/usr/bin/env python3
"""
Simple memory monitor for 512MB droplet
Run this to check if your application is using too much memory
"""

import subprocess
import time
import os

def get_memory_info():
    """Get current memory usage information"""
    try:
        # Get memory info
        result = subprocess.run(['free', '-m'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        
        # Parse memory line
        mem_line = lines[1].split()
        total = int(mem_line[1])
        used = int(mem_line[2])
        available = int(mem_line[6])
        
        usage_percent = (used / total) * 100
        
        return {
            'total': total,
            'used': used,
            'available': available,
            'usage_percent': usage_percent
        }
    except Exception as e:
        print(f"Error getting memory info: {e}")
        return None

def get_gunicorn_memory():
    """Get memory usage of Gunicorn processes"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        gunicorn_processes = []
        
        for line in result.stdout.split('\n'):
            if 'gunicorn' in line and 'app.main:app' in line:
                parts = line.split()
                if len(parts) >= 6:
                    pid = parts[1]
                    mem_percent = float(parts[3])
                    mem_kb = int(parts[5])
                    mem_mb = mem_kb / 1024
                    
                    gunicorn_processes.append({
                        'pid': pid,
                        'mem_percent': mem_percent,
                        'mem_mb': mem_mb
                    })
        
        return gunicorn_processes
    except Exception as e:
        print(f"Error getting Gunicorn memory: {e}")
        return []

def check_oom_history():
    """Check for recent OOM kills"""
    try:
        result = subprocess.run(['dmesg | grep -i "killed process" | tail -5'], 
                              shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            return result.stdout.strip().split('\n')
        return []
    except Exception:
        return []

def main():
    """Main monitoring function"""
    print("🔍 Memory Monitor for 512MB Droplet")
    print("=" * 50)
    
    # Get system memory info
    mem_info = get_memory_info()
    if mem_info:
        print(f"\n💾 System Memory:")
        print(f"   Total: {mem_info['total']} MB")
        print(f"   Used:  {mem_info['used']} MB ({mem_info['usage_percent']:.1f}%)")
        print(f"   Free:  {mem_info['available']} MB")
        
        # Memory status
        if mem_info['usage_percent'] > 90:
            print("   🔴 CRITICAL: Very high memory usage!")
        elif mem_info['usage_percent'] > 80:
            print("   🟡 WARNING: High memory usage")
        else:
            print("   🟢 OK: Normal memory usage")
    
    # Get Gunicorn process memory
    gunicorn_procs = get_gunicorn_memory()
    if gunicorn_procs:
        print(f"\n🐍 Gunicorn Processes ({len(gunicorn_procs)} workers):")
        total_gunicorn_mb = 0
        for proc in gunicorn_procs:
            print(f"   PID {proc['pid']}: {proc['mem_mb']:.1f} MB ({proc['mem_percent']:.1f}%)")
            total_gunicorn_mb += proc['mem_mb']
        
        print(f"   Total Gunicorn Memory: {total_gunicorn_mb:.1f} MB")
        
        if len(gunicorn_procs) > 1:
            print("   💡 Consider reducing workers on 512MB droplet")
    else:
        print("\n🐍 No Gunicorn processes found")
    
    # Check OOM history
    oom_history = check_oom_history()
    if oom_history:
        print(f"\n⚠️  Recent OOM Kills:")
        for oom in oom_history[-3:]:  # Last 3
            print(f"   {oom}")
    else:
        print(f"\n✅ No recent OOM kills detected")
    
    # Recommendations
    print(f"\n💡 Recommendations for 512MB droplet:")
    if mem_info and mem_info['usage_percent'] > 80:
        print("   - Memory usage is high, consider:")
        print("   - Reducing Gunicorn workers to 1")
        print("   - Adding swap space")
        print("   - Upgrading to larger droplet")
    
    if gunicorn_procs and len(gunicorn_procs) > 1:
        print("   - Currently running multiple workers")
        print("   - Reduce to 1 worker: gunicorn app.main:app -w 1 ...")
    
    print("\n🔧 Quick fixes:")
    print("   1. Reduce workers: python fix_deployment.py")
    print("   2. Restart service: sudo systemctl restart news-summary")
    print("   3. Monitor continuously: watch -n 5 'free -h && ps aux | grep gunicorn'")

if __name__ == "__main__":
    main() 