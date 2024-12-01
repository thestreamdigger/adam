import os
import shutil
import psutil
import subprocess
from typing import Tuple, Optional

def find_usb_drive(min_size_gb: int = 4) -> Optional[str]:
    """Find suitable USB drive for copying"""
    print("\n=== USB DRIVE DETECTION DETAILS ===")
    print(f"Minimum size required: {min_size_gb} GB")
    
    partitions = psutil.disk_partitions(all=True)
    print(f"\nFound {len(partitions)} partitions in system:")
    
    for partition in partitions:
        print(f"\nChecking partition:")
        print(f"  Device: {partition.device}")
        print(f"  Mountpoint: {partition.mountpoint}")
        print(f"  Filesystem: {partition.fstype}")
        print(f"  Options: {partition.opts}")
        
        if partition.device.startswith(('/dev/sd', '/dev/usb', '/dev/disk')):
            print("  Status: Potential USB device (correct device pattern)")
            
            result = subprocess.run(['lsblk', '-ndo', 'rm', partition.device], 
                               capture_output=True, text=True)
            
            is_removable = result.stdout.strip() == '1'
            print(f"  Removable: {is_removable}")
            
            if is_removable:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    size_gb = usage.total / (1024 * 1024 * 1024)
                    free_gb = usage.free / (1024 * 1024 * 1024)
                    print(f"  Total size: {size_gb:.2f} GB")
                    print(f"  Free space: {free_gb:.2f} GB")
                    
                    if size_gb >= min_size_gb:
                        print("  Status: SELECTED (meets size requirement)")
                        return partition.mountpoint
                    else:
                        print(f"  Status: Rejected (too small, needs {min_size_gb} GB)")
                except PermissionError:
                    print("  Status: Rejected (permission denied)")
                    continue
        else:
            print("  Status: Rejected (not a USB device pattern)")
    
    print("\nNo suitable USB drive found")
    return None

def copy_directory(source: str, destination: str) -> Tuple[int, int]:
    """Copy directory with tracking of files and size"""
    if not os.path.exists(source):
        raise FileNotFoundError(f"Source directory not found: {source}")
    
    print("\nAnalyzing source directory...")
    total_files = sum(len(files) for _, _, files in os.walk(source))
    print(f"Total files found: {total_files}")
        
    files_copied = 0
    total_size = 0
    
    destination = os.path.dirname(destination)
    print(f"\nAdjusted destination path: {destination}")
    
    for root, dirs, files in os.walk(source):
        relative_path = os.path.relpath(root, os.path.dirname(source))
        target_dir = os.path.join(destination, relative_path) if relative_path != '.' else destination
        
        print(f"Processing directory: {relative_path if relative_path != '.' else 'root'}")
        print(f"Creating directory: {target_dir}")
        os.makedirs(target_dir, exist_ok=True)
        
        if dirs:
            print("Subdirectories to process:", dirs)
        
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_dir, file)
            
            try:
                file_size = os.path.getsize(src_file)
                print(f"\nCopying file ({files_copied + 1}/{total_files}):")
                print(f"  Name: {file}")
                print(f"  Size: {file_size/1024/1024:.2f} MB")
                print(f"  From: {src_file}")
                print(f"  To: {dst_file}")
                
                shutil.copy2(src_file, dst_file)
                files_copied += 1
                total_size += file_size
                print(f"  Status: Successfully copied")
                print(f"Progress: {files_copied}/{total_files} files")
                print(f"Total size so far: {total_size/1024/1024:.2f} MB")
                
            except Exception as e:
                print(f"  ERROR copying {file}: {str(e)}")
                raise
    
    return files_copied, total_size
