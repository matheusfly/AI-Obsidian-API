# Mobile API Endpoints & Cross-Platform Integration

## 📱 Mobile-First API Design

### Mobile Authentication System

```python
# mobile/auth_system.py
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
import asyncio
from typing import Dict, Any, Optional

class MobileAuthManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.refresh_tokens = {}
        self.device_registry = {}
    
    async def authenticate_device(self, device_info: Dict[str, Any]) -> Dict[str, str]:
        """Authenticate mobile device and generate tokens"""
        
        device_id = device_info.get('device_id')
        device_type = device_info.get('device_type')  # 'ios', 'android', 'web'
        app_version = device_info.get('app_version')
        
        # Register device
        self.device_registry[device_id] = {
            'device_type': device_type,
            'app_version': app_version,
            'last_seen': datetime.utcnow(),
            'push_token': device_info.get('push_token')
        }
        
        # Generate access token (short-lived)
        access_token = self._generate_access_token(device_id, expires_minutes=60)
        
        # Generate refresh token (long-lived)
        refresh_token = self._generate_refresh_token(device_id, expires_days=30)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'expires_in': 3600
        }
    
    def _generate_access_token(self, device_id: str, expires_minutes: int = 60) -> str:
        """Generate short-lived access token"""
        payload = {
            'device_id': device_id,
            'type': 'access',
            'exp': datetime.utcnow() + timedelta(minutes=expires_minutes),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def _generate_refresh_token(self, device_id: str, expires_days: int = 30) -> str:
        """Generate long-lived refresh token"""
        payload = {
            'device_id': device_id,
            'type': 'refresh',
            'exp': datetime.utcnow() + timedelta(days=expires_days),
            'iat': datetime.utcnow()
        }
        
        refresh_token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        self.refresh_tokens[device_id] = refresh_token
        return refresh_token
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=['HS256'])
            device_id = payload['device_id']
            
            if payload['type'] != 'refresh':
                raise HTTPException(status_code=401, detail="Invalid token type")
            
            if self.refresh_tokens.get(device_id) != refresh_token:
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            
            # Generate new access token
            new_access_token = self._generate_access_token(device_id)
            
            return {
                'access_token': new_access_token,
                'token_type': 'bearer',
                'expires_in': 3600
            }
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
```

### Mobile-Optimized API Endpoints

