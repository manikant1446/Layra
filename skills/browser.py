"""
Layra Browser Module
===============================
Browser automation and web interaction.
Opens URLs, searches, and performs browser tasks.
"""

import subprocess
import logging
import urllib.parse

logger = logging.getLogger("layra.browser")


# Social media URLs mapping
SOCIAL_MEDIA_URLS = {
    "instagram": "https://www.instagram.com",
    "twitter": "https://twitter.com",
    "x": "https://twitter.com",
    "linkedin": "https://www.linkedin.com",
    "whatsapp": "https://web.whatsapp.com",
    "facebook": "https://www.facebook.com",
    "reddit": "https://www.reddit.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
}


class Browser:
    """Browser automation using macOS open command and AppleScript."""

    def __init__(self, default_browser: str = "Google Chrome"):
        self.default_browser = default_browser or "Google Chrome"

    def open_url(self, url: str) -> str:
        """Open a URL in Google Chrome browser."""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        try:
            subprocess.run(['open', '-a', self.default_browser, url], check=True)
            logger.info(f"🌐 Opened in {self.default_browser}: {url}")
            return f"Opened {url} in {self.default_browser}"
        except Exception as e:
            try:
                # Fallback to default open command
                subprocess.run(['open', url], check=True)
                return f"Opened {url}"
            except Exception as ex:
                logger.error(f"Failed to open URL: {ex}")
                return f"Failed to open URL: {ex}"


    def search_web(self, query: str) -> str:
        """Search the web and return results summary."""
        # Open search in browser
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        self.open_url(search_url)

        # Also try to get text results using duckduckgo-search
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
                if results:
                    summary_parts = []
                    for i, r in enumerate(results, 1):
                        title = r.get('title', 'No title')
                        body = r.get('body', '')[:150]
                        summary_parts.append(f"{i}. {title}: {body}")
                    return "Search results:\n" + "\n".join(summary_parts)
        except ImportError:
            logger.warning("duckduckgo-search not installed, showing browser only")
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")

        return f"Opened Google search for: {query}"

    def search_youtube(self, query: str, play_first: bool = True) -> str:
        """Search YouTube and play the top result directly, or open search page."""
        import urllib.request
        import re

        encoded_query = urllib.parse.quote(query)

        if play_first:
            try:
                search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
                req = urllib.request.Request(
                    search_url,
                    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                )
                html = urllib.request.urlopen(req, timeout=4).read().decode('utf-8', errors='ignore')
                video_ids = re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', html)
                if video_ids:
                    first_video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
                    self.open_url(first_video_url)
                    return f"Playing YouTube video: {query}"
            except Exception as e:
                logger.warning(f"Failed to extract direct YouTube video ID: {e}")

        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        self.open_url(url)
        return f"Opened YouTube search for: {query}"


    def open_social_media(self, platform: str) -> str:
        """Open a social media platform."""
        platform_lower = platform.lower().strip()
        url = SOCIAL_MEDIA_URLS.get(platform_lower)

        if url:
            self.open_url(url)
            return f"Opened {platform.capitalize()}"
        else:
            # Try opening as a direct URL
            self.open_url(f"https://www.{platform_lower}.com")
            return f"Opened {platform}"

    def open_new_tab(self) -> str:
        """Open a new browser tab."""
        script = f'''
        tell application "{self.default_browser}"
            activate
            tell application "System Events"
                keystroke "t" using command down
            end tell
        end tell
        '''
        subprocess.run(['/usr/bin/osascript', '-e', script], capture_output=True)
        return "Opened new tab"

    def close_current_tab(self) -> str:
        """Close the current browser tab."""
        script = f'''
        tell application "{self.default_browser}"
            activate
            tell application "System Events"
                keystroke "w" using command down
            end tell
        end tell
        '''
        subprocess.run(['/usr/bin/osascript', '-e', script], capture_output=True)
        return "Closed current tab"

    def go_back(self) -> str:
        """Navigate back in browser."""
        script = f'''
        tell application "{self.default_browser}"
            activate
            tell application "System Events"
                keystroke "[" using command down
            end tell
        end tell
        '''
        subprocess.run(['/usr/bin/osascript', '-e', script], capture_output=True)
        return "Navigated back"

    def refresh_page(self) -> str:
        """Refresh the current page."""
        script = f'''
        tell application "{self.default_browser}"
            activate
            tell application "System Events"
                keystroke "r" using command down
            end tell
        end tell
        '''
        subprocess.run(['/usr/bin/osascript', '-e', script], capture_output=True)
        return "Page refreshed"
