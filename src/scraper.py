"""
Pirate Radio AI - News Scraper
Scrapes trending topics from Reddit, RSS feeds, and APIs
"""
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
import aiohttp
import feedparser
from bs4 import BeautifulSoup

import config

logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    """Represents a single news item"""
    title: str
    summary: str
    source: str
    url: str
    timestamp: datetime
    category: str = "general"
    score: float = 0.0  # For ranking


class NewsScraper:
    """Aggregates news from multiple sources"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: List[NewsItem] = []
        self.last_fetch: Optional[datetime] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "PirateRadioAI/1.0"}
        )
        return self
        
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
            
    async def fetch_all(self) -> List[NewsItem]:
        """Fetch news from all sources"""
        logger.info("Fetching news from all sources...")
        
        tasks = [
            self.fetch_reddit(),
            self.fetch_rss(),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_news = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Scraper error: {result}")
            else:
                all_news.extend(result)
        
        # Sort by score and recency
        all_news.sort(key=lambda x: (x.score, x.timestamp), reverse=True)
        
        # Deduplicate by similar titles
        unique_news = self._deduplicate(all_news)
        
        # Take top N items
        self.cache = unique_news[:config.MAX_NEWS_ITEMS]
        self.last_fetch = datetime.now()
        
        logger.info(f"Fetched {len(self.cache)} news items")
        return self.cache
    
    async def fetch_reddit(self) -> List[NewsItem]:
        """Fetch trending posts from Reddit"""
        news_items = []
        
        for subreddit in config.REDDIT_SUBREDDITS:
            try:
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        posts = data.get("data", {}).get("children", [])
                        
                        for post in posts[:5]:
                            post_data = post.get("data", {})
                            
                            # Skip stickied/pinned posts
                            if post_data.get("stickied"):
                                continue
                                
                            news_items.append(NewsItem(
                                title=post_data.get("title", ""),
                                summary=post_data.get("selftext", "")[:500] or post_data.get("title", ""),
                                source=f"Reddit r/{subreddit}",
                                url=f"https://reddit.com{post_data.get('permalink', '')}",
                                timestamp=datetime.fromtimestamp(post_data.get("created_utc", 0)),
                                category=self._categorize(subreddit),
                                score=post_data.get("score", 0) / 1000  # Normalize score
                            ))
                            
                        logger.debug(f"Fetched {len(posts)} posts from r/{subreddit}")
                    else:
                        logger.warning(f"Reddit API returned {response.status} for r/{subreddit}")
                        
            except Exception as e:
                logger.error(f"Error fetching r/{subreddit}: {e}")
                
        return news_items
    
    async def fetch_rss(self) -> List[NewsItem]:
        """Fetch news from RSS feeds"""
        news_items = []
        
        for feed_url in config.RSS_FEEDS:
            try:
                async with self.session.get(feed_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        
                        source_name = feed.feed.get("title", feed_url)
                        
                        for entry in feed.entries[:5]:
                            # Parse timestamp
                            published = entry.get("published_parsed") or entry.get("updated_parsed")
                            if published:
                                timestamp = datetime(*published[:6])
                            else:
                                timestamp = datetime.now()
                            
                            # Get summary
                            summary = entry.get("summary", entry.get("description", ""))
                            # Strip HTML
                            if summary:
                                soup = BeautifulSoup(summary, "html.parser")
                                summary = soup.get_text()[:500]
                            
                            news_items.append(NewsItem(
                                title=entry.get("title", ""),
                                summary=summary or entry.get("title", ""),
                                source=source_name,
                                url=entry.get("link", ""),
                                timestamp=timestamp,
                                category="world",
                                score=self._calculate_rss_score(timestamp)
                            ))
                            
                        logger.debug(f"Fetched {len(feed.entries)} items from {source_name}")
                        
            except Exception as e:
                logger.error(f"Error fetching RSS {feed_url}: {e}")
                
        return news_items
    
    def _deduplicate(self, items: List[NewsItem]) -> List[NewsItem]:
        """Remove similar news items"""
        unique = []
        seen_titles = set()
        
        for item in items:
            # Simple dedup by first few words
            key = " ".join(item.title.lower().split()[:5])
            if key not in seen_titles:
                seen_titles.add(key)
                unique.append(item)
                
        return unique
    
    def _categorize(self, subreddit: str) -> str:
        """Categorize news by subreddit"""
        categories = {
            "worldnews": "world",
            "technology": "tech",
            "science": "science",
            "serbia": "local",
            "news": "general",
        }
        return categories.get(subreddit.lower(), "general")
    
    def _calculate_rss_score(self, timestamp: datetime) -> float:
        """Calculate score based on recency"""
        age = datetime.now() - timestamp
        # Newer = higher score
        if age < timedelta(hours=1):
            return 10.0
        elif age < timedelta(hours=6):
            return 5.0
        elif age < timedelta(hours=24):
            return 2.0
        return 1.0


class WeatherFetcher:
    """Fetches weather data from free API"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
        return self
        
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    async def get_weather(self, city: str = None) -> Optional[dict]:
        """Get current weather for a city"""
        city = city or config.WEATHER_CITY
        
        # Using wttr.in - free, no API key needed
        try:
            url = f"https://wttr.in/{city}?format=j1"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    current = data.get("current_condition", [{}])[0]
                    
                    return {
                        "city": city.split(",")[0],
                        "temp": current.get("temp_C", "?"),
                        "feels_like": current.get("FeelsLikeC", "?"),
                        "description": current.get("weatherDesc", [{}])[0].get("value", ""),
                        "humidity": current.get("humidity", "?"),
                        "wind": current.get("windspeedKmph", "?"),
                        "wind_dir": current.get("winddir16Point", ""),
                    }
                    
        except Exception as e:
            logger.error(f"Weather fetch error: {e}")
            
        return None


# Test
async def main():
    async with NewsScraper() as scraper:
        news = await scraper.fetch_all()
        for item in news:
            print(f"[{item.source}] {item.title}")
            print(f"  Score: {item.score}, Category: {item.category}")
            print()
            
    async with WeatherFetcher() as weather:
        w = await weather.get_weather("Belgrade")
        if w:
            print(f"Weather: {w['temp']}°C, {w['description']}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
