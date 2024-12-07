import os
import shutil
import psutil
import subprocess
from typing import Tuple, Optional

def find_usb_drive(min_size_gb: int = 4) -> Optional[str]:
    print("\n=== USB DRIVE DETECTION ===")
    print(f"  Required size: {min_size_gb} GB")
    
    partitions = psutil.disk_partitions(all=True)
    print(f"  Found partitions: {len(partitions)}")
    
    for partition in partitions:
        print("\n  Checking partition:")
        print(f"  Device: {partition.device}")
        print(f"  Mountpoint: {partition.mountpoint}")
        print(f"  Filesystem: {partition.fstype}")
        print(f"  Options: {partition.opts}")
        
        if is_valid_usb(partition):
            print("  Status: Valid USB device found")
            return partition.mountpoint
            
    print("ERROR: No compatible USB device found")
    return None

def copy_directory(source: str, destination: str) -> Tuple[int, int]:
    if not os.path.exists(source):
        print(f"ERROR: Source directory not found: {source}")
        raise FileNotFoundError(f"Source directory not found: {source}")
    
    print("\n=== COPY ANALYSIS ===")
    print(f"  Total files: {total_files}")
    print(f"  Source: {source}")
    print(f"  Destination: {destination}")
    
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