```python
# mobile/api_endpoints.py
from fastapi import APIRouter, Depends, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio

mobile_router = APIRouter(prefix="/mobile/v1", tags=["mobile"])

class MobileNoteRequest(BaseModel):
    path: str = Field(..., description="Note path")
    content: str = Field(..., description="Note content")
    tags: Optional[List[str]] = Field(default=[], description="Note tags")
    offline_id: Optional[str] = Field(None, description="Offline sync ID")
    last_modified: Optional[str] = Field(None, description="Last modified timestamp")

class MobileSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(default=20, le=50, description="Results limit")
    offset: int = Field(default=0, description="Results offset")
    filters: Optional[Dict[str, Any]] = Field(default={}, description="Search filters")
    include_content: bool = Field(default=False, description="Include full content")

class MobileSyncRequest(BaseModel):
    last_sync: Optional[str] = Field(None, description="Last sync timestamp")
    device_id: str = Field(..., description="Device identifier")
    changes: List[Dict[str, Any]] = Field(default=[], description="Local changes")

@mobile_router.post("/notes/create")
async def create_note_mobile(
    note: MobileNoteRequest,
    device_info: Dict = Depends(get_device_info)
):
    """Create note optimized for mobile"""
    
    # Handle offline sync
    if note.offline_id:
        existing_note = await check_offline_sync(note.offline_id, device_info['device_id'])
        if existing_note:
            return await update_note_mobile(note, device_info)
    
    # Create note with mobile optimizations
    result = await vault_service.create_note(
        path=note.path,
        content=note.content,
        tags=note.tags,
        metadata={
            'created_on_mobile': True,
            'device_id': device_info['device_id'],
            'app_version': device_info.get('app_version')
        }
    )
    
    # Trigger background processing
    asyncio.create_task(process_mobile_note(result['path'], device_info))
    
    return {
        'success': True,
        'note_id': result['id'],
        'path': result['path'],
        'sync_timestamp': datetime.utcnow().isoformat()
    }

@mobile_router.get("/notes/list")
async def list_notes_mobile(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0),
    folder: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    modified_since: Optional[str] = Query(None),
    device_info: Dict = Depends(get_device_info)
):
    """List notes with mobile pagination and filtering"""
    
    # Parse tags
    tag_list = tags.split(',') if tags else None
    
    # Build query
    query_params = {
        'limit': limit,
        'offset': offset,
        'folder': folder,
        'tags': tag_list,
        'modified_since': modified_since
    }
    
    # Get notes with mobile-optimized fields
    notes = await vault_service.list_notes_mobile(query_params)
    
    # Add mobile-specific metadata
    for note in notes:
        note['mobile_optimized'] = True
        note['preview'] = note['content'][:200] + '...' if len(note['content']) > 200 else note['content']
        note['word_count'] = len(note['content'].split())
        note['read_time'] = max(1, note['word_count'] // 200)  # Estimated read time in minutes
    
    return {
        'notes': notes,
        'total': len(notes),
        'has_more': len(notes) == limit,
        'next_offset': offset + limit if len(notes) == limit else None
    }

@mobile_router.post("/search")
async def search_mobile(
    search_request: MobileSearchRequest,
    device_info: Dict = Depends(get_device_info)
):
    """Mobile-optimized search with caching"""
    
    # Check cache first
    cache_key = f"mobile_search:{hash(search_request.query)}:{search_request.limit}:{search_request.offset}"
    cached_result = await redis_client.get(cache_key)
    
    if cached_result:
        return json.loads(cached_result)
    
    # Perform search
    search_results = await vault_service.search_notes(
        query=search_request.query,
        limit=search_request.limit,
        offset=search_request.offset,
        filters=search_request.filters,
        semantic=True
    )
    
    # Optimize results for mobile
    mobile_results = []
    for result in search_results:
        mobile_result = {
            'id': result['id'],
            'path': result['path'],
            'title': result['title'],
            'preview': result['content'][:150] + '...' if len(result['content']) > 150 else result['content'],
            'score': result['score'],
            'tags': result.get('tags', []),
            'modified': result['modified']
        }
        
        if search_request.include_content:
            mobile_result['content'] = result['content']
        
        mobile_results.append(mobile_result)
    
    response = {
        'results': mobile_results,
        'total': len(mobile_results),
        'query': search_request.query,
        'search_time': time.time() - start_time
    }
    
    # Cache results for 5 minutes
    await redis_client.setex(cache_key, 300, json.dumps(response))
    
    return response

@mobile_router.post("/sync")
async def sync_mobile(
    sync_request: MobileSyncRequest,
    device_info: Dict = Depends(get_device_info)
):
    """Intelligent mobile sync with conflict resolution"""
    
    sync_result = {
        'sync_timestamp': datetime.utcnow().isoformat(),
        'changes_applied': [],
        'conflicts': [],
        'server_changes': [],
        'sync_status': 'success'
    }
    
    # Get server changes since last sync
    if sync_request.last_sync:
        server_changes = await vault_service.get_changes_since(
            timestamp=sync_request.last_sync,
            device_id=sync_request.device_id
        )
        sync_result['server_changes'] = server_changes
    
    # Process local changes
    for change in sync_request.changes:
        try:
            result = await process_mobile_change(change, device_info)
            sync_result['changes_applied'].append(result)
        except ConflictError as e:
            sync_result['conflicts'].append({
                'change': change,
                'conflict_type': e.conflict_type,
                'resolution_options': e.resolution_options
            })
    
    # Update device sync status
    await update_device_sync_status(
        device_id=sync_request.device_id,
        sync_timestamp=sync_result['sync_timestamp']
    )
    
    return sync_result
```

### Offline Support System

