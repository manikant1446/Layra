"""
Layra Social Media Module
===================================
Social media interaction via browser automation.
Opens platforms, reads notifications, and posts content.
"""

import subprocess
import logging
import urllib.parse

logger = logging.getLogger("layra.social")

PLATFORM_URLS = {
    "instagram": "https://www.instagram.com",
    "twitter": "https://twitter.com",
    "x": "https://twitter.com",
    "linkedin": "https://www.linkedin.com",
    "whatsapp": "https://web.whatsapp.com",
    "facebook": "https://www.facebook.com",
    "reddit": "https://www.reddit.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "telegram": "https://web.telegram.org",
    "discord": "https://discord.com/app",
    "pinterest": "https://www.pinterest.com",
    "snapchat": "https://web.snapchat.com",
}


class SocialMedia:
    """Social media management via browser."""

    def open_social_media(self, platform: str) -> str:
        """Open a social media platform in the browser."""
        platform_lower = platform.lower().strip()
        url = PLATFORM_URLS.get(platform_lower)

        if url:
            subprocess.run(['open', url], check=True)
            logger.info(f"📱 Opened: {platform}")
            return f"Opened {platform.capitalize()}"
        else:
            # Try as a direct URL
            url = f"https://www.{platform_lower}.com"
            subprocess.run(['open', url])
            return f"Opened {platform}"

    def open_profile(self, platform: str, username: str) -> str:
        """Open a specific profile on a platform."""
        urls = {
            "instagram": f"https://www.instagram.com/{username}",
            "twitter": f"https://twitter.com/{username}",
            "x": f"https://twitter.com/{username}",
            "linkedin": f"https://www.linkedin.com/in/{username}",
            "github": f"https://github.com/{username}",
            "youtube": f"https://www.youtube.com/@{username}",
            "reddit": f"https://www.reddit.com/user/{username}",
            "facebook": f"https://www.facebook.com/{username}",
        }

        platform_lower = platform.lower()
        url = urls.get(platform_lower, f"https://www.{platform_lower}.com/{username}")

        subprocess.run(['open', url])
        return f"Opened {username}'s {platform} profile"

    def search_on_platform(self, platform: str, query: str) -> str:
        """Search for content on a social media platform."""
        encoded = urllib.parse.quote(query)
        search_urls = {
            "twitter": f"https://twitter.com/search?q={encoded}",
            "x": f"https://twitter.com/search?q={encoded}",
            "youtube": f"https://www.youtube.com/results?search_query={encoded}",
            "reddit": f"https://www.reddit.com/search/?q={encoded}",
            "linkedin": f"https://www.linkedin.com/search/results/all/?keywords={encoded}",
            "github": f"https://github.com/search?q={encoded}",
            "instagram": f"https://www.instagram.com/explore/tags/{encoded.replace('+', '')}",
        }

        platform_lower = platform.lower()
        url = search_urls.get(platform_lower)

        if url:
            subprocess.run(['open', url])
            return f"Searching '{query}' on {platform}"
        else:
            return f"Search not supported for {platform}"

    def open_messages(self, platform: str) -> str:
        """Open the messages/DMs section of a platform."""
        message_urls = {
            "instagram": "https://www.instagram.com/direct/inbox/",
            "twitter": "https://twitter.com/messages",
            "x": "https://twitter.com/messages",
            "linkedin": "https://www.linkedin.com/messaging/",
            "facebook": "https://www.facebook.com/messages/",
        }

        platform_lower = platform.lower()
        url = message_urls.get(platform_lower)

        if url:
            subprocess.run(['open', url])
            return f"Opened {platform} messages"
        else:
            return f"Direct messages URL not available for {platform}"

    def open_notifications(self, platform: str) -> str:
        """Open notifications on a platform."""
        notif_urls = {
            "instagram": "https://www.instagram.com/accounts/activity/",
            "twitter": "https://twitter.com/notifications",
            "x": "https://twitter.com/notifications",
            "linkedin": "https://www.linkedin.com/notifications/",
            "github": "https://github.com/notifications",
            "facebook": "https://www.facebook.com/notifications",
        }

        platform_lower = platform.lower()
        url = notif_urls.get(platform_lower)

        if url:
            subprocess.run(['open', url])
            return f"Opened {platform} notifications"
        else:
            return f"Notifications URL not available for {platform}"
