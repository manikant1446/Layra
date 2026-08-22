"""
Layra Research Module
================================
Web research, weather, news, and knowledge retrieval.
Uses DuckDuckGo search + Gemini for AI-powered research summaries.
"""

import logging
import json
from datetime import datetime

logger = logging.getLogger("layra.researcher")


class Researcher:
    """Performs web research and information retrieval."""

    def research_topic(self, topic: str, depth: str = "quick") -> str:
        """
        Research a topic by searching the web and summarizing results.
        
        Args:
            topic: Topic to research
            depth: 'quick' (1-3 sources) or 'deep' (5+ sources)
        """
        max_results = 3 if depth == "quick" else 8

        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(topic, max_results=max_results))

            if not results:
                return f"No results found for: {topic}"

            # Format results
            formatted = []
            for i, r in enumerate(results, 1):
                title = r.get('title', 'No title')
                body = r.get('body', '')
                href = r.get('href', '')
                formatted.append(f"Source {i}: {title}\n{body}\nURL: {href}")

            summary = f"Research on '{topic}' ({len(results)} sources found):\n\n"
            summary += "\n\n".join(formatted)
            logger.info(f"🔍 Researched: {topic} ({len(results)} sources)")
            return summary

        except ImportError:
            return f"Research module needs duckduckgo-search package. Topic: {topic}"
        except Exception as e:
            logger.error(f"Research error: {e}")
            return f"Research error: {e}"

    def get_weather(self, city: str) -> str:
        """Get weather information for a city using wttr.in."""
        try:
            import requests
            response = requests.get(
                f"https://wttr.in/{city}?format=j1",
                timeout=10,
                headers={"User-Agent": "Layra/1.0"}
            )
            if response.status_code == 200:
                data = response.json()
                current = data.get("current_condition", [{}])[0]
                temp_c = current.get("temp_C", "N/A")
                feels_like = current.get("FeelsLikeC", "N/A")
                humidity = current.get("humidity", "N/A")
                desc = current.get("weatherDesc", [{}])[0].get("value", "N/A")
                wind = current.get("windspeedKmph", "N/A")

                return (
                    f"Weather in {city}:\n"
                    f"Temperature: {temp_c}°C (feels like {feels_like}°C)\n"
                    f"Condition: {desc}\n"
                    f"Humidity: {humidity}%\n"
                    f"Wind: {wind} km/h"
                )
            else:
                return f"Could not get weather for {city}"
        except ImportError:
            return "Weather module needs 'requests' package"
        except Exception as e:
            return f"Weather error: {e}"

    def get_news(self, topic: str = None) -> str:
        """Get latest news headlines."""
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                query = topic if topic else "top news today"
                results = list(ddgs.news(query, max_results=5))

            if not results:
                return "No news found"

            news_items = []
            for i, r in enumerate(results, 1):
                title = r.get('title', 'No title')
                source = r.get('source', 'Unknown')
                body = r.get('body', '')[:100]
                news_items.append(f"{i}. [{source}] {title}\n   {body}")

            return "Latest News:\n" + "\n".join(news_items)

        except ImportError:
            return "News module needs duckduckgo-search package"
        except Exception as e:
            return f"News error: {e}"

    def get_wikipedia(self, topic: str) -> str:
        """Get Wikipedia summary for a topic."""
        try:
            import requests
            response = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}",
                timeout=10,
                headers={"User-Agent": "Layra/1.0"}
            )
            if response.status_code == 200:
                data = response.json()
                title = data.get("title", topic)
                extract = data.get("extract", "No information found")
                return f"Wikipedia - {title}:\n{extract}"
            else:
                return f"No Wikipedia article found for: {topic}"
        except Exception as e:
            return f"Wikipedia error: {e}"
