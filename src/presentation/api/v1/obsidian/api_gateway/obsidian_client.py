import requests
from typing import Optional, Dict, Any
from api_gateway.config import settings
from utils.safe_write import compute_content_hash

class ObsidianAPIClient:
    def __init__(self):
        self.base_url = settings.obsidian_api_base
        self.api_key = settings.obsidian_api_key
        self.headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def list_vaults(self) -> Dict[str, Any]:
        return self._make_request("GET", "/vaults")
    
    def list_files(self, vault_name: str, recursive: bool = False, filter: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if recursive:
            params["recursive"] = recursive
        if filter:
            params["filter"] = filter
        return self._make_request("GET", f"/vault/{vault_name}/files", params=params)
    
    def read_note(self, vault_name: str, path: str) -> Dict[str, Any]:
        result = self._make_request("GET", f"/vault/{vault_name}/file/{path}")
        # Add hash for conflict detection
        if "content" in result:
            result["_hash"] = compute_content_hash(result["content"])
        return result
    
    def upsert_note(self, vault_name: str, path: str, content: str, dry_run: bool = True, 
                   if_match: Optional[str] = None, mode: str = "upsert") -> Dict[str, Any]:
        data = {
            "path": path,
            "content": content,
            "dry_run": dry_run,
            "mode": mode
        }
        if if_match:
            data["if_match"] = if_match
        return self._make_request("PUT", f"/vault/{vault_name}/file/{path}", json=data)
    
    def patch_note(self, vault_name: str, path: str, patch_ops: list) -> Dict[str, Any]:
        data = {"patch_ops": patch_ops}
        return self._make_request("PATCH", f"/vault/{vault_name}/file/{path}", json=data)
    
    def delete_note(self, vault_name: str, path: str) -> Dict[str, Any]:
        return self._make_request("DELETE", f"/vault/{vault_name}/file/{path}")
    
    def get_daily_note(self, vault_name: str, date: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if date:
            params["date"] = date
        result = self._make_request("GET", f"/periodic/daily/{vault_name}", params=params)
        # Add hash for conflict detection
        if "content" in result:
            result["_hash"] = compute_content_hash(result["content"])
        return result
    
    def search_notes(self, query: str) -> Dict[str, Any]:
        data = {"query": query}
        return self._make_request("POST", "/search/simple", json=data)