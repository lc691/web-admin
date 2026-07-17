"""
Policy Loader untuk menentukan path publik vs private
"""

from typing import Tuple, FrozenSet

from app.core.config import settings
from app.utils.logger import log


class SecurityPolicy:
    """
    Security Policy untuk menentukan akses path.
    """
    
    def __init__(
        self,
        public_paths: FrozenSet[str] = frozenset(),
        public_prefixes: FrozenSet[str] = frozenset(),
        public_exact: FrozenSet[str] = frozenset(),
    ):
        """
        Initialize security policy.
        
        Args:
            public_paths: Set path yang public (exact match)
            public_prefixes: Set prefix path yang public
            public_exact: Set path exact yang public (alternatif)
        """
        self.public_paths = public_paths
        self.public_prefixes = public_prefixes
        self.public_exact = public_exact
        
        log.debug(f"📋 Public paths: {len(self.public_paths)} items")
        log.debug(f"📋 Public prefixes: {len(self.public_prefixes)} items")
    
    def is_public(self, path: str) -> bool:
        """
        Cek apakah sebuah path adalah public (tidak perlu auth).
        
        Args:
            path: URL path yang akan dicek
            
        Returns:
            bool: True jika path public
        """
        # 1. Check exact match
        if path in self.public_paths:
            return True
        
        # 2. Check exact match dari PUBLIC_EXACT
        if path in self.public_exact:
            return True
        
        # 3. Check prefix
        for prefix in self.public_prefixes:
            if path.startswith(prefix):
                return True
        
        return False
    
    def add_public_path(self, path: str):
        """Tambahkan path public baru (runtime)"""
        paths = set(self.public_paths)
        if path not in paths:
            paths.add(path)
            self.public_paths = frozenset(paths)
            log.info(f"✅ Added public path: {path}")
    
    def add_public_prefix(self, prefix: str):
        """Tambahkan prefix public baru (runtime)"""
        prefixes = set(self.public_prefixes)
        if prefix not in prefixes:
            prefixes.add(prefix)
            self.public_prefixes = frozenset(prefixes)
            log.info(f"✅ Added public prefix: {prefix}")
    
    def remove_public_path(self, path: str):
        """Hapus path public (runtime)"""
        paths = set(self.public_paths)
        if path in paths:
            paths.remove(path)
            self.public_paths = frozenset(paths)
            log.info(f"✅ Removed public path: {path}")


def load_policy() -> SecurityPolicy:
    """
    Load access policy dari config.
    
    Returns:
        SecurityPolicy: Instance security policy
    """
    try:
        # Ambil dari settings
        public_paths = settings.get_public_paths()
        public_prefixes = settings.get_public_prefixes()
        public_exact = settings.get_public_exact()
        
        # Buat policy
        policy = SecurityPolicy(
            public_paths=frozenset(public_paths),
            public_prefixes=frozenset(public_prefixes),
            public_exact=frozenset(public_exact),
        )
        
        log.info("✅ Security policy loaded successfully")
        log.debug(f"   Public paths: {len(public_paths)} items")
        log.debug(f"   Public prefixes: {len(public_prefixes)} items")
        
        return policy
        
    except Exception as e:
        log.error(f"❌ Failed to load security policy: {e}")
        raise


# ================================
# POLICY CACHE (Untuk performance)
# ================================
_policy_cache = None


def get_policy() -> SecurityPolicy:
    """
    Get cached policy instance.
    
    Returns:
        SecurityPolicy: Cached policy instance
    """
    global _policy_cache
    if _policy_cache is None:
        _policy_cache = load_policy()
    return _policy_cache


def reload_policy():
    """Reload policy (untuk development)"""
    global _policy_cache
    _policy_cache = load_policy()
    log.info("🔄 Security policy reloaded")