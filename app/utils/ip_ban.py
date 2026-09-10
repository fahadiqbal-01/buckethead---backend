import time
from typing import Dict, List, Tuple
from fastapi import Request
from starlette.websockets import WebSocket


def get_client_ip(request: Request | WebSocket) -> str:
    """
    Extracts real client IP with support for X-Forwarded-For and X-Real-IP
    from reverse proxies (Vercel, Cloudflare, Nginx).
    """
    if hasattr(request, "headers"):
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
    if hasattr(request, "client") and request.client:
        return request.client.host
    return "127.0.0.1"


class IPBanManager:
    """
    Automated IP banning system:
    1. Request-Velocity Flood Protection: Automatically bans any IP that sends
       more than MAX_REQUESTS_IN_WINDOW within WINDOW_SECONDS.
    2. Repeated Rate-Limit Violation Escalation: Automatically bans any IP
       that triggers 429 Too Many Requests MAX_VIOLATIONS times within VIOLATION_WINDOW.
    """

    def __init__(
        self,
        window_seconds: int = 10,
        max_requests_in_window: int = 25,
        ban_duration_seconds: int = 300,  # 5 minutes
        max_violations: int = 3,
        violation_window_seconds: int = 60,
    ):
        self.window_seconds = window_seconds
        self.max_requests_in_window = max_requests_in_window
        self.ban_duration_seconds = ban_duration_seconds
        self.max_violations = max_violations
        self.violation_window_seconds = violation_window_seconds

        # In-memory stores
        self.banned_ips: Dict[str, float] = {}  # ip -> banned_until (timestamp)
        self.ban_reasons: Dict[str, str] = {}  # ip -> reason string
        self.ip_requests: Dict[str, List[float]] = {}  # ip -> list of request timestamps
        self.ip_violations: Dict[str, List[float]] = {}  # ip -> list of 429 timestamps

    def is_banned(self, ip: str) -> Tuple[bool, int, str]:
        """
        Checks if the IP is currently banned.
        Returns: (is_banned: bool, remaining_seconds: int, reason: str)
        """
        now = time.time()
        if ip in self.banned_ips:
            banned_until = self.banned_ips[ip]
            if now < banned_until:
                remaining = int(banned_until - now)
                reason = self.ban_reasons.get(ip, "Excessive requests")
                return True, remaining, reason
            # Ban has expired -> auto unban
            self.unban_ip(ip)

        return False, 0, ""

    def ban_ip(self, ip: str, reason: str, duration: int = None):
        """Manually or automatically ban an IP for duration seconds."""
        dur = duration or self.ban_duration_seconds
        self.banned_ips[ip] = time.time() + dur
        self.ban_reasons[ip] = reason
        # Clear recent request history to prevent immediate re-trigger on unban
        self.ip_requests.pop(ip, None)
        self.ip_violations.pop(ip, None)

    def unban_ip(self, ip: str) -> bool:
        """Removes an IP from the ban list."""
        existed = ip in self.banned_ips
        self.banned_ips.pop(ip, None)
        self.ban_reasons.pop(ip, None)
        self.ip_requests.pop(ip, None)
        self.ip_violations.pop(ip, None)
        return existed

    def record_request(self, ip: str) -> Tuple[bool, str]:
        """
        Records a request from an IP.
        If requests in window exceed threshold, bans the IP immediately.
        Returns: (was_banned_just_now: bool, reason: str)
        """
        now = time.time()
        timestamps = self.ip_requests.setdefault(ip, [])
        cutoff = now - self.window_seconds
        # Clean older entries
        self.ip_requests[ip] = [t for t in timestamps if t > cutoff]
        self.ip_requests[ip].append(now)

        if len(self.ip_requests[ip]) > self.max_requests_in_window:
            reason = (
                f"Exceeded flood threshold ({len(self.ip_requests[ip])} requests "
                f"in {self.window_seconds}s)"
            )
            self.ban_ip(ip, reason)
            return True, reason

        return False, ""

    def record_rate_limit_violation(self, ip: str) -> Tuple[bool, str]:
        """
        Records a 429 Too Many Requests violation.
        If violations exceed threshold, escalates to a full IP ban.
        Returns: (was_banned_just_now: bool, reason: str)
        """
        now = time.time()
        violations = self.ip_violations.setdefault(ip, [])
        cutoff = now - self.violation_window_seconds
        self.ip_violations[ip] = [t for t in violations if t > cutoff]
        self.ip_violations[ip].append(now)

        if len(self.ip_violations[ip]) >= self.max_violations:
            reason = (
                f"Repeated rate-limit violations ({len(self.ip_violations[ip])} "
                f"violations in {self.violation_window_seconds}s)"
            )
            self.ban_ip(ip, reason)
            return True, reason

        return False, ""

    def get_all_banned_ips(self) -> Dict[str, dict]:
        """Returns all currently active bans."""
        now = time.time()
        active = {}
        for ip, banned_until in list(self.banned_ips.items()):
            if now < banned_until:
                active[ip] = {
                    "remaining_seconds": int(banned_until - now),
                    "reason": self.ban_reasons.get(ip, "Excessive requests"),
                }
            else:
                self.unban_ip(ip)
        return active

    def reset_all(self):
        """Clears all bans and request history."""
        self.banned_ips.clear()
        self.ban_reasons.clear()
        self.ip_requests.clear()
        self.ip_violations.clear()


# Global Singleton instance
ip_ban_manager = IPBanManager()

