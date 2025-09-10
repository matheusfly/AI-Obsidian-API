#!/usr/bin/env python3
"""
Enhanced Filesystem Vault Client
Filesystem-first approach for Obsidian vault access with rich metadata extraction
"""

import asyncio
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import frontmatter
import logging

logger = logging.getLogger(__name__)

class FilesystemVaultClient:
    """Enhanced filesystem client for Obsidian vault access"""
    
    def __init__(self, vault_path: str):
        """
        Initialize the client with the path to the Obsidian vault.
        Args:
            vault_path (str): The absolute path to the root of the Obsidian vault (e.g., "D:\\Nomade Milionario").
        """
        self.vault_root = Path(vault_path)
        if not self.vault_root.exists():
            raise FileNotFoundError(f"Vault path does not exist: {vault_path}")
        if not self.vault_root.is_dir():
            raise NotADirectoryError(f"Vault path is not a directory: {vault_path}")
        
        logger.info(f"Initialized FilesystemVaultClient for vault: {self.vault_root}")

    async def list_vault_files(self) -> List[Dict[str, Any]]:
        """
        Asynchronously list all markdown files in the vault.
        Returns:
            List[Dict[str, Any]]: A list of file info dictionaries.
        """
        # For true async file I/O on Windows, we use asyncio.to_thread for CPU-bound path operations.
        files = await asyncio.to_thread(self._sync_list_files)
        logger.info(f"Found {len(files)} markdown files in vault.")
        return files

    def _sync_list_files(self) -> List[Dict[str, Any]]:
        """Synchronous helper for listing files."""
        files = []
        for file_path in self.vault_root.rglob("*.md"):
            try:
                stat = file_path.stat()
                relative_path = file_path.relative_to(self.vault_root).as_posix()  # Use forward slashes for consistency
                files.append({
                    "path": relative_path,
                    "name": file_path.name,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,  # Unix timestamp
                    "created": stat.st_ctime,   # Unix timestamp (on Windows, this is creation time)
                })
            except (OSError, PermissionError) as e:
                logger.error(f"Error accessing file {file_path}: {e}")
                continue  # Skip problematic files
        return files

    async def get_file_content(self, relative_path: str) -> Dict[str, Any]:
        """
        Asynchronously read the content and extract metadata for a specific file.
        Args:
            relative_path (str): The file's path relative to the vault root.
        Returns:
            Dict[str, Any]: A dictionary containing content, path, and extracted metadata.
        Raises:
            FileNotFoundError: If the file does not exist.
        """
        full_path = self.vault_root / relative_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")

        # Read file content
        content, stat = await asyncio.to_thread(self._sync_read_file, full_path)

        # Extract metadata and get cleaned content
        metadata, cleaned_content = self._extract_metadata(content, full_path, stat)

        return {
            "path": relative_path,
            "name": full_path.name,
            "content": cleaned_content,  # Use cleaned content (without frontmatter)
            "metadata": metadata  # All extracted metadata goes here
        }

    def _sync_read_file(self, full_path: Path) -> tuple[str, os.stat_result]:
        """Synchronous helper for reading a file."""
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        stat = full_path.stat()
        return content, stat

    def _extract_metadata(self, content: str, file_path: Path, stat: os.stat_result) -> tuple[Dict[str, Any], str]:
        """
        Extract rich metadata from the file content and its system stats.
        Returns both metadata AND cleaned content (without frontmatter).
        """
        metadata = {
            # Basic File Stats
            "file_size": stat.st_size,
            "file_modified": stat.st_mtime,
            "file_created": stat.st_ctime,
            "file_word_count": len(content.split()),
            "file_char_count": len(content),
            # File Structure
            "file_name": file_path.name,
            "file_extension": file_path.suffix.lower().lstrip('.') if file_path.suffix else "",
            "directory_path": file_path.parent.relative_to(self.vault_root).as_posix() if file_path.parent != self.vault_root else "",
            # Tags (Separated)
            "frontmatter_tags": [],
            "content_tags": [],
            "has_frontmatter": False,
            "frontmatter_keys": [],
            # Legacy fields for compatibility
            "frontmatter": {},
            "in_content_tags": [],
            "links": []
        }

        # Parse Frontmatter with robust error handling
        try:
            post = frontmatter.loads(content)
            fm = post.metadata
            metadata["has_frontmatter"] = True
            metadata["frontmatter_keys"] = list(fm.keys())
            metadata["frontmatter"] = fm  # Keep for compatibility

            # Extract tags from frontmatter (can be list or string)
            fm_tags = fm.get('tags', [])
            if isinstance(fm_tags, str):
                fm_tags = [tag.strip() for tag in fm_tags.split(',')]
            elif isinstance(fm_tags, list):
                fm_tags = [str(tag).strip() for tag in fm_tags]
            metadata["frontmatter_tags"] = fm_tags

            # Update content to be without frontmatter for cleaner chunking
            content = post.content

        except Exception as e:
            logger.debug(f"No frontmatter or parsing error in {file_path}: {e}")

        # Extract in-content tags with enhanced semantic filtering
        # Multiple patterns to capture different tag formats
        tag_patterns = [
            r'(?<!\S)#([a-zA-Z][a-zA-Z0-9]*(?:[-_][a-zA-Z0-9]+)*)',  # Semantic tags starting with letter
            r'\[\[([a-zA-Z][a-zA-Z0-9]*(?:[-_][a-zA-Z0-9]+)*)\]\]',  # Obsidian links
            r'@([a-zA-Z][a-zA-Z0-9]*(?:[-_][a-zA-Z0-9]+)*)',         # Mention-style tags
        ]
        
        content_tags = []
        for pattern in tag_patterns:
            matches = re.findall(pattern, content)
            content_tags.extend(matches)
        
        # Filter out common non-semantic patterns
        filtered_tags = []
        for tag in content_tags:
            tag_lower = tag.lower()
            # Skip if it's purely numeric or common non-semantic patterns
            if (not tag.isdigit() and 
                tag_lower not in ['todo', 'done', 'note', 'temp', 'draft'] and
                len(tag) > 1):
                filtered_tags.append(tag)
        
        metadata["content_tags"] = filtered_tags
        metadata["in_content_tags"] = filtered_tags  # Keep for compatibility

        # Extract internal Obsidian links (optional)
        link_pattern = r'\[\[(.*?)\]\]'
        metadata["links"] = re.findall(link_pattern, content)

        # Extract path patterns for enhanced filtering
        self._extract_path_patterns(file_path, metadata)

        return metadata, content  # Return both metadata AND cleaned content

    def _extract_path_patterns(self, file_path: Path, metadata: Dict[str, Any]):
        """Extract patterns from file path for enhanced filtering."""
        path_str = str(file_path)
        filename = file_path.name
        
        # Extract year from path (e.g., "2025-01-09" or "2025")
        year_pattern = r'(?:^|[/\\])(\d{4})(?:[/\\]|$)'
        year_match = re.search(year_pattern, path_str)
        if year_match:
            metadata["path_year"] = int(year_match.group(1))
        
        # Extract year and month from filename (e.g., "2025-01-09_11-23-28_...")
        filename_year_pattern = r'^(\d{4})-(\d{1,2})-(\d{1,2})'
        filename_match = re.search(filename_year_pattern, filename)
        if filename_match:
            metadata["path_year"] = int(filename_match.group(1))
            metadata["path_month"] = int(filename_match.group(2))
            metadata["path_day"] = int(filename_match.group(3))
        
        # Extract category from path (directory structure)
        path_parts = file_path.parts
        if len(path_parts) > 1:
            metadata["path_category"] = path_parts[-2]  # Parent directory
            metadata["path_subcategory"] = path_parts[-3] if len(path_parts) > 2 else None
        
        # Extract file type patterns
        if 'excalidraw' in filename.lower():
            metadata["file_type"] = "excalidraw"
        elif 'template' in filename.lower():
            metadata["file_type"] = "template"
        elif filename.startswith('2025-'):
            metadata["file_type"] = "dated_note"
        elif filename.startswith('AGENTS'):
            metadata["file_type"] = "agent_doc"
        
        # Extract project indicators
        project_indicators = ['project', 'task', 'meeting', 'note', 'idea', 'research']
        for indicator in project_indicators:
            if indicator in filename.lower():
                metadata["content_type"] = indicator
                break

    async def get_multiple_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Asynchronously read multiple files in parallel.
        Args:
            file_paths (List[str]): List of relative file paths.
        Returns:
            List[Dict[str, Any]]: List of file content dictionaries.
        """
        tasks = [self.get_file_content(path) for path in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error reading file {file_paths[i]}: {result}")
            else:
                valid_results.append(result)
        
        return valid_results

    def get_vault_stats(self) -> Dict[str, Any]:
        """Get comprehensive vault statistics."""
        files = self._sync_list_files()
        total_size = sum(f["size"] for f in files)
        
        return {
            "total_files": len(files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "vault_path": str(self.vault_root),
            "files_sample": files[:5]  # First 5 files as sample
        }
