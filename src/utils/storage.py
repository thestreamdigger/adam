import os
import shutil
import psutil
import subprocess
from typing import Tuple, Optional

def find_usb_drive(min_size_gb: int = 4) -> Optional[str]:
    print("[INFO]   === USB DRIVE DETECTION ===")
    print(f"[INFO]   Required size: {min_size_gb} GB")
    
    partitions = psutil.disk_partitions(all=True)
    print(f"[DEBUG]  Found partitions: {len(partitions)}")
    
    for partition in partitions:
        print("[INFO]   Checking partition:")
        print(f"[DEBUG]  Device: {partition.device}")
        print(f"[DEBUG]  Mountpoint: {partition.mountpoint}")
        print(f"[DEBUG]  Filesystem: {partition.fstype}")
        print(f"[DEBUG]  Options: {partition.opts}")
        
        if is_valid_usb(partition):
            print("[OK]     Valid USB device found")
            return partition.mountpoint
            
    print("[ERROR]  No compatible USB device found")
    return None

def copy_directory(source: str, destination: str) -> Tuple[int, int]:
    if not os.path.exists(source):
        print(f"[ERROR]  Source directory not found: {source}")
        raise FileNotFoundError(f"Source directory not found: {source}")
    
    total_files = sum([len(files) for _, _, files in os.walk(source)])
    
    print("[INFO]   === COPY ANALYSIS ===")
    print(f"[DEBUG]  Total files: {total_files}")
    print(f"[DEBUG]  Source: {source}")
    print(f"[DEBUG]  Destination: {destination}")
    
    print(f"[INFO]   Adjusted destination path: {destination}")
    
    files_copied = 0
    total_size = 0
    
    for root, dirs, files in os.walk(source):
        relative_path = os.path.relpath(root, source)
        print(f"[DEBUG]  Processing: {relative_path if relative_path != '.' else 'root'}")
        
        target_dir = os.path.join(destination) if relative_path == '.' else os.path.join(destination, relative_path)
        
        os.makedirs(target_dir, exist_ok=True)
        print(f"[DEBUG]  Creating directory: {target_dir}")
        
        for file in files:
            files_copied += 1
            print(f"[WAIT]   Copying file {files_copied}/{total_files}")
            
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_dir, file)
            
            file_size = os.path.getsize(src_file)
            total_size += file_size
            
            print(f"[DEBUG]  Name: {file}")
            print(f"[DEBUG]  Size: {file_size/1024/1024:.2f} MB")
            print(f"[DEBUG]  From: {src_file}")
            print(f"[DEBUG]  To: {dst_file}")
            
            try:
                shutil.copy2(src_file, dst_file)
                print("[OK]     File copied successfully")
                print(f"[INFO]   Progress: {files_copied}/{total_files} files")
                print(f"[INFO]   Total size: {total_size/1024/1024:.2f} MB")
                
            except Exception as e:
                print(f"[ERROR]  Unable to copy {file}: {str(e)}")
                raise
    
    return files_copied, total_size

def is_valid_usb(partition) -> bool:
    if not partition.device.startswith('/dev/sd'):
        return False
        
    if not partition.mountpoint:
        return False
        
    if partition.fstype not in ['vfat', 'exfat', 'ntfs', 'ext4']:
        return False
        
    try:
        usage = shutil.disk_usage(partition.mountpoint)
        total_size_gb = usage.total / (1024**3)
        print(f"[INFO]   Drive size: {total_size_gb:.1f} GB")
        
        if total_size_gb < 4:
            print(f"[WARN]   Drive too small ({total_size_gb:.1f} GB)")
            return False
            
        print(f"[INFO]   Free space: {(usage.free / (1024**3)):.1f} GB")
        
    except Exception as e:
        print(f"[ERROR]  Failed to check drive size: {str(e)}")
        return False
        
    return True