```python
# mobile/offline_support.py
import sqlite3
import json
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

class OfflineManager:
    def __init__(self, db_path: str = "mobile_offline.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize offline database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Offline changes queue
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS offline_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                change_type TEXT NOT NULL,
                note_path TEXT NOT NULL,
                content TEXT,
                metadata TEXT,
                timestamp TEXT NOT NULL,
                sync_status TEXT DEFAULT 'pending',
                conflict_resolution TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Cached notes for offline access
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cached_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                note_path TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
                cache_priority INTEGER DEFAULT 1,
                UNIQUE(device_id, note_path)
            )
        ''')
        
        # Sync status tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_status (
                device_id TEXT PRIMARY KEY,
                last_sync_timestamp TEXT,
                pending_changes INTEGER DEFAULT 0,
                last_successful_sync TEXT,
                sync_errors TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def queue_offline_change(self, device_id: str, change: Dict[str, Any]) -> str:
        """Queue change for later sync"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        change_id = f"offline_{device_id}_{int(datetime.utcnow().timestamp())}"
        
        cursor.execute('''
            INSERT INTO offline_changes 
            (device_id, change_type, note_path, content, metadata, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            device_id,
            change['type'],
            change['path'],
            change.get('content'),
            json.dumps(change.get('metadata', {})),
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return change_id
    
    async def get_pending_changes(self, device_id: str) -> List[Dict[str, Any]]:
        """Get all pending changes for device"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, change_type, note_path, content, metadata, timestamp
            FROM offline_changes
            WHERE device_id = ? AND sync_status = 'pending'
            ORDER BY timestamp ASC
        ''', (device_id,))
        
        changes = []
        for row in cursor.fetchall():
            changes.append({
                'id': row[0],
                'type': row[1],
                'path': row[2],
                'content': row[3],
                'metadata': json.loads(row[4]) if row[4] else {},
                'timestamp': row[5]
            })
        
        conn.close()
        return changes
    
    async def cache_note_for_offline(self, device_id: str, note_path: str, content: str, metadata: Dict = None):
        """Cache note for offline access"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO cached_notes
            (device_id, note_path, content, metadata, last_accessed)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            device_id,
            note_path,
            content,
            json.dumps(metadata or {}),
            datetime.utcnow()
        ))
        
        conn.commit()
        conn.close()
    
    async def get_cached_notes(self, device_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get cached notes for offline access"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT note_path, content, metadata, last_accessed
            FROM cached_notes
            WHERE device_id = ?
            ORDER BY cache_priority DESC, last_accessed DESC
            LIMIT ?
        ''', (device_id, limit))
        
        notes = []
        for row in cursor.fetchall():
            notes.append({
                'path': row[0],
                'content': row[1],
                'metadata': json.loads(row[2]) if row[2] else {},
                'last_accessed': row[3]
            })
        
        conn.close()
        return notes

class ConflictResolver:
    def __init__(self):
        self.resolution_strategies = {
            'server_wins': self._server_wins,
            'client_wins': self._client_wins,
            'merge_content': self._merge_content,
            'create_duplicate': self._create_duplicate,
            'ai_assisted': self._ai_assisted_resolution
        }
    
    async def resolve_conflict(self, local_change: Dict, server_version: Dict, strategy: str = 'ai_assisted') -> Dict[str, Any]:
        """Resolve sync conflict using specified strategy"""
        
        if strategy not in self.resolution_strategies:
            strategy = 'ai_assisted'
        
        resolver = self.resolution_strategies[strategy]
        resolution = await resolver(local_change, server_version)
        
        return {
            'strategy_used': strategy,
            'resolution': resolution,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _ai_assisted_resolution(self, local_change: Dict, server_version: Dict) -> Dict[str, Any]:
        """Use AI to intelligently merge conflicting changes"""
        
        prompt = f"""
        Resolve this conflict between local and server versions of a note:
        
        Local Version (modified on mobile):
        {local_change.get('content', '')}
        
        Server Version:
        {server_version.get('content', '')}
        
        Provide the best merged version that preserves important changes from both.
        """
        
        # Call AI service for resolution
        ai_response = await ai_service.resolve_conflict(prompt)
        
        return {
            'merged_content': ai_response.get('merged_content'),
            'explanation': ai_response.get('explanation'),
            'confidence': ai_response.get('confidence', 0.8)
        }
    
    async def _merge_content(self, local_change: Dict, server_version: Dict) -> Dict[str, Any]:
        """Attempt automatic content merge"""
        
        local_content = local_change.get('content', '')
        server_content = server_version.get('content', '')
        
        # Simple line-based merge
        local_lines = local_content.split('\n')
        server_lines = server_content.split('\n')
        
        # Use difflib for basic merge
        import difflib
        
        merged_lines = []
        matcher = difflib.SequenceMatcher(None, server_lines, local_lines)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                merged_lines.extend(server_lines[i1:i2])
            elif tag == 'replace':
                merged_lines.append(f"<<<<<<< LOCAL")
                merged_lines.extend(local_lines[j1:j2])
                merged_lines.append("=======")
                merged_lines.extend(server_lines[i1:i2])
                merged_lines.append(">>>>>>> SERVER")
            elif tag == 'delete':
                merged_lines.extend(server_lines[i1:i2])
            elif tag == 'insert':
                merged_lines.extend(local_lines[j1:j2])
        
        return {
            'merged_content': '\n'.join(merged_lines),
            'has_conflicts': '<<<<<<< LOCAL' in '\n'.join(merged_lines)
        }
```

