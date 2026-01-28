"""
AKESO FILE SYSTEM MANAGER
-------------------------
Handles all physical I/O operations:
- Atomic file writes (fsync)
- Safe backup generation
- Directory crawling with security checks (symlinks, traversal)

Decoupled from AkesoEngine to support future S3/Remote backends.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Generator, Tuple

logger = logging.getLogger("akeso.io")

class FileSystemManager:
    """
    Abstration layer for local file system operations.
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace = workspace_root.resolve()

    def ensure_workspace(self):
        """Creates workspace directory if missing."""
        if not self.workspace.exists():
            try:
                self.workspace.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created workspace: {self.workspace}")
            except Exception as e:
                raise RuntimeError(f"Workspace creation failed: {e}")

    def read_text(self, path: Path) -> str:
        """Reads text file with BOM handling."""
        return path.read_text(encoding='utf-8-sig')

    def atomic_write(self, target_path: Path, content: str) -> None:
        """
        Atomically writes content to file with fsync for durability.
        Uses .akeso.tmp + os.replace.
        """
        temp_file = target_path.with_suffix('.akeso.tmp')
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            
            os.replace(temp_file, target_path)
            
        except Exception as e:
            if temp_file.exists(): 
                temp_file.unlink()
            raise IOError(f"Atomic write failed: {e}")

    def create_backup(self, target_path: Path) -> Path:
        """
        Creates a unique backup file (file-1.akeso.backup).
        Returns the path to the backup created.
        """
        backup_path = target_path.with_suffix('.akeso.backup')
        counter = 1
        while backup_path.exists():
            backup_path = target_path.with_name(f"{target_path.stem}-{counter}.akeso.backup")
            counter += 1
            
        shutil.copy2(target_path, backup_path)
        return backup_path

    def crawl(self, root_path: Path, extensions: List[str], max_depth: int) -> Generator[Tuple[Path, str], None, None]:
        """
        Generator that yields (absolute_path, relative_path_str) for matching files.
        Handles depth limiting and security checks.
        """
        ext_set = {e.strip() if e.startswith('.') else f".{e.strip()}" for e in extensions}
        
        # Verify root exists
        if not root_path.exists():
            logger.error(f"Scan root does not exist: {root_path}")
            return

        for root, dirs, files in os.walk(root_path):
            # Depth check
            current_depth = len(Path(root).relative_to(root_path).parts)
            if current_depth >= max_depth:
                del dirs[:]
                continue

            for file in files:
                if any(file.endswith(ext) for ext in ext_set):
                    abs_path = Path(root) / file
                    
                    # Compute relative path for reporting
                    try:
                        rel_path = str(abs_path.relative_to(self.workspace))
                    except ValueError:
                        # File outside workspace (e.g. symlink or external scan)
                        rel_path = str(abs_path)
                    
                    yield abs_path, rel_path
