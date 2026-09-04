"""
Shared configuration for all sync engines.
Centralized settings for anime/manga syncing.
"""

import os
from typing import Dict, Any

class Config:
    """Base configuration class"""
    
    # ================== AniList Settings ==================
    ANILIST_TOKEN = os.environ.get('ANILIST_TARGET_TOKEN', '')
    ANILIST_ENDPOINT = 'https://graphql.anilist.co'
    ANILIST_PAGE_SIZE = 75  # Optimized from 50
    
    # ================== Discord Settings ==================
    DISCORD_TIMEOUT = 15
    DISCORD_EMBED_LIMIT = 25
    RATE_LIMIT_DELAY = 2
    THREAD_CREATION_DELAY = 2
    
    # ================== Telegram Settings ==================
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')
    TELEGRAM_TIMEOUT = 10
    
    # ================== Zulip Settings ==================
    ZULIP_SERVER_URL = os.environ.get('ZULIP_SERVER_URL', '')
    ZULIP_BOT_EMAIL = os.environ.get('ZULIP_BOT_EMAIL', '')
    ZULIP_API_KEY = os.environ.get('ZULIP_API_KEY', '')
    ZULIP_TIMEOUT = 10
    
    # ================== Performance & Cache ==================
    CACHE_TTL_SECONDS = 3600  # 1 hour
    REQUEST_TIMEOUT = 15
    MAX_RETRIES = 3
    RETRY_BACKOFF_BASE = 2
    
    # ================== Anime Configuration ==================
    ANIME_CONFIG = {
        'media_type': 'ANIME',
        'db_prefix': 'db_anime',
        'scoring': {
            'per_episode': 10,
            'completion_bonus': 100
        },
        'duration_default': 24,
        'airing_enabled': True,
        'zulip_stream': 'Anime-Vault'
    }
    
    # ================== Manga Configuration ==================
    MANGA_CONFIG = {
        'media_type': 'MANGA',
        'db_prefix': 'db_manga',
        'scoring': {
            'per_chapter': 2,
            'completion_bonus': 50
        },
        'duration_default': 5,
        'airing_enabled': False,
        'zulip_stream': 'Manga-Vault'
    }
    
    # ================== Target Lists & Categorization ==================
    TARGET_LISTS = [
        'anime movies', 'iseki', 'isekai', 'milf', 'loli', 'rom com',
        'plan to continue', 'hentai', 'favourite', 'fav', 'planning'
    ]
    
    DESCRIPTOR_CATEGORIES = {
        'movie': ['MOVIE'],
        'isekai': ['isekai'],
        'hentai': ['hentai', 'ecchi', 'adult', 'smut'],
        'milf': ['milf', 'older woman', 'mother'],
        'loli': ['loli']
    }
    
    # ================== VIP Franchises ==================
    PRIORITY_FAVORITES = [
        'One Piece',
        'Detective Conan',
        'Kono Suba',
        'Dragon Ball Z'
    ]
    
    # ================== Achievement Milestones ==================
    ACHIEVEMENT_TIERS = [1000, 5000, 10000]
    
    ACHIEVEMENT_GIFS = {
        1000: 'https://i.imgur.com/QzXoX1j.gif',
        5000: 'https://i.imgur.com/W2dM9Ue.gif'
    }
    
    # ================== Source Settings ==================
    SOURCE_USERNAME = 'Orewatokyo'
    MAL_ANIME_XML = 'mal_anime.xml'
    MAL_EXPORT_XML = 'mal_export.xml'
    
    # ================== Folder Structure ==================
    PERFORMANCE_DIRS = ['daily', 'weekly', 'monthly', 'yearly']
    
    @staticmethod
    def get_db_files(media_type: str) -> Dict[str, str]:
        """Get all database file names for a media type"""
        prefix = Config.ANIME_CONFIG['db_prefix'] if media_type == 'ANIME' else Config.MANGA_CONFIG['db_prefix']
        return {
            'sync': f'{prefix}_sync.json',
            'inventory': f'{prefix}_inventory.json',
            'timestamp': f'{prefix}_timestamp.json',
            'threads': f'{prefix}_threads.json',
            'messages': f'{prefix}_messages.json',
            'ghosts': f'{prefix}_ghosts.json',
            'void': f'{prefix}_void.json',
            'airing': f'{prefix}_airing.json',
            'achievements': f'{prefix}_achievements.json',
            'performance_msg': f'{prefix}_performance_msg.json'
        }
    
    @staticmethod
    def get_webhooks(media_type: str) -> Dict[str, str]:
        """Get Discord webhooks for a media type"""
        if media_type == 'ANIME':
            return {
                'main': os.environ.get('DISCORD_ANILIST_ANIME_WEBHOOK', ''),
                'airing': os.environ.get('DISCORD_AIRING_WEBHOOK', ''),
            }
        else:
            return {
                'main': os.environ.get('DISCORD_ANILIST_MANGA_WEBHOOK', ''),
            }
    
    @staticmethod
    def get_shared_webhooks() -> Dict[str, str]:
        """Get shared Discord webhooks used by both engines"""
        return {
            'log': os.environ.get('DISCORD_ANILIST_LOG_WEBHOOK', ''),
            'favorites': os.environ.get('DISCORD_FAVORITES_WEBHOOK', ''),
            'ghost': os.environ.get('DISCORD_GHOST_RADAR_WEBHOOK', ''),
            'achievements': os.environ.get('DISCORD_ACHIEVEMENTS_WEBHOOK', ''),
            'performance': os.environ.get('DISCORD_PERFORMANCE_WEBHOOK', '')
        }
