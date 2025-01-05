import os
import shutil
import psutil
import subprocess
from typing import Tuple, Optional
from src.utils.logger import Logger

log = Logger()

def find_usb_drive(min_size_gb: int = 4) -> Optional[str]:
    log.info("Looking for USB device...")
    partitions = psutil.disk_partitions(all=True)
    for partition in partitions:
        if is_valid_usb(partition):
            log.ok("USB device found")
            return partition.mountpoint
    log.info("No USB device connected")
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
    files_copied = 0
    total_size = 0
    for root, dirs, files in os.walk(source):
        relative_path = os.path.relpath(root, source)
        target_dir = os.path.join(destination) if relative_path == '.' else os.path.join(destination, relative_path)
        os.makedirs(target_dir, exist_ok=True)
        for file in files:
            files_copied += 1
            log.wait(f"Copying file {files_copied}/{total_files}")
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_dir, file)
            file_size = os.path.getsize(src_file)
            total_size += file_size
            try:
                shutil.copy2(src_file, dst_file)
                log.info(f"Progress: {files_copied}/{total_files} files ({total_size/1024/1024:.1f} MB)")
            except Exception as e:
                log.error(f"Unable to copy {file}: {str(e)}")
                raise
    log.ok(f"Copy complete: {files_copied} files ({total_size/1024/1024:.1f} MB)")
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
        free_space_gb = usage.free / (1024**3)
        if total_size_gb < 4:
            log.debug(f"Device too small ({total_size_gb:.1f} GB)")
            return False
        log.debug(f"Device found: {total_size_gb:.1f} GB ({free_space_gb:.1f} GB free)")
    except Exception as e:
        log.debug(f"Could not check drive size: {str(e)}")
        return False
    return True
