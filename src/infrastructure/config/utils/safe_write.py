import hashlib
from typing import Optional, Tuple

def compute_content_hash(content: str) -> str:
    """Compute SHA256 hash of content"""
    return hashlib.sha256(content.encode()).hexdigest()

def validate_precondition(content: str, if_match: Optional[str]) -> Tuple[bool, str]:
    """
    Validate precondition for safe writes
    
    Args:
        content: The content to validate
        if_match: The expected hash (ETag-like)
    
    Returns:
        Tuple of (is_valid, current_hash)
    """
    current_hash = compute_content_hash(content)
    
    # If no precondition is specified, it's always valid
    if if_match is None:
        return True, current_hash
    
    # Check if the current hash matches the expected hash
    return current_hash == if_match, current_hash

def safe_write_operation(content: str, if_match: Optional[str], dry_run: bool = True) -> dict:
    """
    Perform a safe write operation with conflict detection
    
    Args:
        content: The content to write
        if_match: The expected hash for conflict detection
        dry_run: Whether to perform a dry run
    
    Returns:
        Dictionary with operation result
    """
    is_valid, current_hash = validate_precondition(content, if_match)
    
    if not is_valid:
        return {
            "status": "conflict",
            "message": "Content has been modified since last read",
            "current_hash": current_hash,
            "expected_hash": if_match
        }
    
    if dry_run:
        return {
            "status": "dry_run",
            "message": "Dry run completed successfully",
            "hash": current_hash
        }
    
    # In a real implementation, this is where we would actually write the content
    return {
        "status": "success",
        "message": "Content written successfully",
        "hash": current_hash
    }