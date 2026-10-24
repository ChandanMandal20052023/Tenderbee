"""
Portal Session & Cookie Pooler for Government E-Procurement Portals.
Maintains active authenticated sessions, cookies, and ViewState to eliminate
redundant CAPTCHA solves across consecutive tender requests.
"""
import logging
import threading
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class PortalSession:
    def __init__(
        self,
        domain: str,
        cookies: Dict[str, str],
        headers: Optional[Dict[str, str]] = None,
        view_state: Optional[str] = None,
        ttl_seconds: int = 1200,  # 20 minutes default
    ):
        self.domain = domain
        self.cookies = cookies
        self.headers = headers or {}
        self.view_state = view_state
        self.created_at = time.time()
        self.expires_at = self.created_at + ttl_seconds

    @property
    def is_expired(self) -> bool:
        return time.time() >= self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "cookies": self.cookies,
            "headers": self.headers,
            "view_state": self.view_state,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "is_expired": self.is_expired,
        }


class PortalSessionPool:
    """
    Thread-safe in-memory session pool with automatic expiration.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._sessions: Dict[str, PortalSession] = {}
                cls._instance._session_lock = threading.Lock()
        return cls._instance

    def get_session(self, domain: str) -> Optional[PortalSession]:
        """
        Get an active, unexpired session for the specified domain.
        Returns None if expired or not found.
        """
        with self._session_lock:
            session = self._sessions.get(domain)
            if session:
                if not session.is_expired:
                    logger.debug("Active session pool hit for %s (remaining: %.1fs)", domain, session.expires_at - time.time())
                    return session
                else:
                    logger.info("Session for %s expired. Removing from pool.", domain)
                    del self._sessions[domain]
            return None

    def save_session(
        self,
        domain: str,
        cookies: Dict[str, str],
        headers: Optional[Dict[str, str]] = None,
        view_state: Optional[str] = None,
        ttl_seconds: int = 1200,
    ) -> PortalSession:
        """
        Save or refresh an authenticated session in the pool.
        """
        with self._session_lock:
            session = PortalSession(
                domain=domain,
                cookies=cookies,
                headers=headers,
                view_state=view_state,
                ttl_seconds=ttl_seconds,
            )
            self._sessions[domain] = session
            logger.info("Saved new active session for %s (TTL: %ds)", domain, ttl_seconds)
            return session

    def invalidate(self, domain: str) -> None:
        """
        Explicitly invalidate a session (e.g. after receiving a session expired error from portal).
        """
        with self._session_lock:
            if domain in self._sessions:
                del self._sessions[domain]
                logger.info("Invalidated session for %s", domain)

    def clear(self) -> None:
        """
        Clear all sessions.
        """
        with self._session_lock:
            self._sessions.clear()
