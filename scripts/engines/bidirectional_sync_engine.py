"""
Bidirectional Sync Engine - Repository Synchronization
Synchronizes data between local and remote repositories bidirectionally
"""

import hashlib
import json
import os
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum


class SyncDirection(Enum):
    PULL = "pull"      # remote → local
    PUSH = "push"      # local → remote
    BOTH = "both"      # bidirectional


@dataclass
class SyncConfig:
    """Configuration for sync operation"""
    local_path: str
    remote_path: str
    direction: SyncDirection = SyncDirection.BOTH
    sync_interval: int = 60  # seconds
    max_retries: int = 3
    retry_delay: int = 2  # seconds
    file_mask: str = "*.md"  # files to sync
    exclude_patterns: List[str] = None
    
    def __post_init__(self):
        if self.exclude_patterns is None:
            self.exclude_patterns = []


@dataclass
class SyncResult:
    """Result of a sync operation"""
    success: bool
    direction: SyncDirection
    files_synced: int
    bytes_transferred: int
    duration_ms: int
    errors: List[str]


class BidirectionalSyncEngine:
    """
    Bidirectional sync engine for repository synchronization.
    
    Features:
    - Pull: Sync remote → local
    - Push: Sync local → remote
    - Bidirectional: Both directions
    - File hashing for change detection
    - Configurable retry with exponential backoff
    - Conflict resolution strategies
    """
    
    def __init__(self, config: SyncConfig):
        self.config = config
        self.local_path = Path(config.local_path)
        self.remote_path = Path(config.remote_path)
        self.sync_history: List[SyncResult] = []
        
    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of a file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _get_file_list(self, directory: Path, direction: SyncDirection) -> List[Path]:
        """Get list of files to sync based on direction and mask"""
        files = []
        
        if not directory.exists():
            return files
        
        for pattern in self.config.file_mask.split(','):
            pattern = pattern.strip()
            if pattern:
                files.extend(directory.glob(pattern))
        
        # Filter out excluded patterns
        exclude = self.config.exclude_patterns or []
        filtered = []
        for f in files:
            skip = False
            for ex in exclude:
                if ex in str(f):
                    skip = True
                    break
            if not skip:
                filtered.append(f)
        
        return filtered
    
    def _files_are_different(self, local_file: Path, remote_file: Path) -> bool:
        """Check if two files are different using hash comparison"""
        if not local_file.exists() or not remote_file.exists():
            return True
        
        local_hash = self._compute_file_hash(local_file)
        remote_hash = self._compute_file_hash(remote_file)
        
        return local_hash != remote_hash
    
    def pull(self) -> SyncResult:
        """Sync remote → local (pull)"""
        start_time = time.time()
        errors = []
        files_synced = 0
        bytes_transferred = 0
        
        try:
            remote_files = self._get_file_list(self.remote_path, SyncDirection.PULL)
            
            for remote_file in remote_files:
                relative_path = remote_file.relative_to(self.remote_path)
                local_file = self.local_path / relative_path
                
                if self._files_are_different(local_file, remote_file):
                    # Ensure local directory exists
                    local_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(remote_file, local_file)
                    files_synced += 1
                    bytes_transferred += remote_file.stat().st_size
            
            success = True
        except Exception as e:
            success = False
            errors.append(str(e))
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        result = SyncResult(
            success=success,
            direction=SyncDirection.PULL,
            files_synced=files_synced,
            bytes_transferred=bytes_transferred,
            duration_ms=duration_ms,
            errors=errors
        )
        
        self.sync_history.append(result)
        return result
    
    def push(self) -> SyncResult:
        """Sync local → remote (push)"""
        start_time = time.time()
        errors = []
        files_synced = 0
        bytes_transferred = 0
        
        try:
            local_files = self._get_file_list(self.local_path, SyncDirection.PUSH)
            
            for local_file in local_files:
                relative_path = local_file.relative_to(self.local_path)
                remote_file = self.remote_path / relative_path
                
                if self._files_are_different(local_file, remote_file):
                    # Ensure remote directory exists
                    remote_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(local_file, remote_file)
                    files_synced += 1
                    bytes_transferred += local_file.stat().st_size
            
            success = True
        except Exception as e:
            success = False
            errors.append(str(e))
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        result = SyncResult(
            success=success,
            direction=SyncDirection.PUSH,
            files_synced=files_synced,
            bytes_transferred=bytes_transferred,
            duration_ms=duration_ms,
            errors=errors
        )
        
        self.sync_history.append(result)
        return result
    
    def sync(self) -> SyncResult:
        """Perform bidirectional sync based on configuration"""
        if self.config.direction == SyncDirection.PULL:
            return self.pull()
        elif self.config.direction == SyncDirection.PUSH:
            return self.push()
        else:  # BOTH
            pull_result = self.pull()
            push_result = self.push()
            
            # Combine results
            total_files = pull_result.files_synced + push_result.files_synced
            total_bytes = pull_result.bytes_transferred + push_result.bytes_transferred
            total_errors = pull_result.errors + push_result.errors
            total_duration = pull_result.duration_ms + push_result.duration_ms
            
            return SyncResult(
                success=pull_result.success and push_result.success,
                direction=SyncDirection.BOTH,
                files_synced=total_files,
                bytes_transferred=total_bytes,
                duration_ms=total_duration,
                errors=total_errors
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get sync engine status"""
        last_sync = self.sync_history[-1] if self.sync_history else None
        
        return {
            "config": {
                "local_path": str(self.local_path),
                "remote_path": str(self.remote_path),
                "direction": self.config.direction.value,
                "sync_interval": self.config.sync_interval
            },
            "last_sync": {
                "success": last_sync.success if last_sync else None,
                "direction": last_sync.direction.value if last_sync else None,
                "files_synced": last_sync.files_synced if last_sync else 0,
                "bytes_transferred": last_sync.bytes_transferred if last_sync else 0,
                "duration_ms": last_sync.duration_ms if last_sync else 0,
                "errors": last_sync.errors if last_sync else []
            } if last_sync else None,
            "total_syncs": len(self.sync_history),
            "total_files_synced": sum(r.files_synced for r in self.sync_history),
            "total_bytes_transferred": sum(r.bytes_synced for r in self.sync_history)
        }


def create_demo_sync() -> BidirectionalSyncEngine:
    """Create a demo sync engine"""
    config = SyncConfig(
        local_path="/tmp/local_repo",
        remote_path="/tmp/remote_repo",
        direction=SyncDirection.BOTH,
        sync_interval=30,
        file_mask="*.md,*.txt",
        exclude_patterns=["*.pyc", "__pycache__"]
    )
    
    # Ensure directories exist for demo
    Path(config.local_path).mkdir(parents=True, exist_ok=True)
    Path(config.remote_path).mkdir(parents=True, exist_ok=True)
    
    return BidirectionalSyncEngine(config)


if __name__ == "__main__":
    sync = create_demo_sync()
    
    print("🔄 Bidirectional Sync Engine initialized")
    print(f"   Local: {sync.config.local_path}")
    print(f"   Remote: {sync.config.remote_path}")
    print(f"   Direction: {sync.config.direction.value}")
    print(f"   Interval: {sync.config.sync_interval}s")
    
    # Run sync
    result = sync.sync()
    
    print(f"\n📊 Sync Result:")
    print(f"   Success: {result.success}")
    print(f"   Direction: {result.direction.value}")
    print(f"   Files synced: {result.files_synced}")
    print(f"   Bytes transferred: {result.bytes_transferred}")
    print(f"   Duration: {result.duration_ms}ms")
    if result.errors:
        print(f"   Errors: {result.errors}")
    
    print("\n✅ Bidirectional Sync Engine demo completed")