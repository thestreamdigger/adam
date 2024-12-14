import os
import shutil
import psutil
import subprocess
from typing import Tuple, Optional
from src.utils.logger import Logger

log = Logger()

def find_usb_drive(min_size_gb: int = 4) -> Optional[str]:
    log.info("=== USB DRIVE DETECTION ===")
    log.info(f"Required size: {min_size_gb} GB")
    
    partitions = psutil.disk_partitions(all=True)
    log.debug(f"Found partitions: {len(partitions)}")
    
    for partition in partitions:
        log.info("Checking partition:")
        log.debug(f"Device: {partition.device}")
        log.debug(f"Mountpoint: {partition.mountpoint}")
        log.debug(f"Filesystem: {partition.fstype}")
        log.debug(f"Options: {partition.opts}")
        
        if is_valid_usb(partition):
            log.ok("Valid USB device found")
            return partition.mountpoint
            
    log.error("No compatible USB device found")
    return None

def copy_directory(source: str, destination: str) -> Tuple[int, int]:
    if not os.path.exists(source):
        log.error(f"Source directory not found: {source}")
        raise FileNotFoundError(f"Source directory not found: {source}")
    
    total_files = sum([len(files) for _, _, files in os.walk(source)])
    
    log.info("=== COPY ANALYSIS ===")
    log.debug(f"Total files: {total_files}")
    log.debug(f"Source: {source}")
    log.debug(f"Destination: {destination}")
    
    log.info(f"Adjusted destination path: {destination}")
    
    files_copied = 0
    total_size = 0
    
    for root, dirs, files in os.walk(source):
        relative_path = os.path.relpath(root, source)
        log.debug(f"Processing: {relative_path if relative_path != '.' else 'root'}")
        
        target_dir = os.path.join(destination) if relative_path == '.' else os.path.join(destination, relative_path)
        
        os.makedirs(target_dir, exist_ok=True)
        log.debug(f"Creating directory: {target_dir}")
        
        for file in files:
            files_copied += 1
            log.wait(f"Copying file {files_copied}/{total_files}")
            
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_dir, file)
            
            file_size = os.path.getsize(src_file)
            total_size += file_size
            
            log.debug(f"Name: {file}")
            log.debug(f"Size: {file_size/1024/1024:.2f} MB")
            log.debug(f"From: {src_file}")
            log.debug(f"To: {dst_file}")
            
            try:
                shutil.copy2(src_file, dst_file)
                log.ok("File copied successfully")
                log.info(f"Progress: {files_copied}/{total_files} files")
                log.info(f"Total size: {total_size/1024/1024:.2f} MB")
                
            except Exception as e:
                log.error(f"Unable to copy {file}: {str(e)}")
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
        log.info(f"Drive size: {total_size_gb:.1f} GB")
        
        if total_size_gb < 4:
            log.warning(f"Drive too small ({total_size_gb:.1f} GB)")
            return False
            
        log.info(f"Free space: {(usage.free / (1024**3)):.1f} GB")
        
    except Exception as e:
        log.error(f"Failed to check drive size: {str(e)}")
        return False
        
    return True
