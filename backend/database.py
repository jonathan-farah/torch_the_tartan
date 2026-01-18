import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
import os

DB_PATH = 'recognition_cache.db'

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Voice actors cache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voice_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            features_hash TEXT UNIQUE NOT NULL,
            actor_name TEXT NOT NULL,
            notable_projects TEXT NOT NULL,
            confidence REAL NOT NULL,
            features TEXT NOT NULL,
            context TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            access_count INTEGER DEFAULT 1
        )
    ''')
    
    # Face recognition cache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS face_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_hash TEXT UNIQUE NOT NULL,
            person_name TEXT NOT NULL,
            notable_projects TEXT NOT NULL,
            confidence REAL NOT NULL,
            features TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            access_count INTEGER DEFAULT 1
        )
    ''')
    
    # Create indexes for faster lookups
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_voice_hash ON voice_cache(features_hash)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_face_hash ON face_cache(image_hash)')
    
    conn.commit()
    conn.close()

def compute_features_hash(features: Dict[str, Any]) -> str:
    """
    Compute a hash of audio/image features for caching
    Uses key features to create a unique identifier
    """
    # For voice: use key acoustic features
    if 'mean_pitch' in features:
        key_features = {
            'mean_pitch': round(features.get('mean_pitch', 0), 1),
            'pitch_std': round(features.get('pitch_std', 0), 1),
            'spectral_centroid_mean': round(features.get('spectral_centroid_mean', 0), 0),
            'energy': round(features.get('energy', 0), 5)
        }
    else:
        # For face: use all features
        key_features = features
    
    # Create deterministic hash
    features_str = json.dumps(key_features, sort_keys=True)
    return hashlib.sha256(features_str.encode()).hexdigest()

def get_cached_voice_result(features: Dict[str, Any], context: str = '') -> Optional[Dict[str, Any]]:
    """
    Check if voice recognition result exists in cache
    Returns cached result if found, None otherwise
    """
    features_hash = compute_features_hash(features)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT actor_name, notable_projects, confidence, features, access_count
        FROM voice_cache
        WHERE features_hash = ?
    ''', (features_hash,))
    
    row = cursor.fetchone()
    
    if row:
        # Update access statistics
        cursor.execute('''
            UPDATE voice_cache
            SET last_accessed = ?,
                access_count = access_count + 1
            WHERE features_hash = ?
        ''', (datetime.now(), features_hash))
        conn.commit()
        
        result = {
            'actor_name': row['actor_name'],
            'notable_projects': json.loads(row['notable_projects']),
            'confidence': row['confidence'],
            'cached': True,
            'cache_hits': row['access_count'] + 1
        }
        conn.close()
        return result
    
    conn.close()
    return None

def cache_voice_result(features: Dict[str, Any], actor_name: str, notable_projects: list, 
                       confidence: float, context: str = ''):
    """
    Cache voice recognition result for future lookups
    """
    features_hash = compute_features_hash(features)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO voice_cache 
            (features_hash, actor_name, notable_projects, confidence, features, context)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            features_hash,
            actor_name,
            json.dumps(notable_projects),
            confidence,
            json.dumps(features),
            context
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        # Entry already exists, update it
        cursor.execute('''
            UPDATE voice_cache
            SET actor_name = ?,
                notable_projects = ?,
                confidence = ?,
                last_accessed = ?,
                access_count = access_count + 1
            WHERE features_hash = ?
        ''', (actor_name, json.dumps(notable_projects), confidence, datetime.now(), features_hash))
        conn.commit()
    
    conn.close()

def get_cached_face_result(image_features: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Check if face recognition result exists in cache
    Returns cached result if found, None otherwise
    """
    features_hash = compute_features_hash(image_features)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT person_name, notable_projects, confidence, features, access_count
        FROM face_cache
        WHERE image_hash = ?
    ''', (features_hash,))
    
    row = cursor.fetchone()
    
    if row:
        # Update access statistics
        cursor.execute('''
            UPDATE face_cache
            SET last_accessed = ?,
                access_count = access_count + 1
            WHERE image_hash = ?
        ''', (datetime.now(), features_hash))
        conn.commit()
        
        result = {
            'person_name': row['person_name'],
            'notable_projects': json.loads(row['notable_projects']),
            'confidence': row['confidence'],
            'cached': True,
            'cache_hits': row['access_count'] + 1
        }
        conn.close()
        return result
    
    conn.close()
    return None

def cache_face_result(image_features: Dict[str, Any], person_name: str, 
                      notable_projects: list, confidence: float):
    """
    Cache face recognition result for future lookups
    """
    features_hash = compute_features_hash(image_features)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO face_cache 
            (image_hash, person_name, notable_projects, confidence, features)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            features_hash,
            person_name,
            json.dumps(notable_projects),
            confidence,
            json.dumps(image_features)
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        # Entry already exists, update it
        cursor.execute('''
            UPDATE face_cache
            SET person_name = ?,
                notable_projects = ?,
                confidence = ?,
                last_accessed = ?,
                access_count = access_count + 1
            WHERE image_hash = ?
        ''', (person_name, json.dumps(notable_projects), confidence, datetime.now(), features_hash))
        conn.commit()
    
    conn.close()

def get_cache_stats() -> Dict[str, Any]:
    """
    Get statistics about the cache
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count, SUM(access_count) as total_hits FROM voice_cache')
    voice_stats = cursor.fetchone()
    
    cursor.execute('SELECT COUNT(*) as count, SUM(access_count) as total_hits FROM face_cache')
    face_stats = cursor.fetchone()
    
    conn.close()
    
    return {
        'voice_cache': {
            'entries': voice_stats['count'],
            'total_hits': voice_stats['total_hits'] or 0
        },
        'face_cache': {
            'entries': face_stats['count'],
            'total_hits': face_stats['total_hits'] or 0
        }
    }

def clear_cache():
    """
    Clear all cache entries
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM voice_cache')
    cursor.execute('DELETE FROM face_cache')
    
    conn.commit()
    conn.close()

# Initialize database on module import
init_database()