### Push Notifications System

```python
# mobile/push_notifications.py
from pyfcm import FCMNotification
from apns2.client import APNsClient
from apns2.payload import Payload
import asyncio
from typing import Dict, List, Any

class PushNotificationManager:
    def __init__(self):
        self.fcm = FCMNotification(api_key=os.getenv('FCM_SERVER_KEY'))
        self.apns_client = APNsClient(
            credentials=os.getenv('APNS_KEY_PATH'),
            use_sandbox=os.getenv('APNS_USE_SANDBOX', 'false').lower() == 'true'
        )
        self.notification_templates = self._load_templates()
    
    async def send_vault_update_notification(self, device_tokens: List[str], update_info: Dict[str, Any]):
        """Send notification about vault updates"""
        
        notification_data = {
            'title': 'Vault Updated',
            'body': f"New changes in {update_info.get('note_path', 'your vault')}",
            'data': {
                'type': 'vault_update',
                'note_path': update_info.get('note_path'),
                'change_type': update_info.get('change_type'),
                'timestamp': update_info.get('timestamp')
            }
        }
        
        # Send to Android devices (FCM)
        android_tokens = [token for token in device_tokens if token.startswith('fcm:')]
        if android_tokens:
            await self._send_fcm_notification(android_tokens, notification_data)
        
        # Send to iOS devices (APNs)
        ios_tokens = [token for token in device_tokens if token.startswith('apns:')]
        if ios_tokens:
            await self._send_apns_notification(ios_tokens, notification_data)
    
    async def send_ai_analysis_complete(self, device_tokens: List[str], analysis_result: Dict[str, Any]):
        """Notify when AI analysis is complete"""
        
        notification_data = {
            'title': 'AI Analysis Complete',
            'body': f"Your note has been analyzed and enhanced",
            'data': {
                'type': 'ai_analysis_complete',
                'note_path': analysis_result.get('note_path'),
                'tags_added': analysis_result.get('tags_added', []),
                'links_suggested': analysis_result.get('links_suggested', [])
            }
        }
        
        await self._send_to_all_devices(device_tokens, notification_data)
    
    async def send_sync_conflict_notification(self, device_tokens: List[str], conflict_info: Dict[str, Any]):
        """Notify about sync conflicts that need resolution"""
        
        notification_data = {
            'title': 'Sync Conflict',
            'body': f"Conflict detected in {conflict_info.get('note_path')}",
            'data': {
                'type': 'sync_conflict',
                'note_path': conflict_info.get('note_path'),
                'conflict_id': conflict_info.get('conflict_id'),
                'requires_user_action': True
            }
        }
        
        await self._send_to_all_devices(device_tokens, notification_data)
    
    async def _send_fcm_notification(self, tokens: List[str], notification_data: Dict[str, Any]):
        """Send FCM notification to Android devices"""
        
        # Remove 'fcm:' prefix from tokens
        clean_tokens = [token.replace('fcm:', '') for token in tokens]
        
        result = self.fcm.notify_multiple_devices(
            registration_ids=clean_tokens,
            message_title=notification_data['title'],
            message_body=notification_data['body'],
            data_message=notification_data['data']
        )
        
        return result
    
    async def _send_apns_notification(self, tokens: List[str], notification_data: Dict[str, Any]):
        """Send APNs notification to iOS devices"""
        
        # Remove 'apns:' prefix from tokens
        clean_tokens = [token.replace('apns:', '') for token in tokens]
        
        payload = Payload(
            alert=notification_data['body'],
            badge=1,
            sound='default',
            custom=notification_data['data']
        )
        
        for token in clean_tokens:
            try:
                self.apns_client.send_notification(token, payload, 'com.yourapp.obsidianvault')
            except Exception as e:
                print(f"Failed to send APNs notification to {token}: {e}")
    
    async def _send_to_all_devices(self, device_tokens: List[str], notification_data: Dict[str, Any]):
        """Send notification to all device types"""
        
        tasks = []
        
        # Group tokens by platform
        android_tokens = [token for token in device_tokens if token.startswith('fcm:')]
        ios_tokens = [token for token in device_tokens if token.startswith('apns:')]
        
        if android_tokens:
            tasks.append(self._send_fcm_notification(android_tokens, notification_data))
        
        if ios_tokens:
            tasks.append(self._send_apns_notification(ios_tokens, notification_data))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

class MobileAnalytics:
    def __init__(self):
        self.analytics_db = {}
        self.usage_patterns = {}
    
    async def track_mobile_usage(self, device_id: str, action: str, metadata: Dict[str, Any]):
        """Track mobile app usage patterns"""
        
        usage_event = {
            'device_id': device_id,
            'action': action,
            'metadata': metadata,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store in analytics database
        await self._store_analytics_event(usage_event)
        
        # Update usage patterns
        await self._update_usage_patterns(device_id, action, metadata)
    
    async def get_mobile_insights(self, device_id: str) -> Dict[str, Any]:
        """Get mobile usage insights for optimization"""
        
        insights = {
            'most_accessed_notes': await self._get_most_accessed_notes(device_id),
            'usage_patterns': await self._get_usage_patterns(device_id),
            'optimal_sync_times': await self._calculate_optimal_sync_times(device_id),
            'cache_recommendations': await self._get_cache_recommendations(device_id),
            'performance_metrics': await self._get_performance_metrics(device_id)
        }
        
        return insights
    
    async def _calculate_optimal_sync_times(self, device_id: str) -> List[str]:
        """Calculate optimal times for background sync"""
        
        # Analyze usage patterns to find low-activity periods
        usage_data = await self._get_device_usage_data(device_id)
        
        # Find time slots with minimal activity
        optimal_times = []
        for hour in range(24):
            activity_count = sum(1 for event in usage_data 
                               if datetime.fromisoformat(event['timestamp']).hour == hour)
            
            if activity_count < 5:  # Low activity threshold
                optimal_times.append(f"{hour:02d}:00")
        
        return optimal_times[:3]  # Return top 3 optimal times
```

This mobile API expansion provides:

1. **Mobile Authentication** - Device-specific JWT tokens with refresh mechanism
2. **Mobile-Optimized Endpoints** - Pagination, caching, and mobile-specific responses
3. **Offline Support** - Local SQLite database for offline changes and caching
4. **Conflict Resolution** - AI-assisted and automatic merge strategies
5. **Push Notifications** - FCM and APNs integration for real-time updates
6. **Mobile Analytics** - Usage tracking and optimization insights
7. **Intelligent Sync** - Background sync with conflict detection
8. **Performance Optimization** - Caching and prefetching for mobile devices

The system ensures seamless mobile experience with robust offline capabilities and intelligent synchronization.