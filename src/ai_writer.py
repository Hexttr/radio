"""
Pirate Radio AI - AI News Writer
Generates radio-ready news scripts using Groq (Llama)
"""
import asyncio
import logging
import random
from typing import List, Optional
from groq import AsyncGroq

import config
from src.scraper import NewsItem

logger = logging.getLogger(__name__)


class AIWriter:
    """Generates radio scripts using Llama via Groq"""
    
    def __init__(self):
        self.api_key = (config.GROQ_API_KEY or "").strip()
        self.client = AsyncGroq(api_key=self.api_key) if self.api_key else None
        
    async def generate_news_segment(self, news_items: List[NewsItem]) -> Optional[str]:
        """Generate a complete news segment from news items. Returns None to skip (no filler)."""
        
        if not news_items:
            return None  # Не озвучиваем filler — просто пропускаем блок новостей
        
        # Build news list for prompt
        news_text = "\n".join([
            f"{i+1}. [{item.category.upper()}] {item.title}\n   {item.summary[:200]}..."
            for i, item in enumerate(news_items)
        ])
        
        lang = config.PROMPT_LANG
        rules = config.NEWS_PROMPT_LANG.get(lang, config.NEWS_PROMPT_LANG["en"])
        prompt = f"""Write a short radio news segment based on these items.

ITEMS:
{news_text}

{rules}

STYLE: {config.NEWS_STYLE}"""

        if not self.client:
            logger.warning("GROQ_API_KEY not set - skipping news. Get free key at console.groq.com")
            return None
        system_prompt = config.NEWS_SYSTEM_PROMPTS.get(lang, config.NEWS_SYSTEM_PROMPTS["en"]).format(style=config.NEWS_STYLE)
        try:
            response = await self.client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
            )
            
            script = response.choices[0].message.content
            logger.info(f"Generated news segment: {len(script)} chars")
            return script
            
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return None
    
    async def generate_weather_report(self, weather_data: dict) -> str:
        """Generate a weather report"""
        
        if not weather_data:
            fallbacks = {"ru": "Прогноз погоды временно недоступен.", "en": "Weather forecast is temporarily unavailable.", "sr": "Vremensku prognozu trenutno ne možemo da vam prenesemo."}
            return fallbacks.get(config.PROMPT_LANG, fallbacks["en"])
        
        lang = config.PROMPT_LANG
        tmpl = config.WEATHER_PROMPTS.get(lang, config.WEATHER_PROMPTS["en"])
        prompt = tmpl.format(
            city=weather_data.get("city", "Belgrade"),
            temp=weather_data.get("temp", "?"),
            description=weather_data.get("description", ""),
            humidity=weather_data.get("humidity", "?"),
            wind=weather_data.get("wind", "?"),
        )
        
        weather_system = {"ru": "Ты ведущий, читаешь прогноз погоды. Кратко и естественно.", "en": "You are a radio host reading the weather. Be brief and natural.", "sr": "Ti si radio voditelj koji čita vremensku prognozu. Budi kratak i prirodan."}
        if not self.client:
            city = weather_data.get("city", "")
            temp = weather_data.get("temp", "?")
            return {"ru": f"В {city} сейчас {temp} градусов.", "en": f"In {city} it's {temp} degrees.", "sr": f"U {city} je trenutno {temp} stepeni."}.get(lang, f"In {city} {temp}°C.")
        try:
            response = await self.client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": weather_system.get(lang, weather_system["en"])},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Weather generation error: {e}")
            city = weather_data.get("city", "")
            temp = weather_data.get("temp", "?")
            return {"ru": f"В {city} сейчас {temp} градусов.", "en": f"In {city} {temp}°C.", "sr": f"U {city} je trenutno {temp} stepeni."}.get(lang, f"In {city} {temp}°C.")
    
    async def generate_intro(self) -> str:
        """Generate a radio intro/jingle text"""
        intros = config.INTRO_TEXTS.get(config.PROMPT_LANG, config.INTRO_TEXTS["en"])
        return random.choice(intros)
    
    async def generate_outro(self) -> str:
        """Generate segment outro"""
        outros = config.OUTRO_TEXTS.get(config.PROMPT_LANG, config.OUTRO_TEXTS["en"])
        return random.choice(outros)
    
    async def generate_time_announcement(self) -> str:
        """Generate current time announcement"""
        from datetime import datetime
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        lang = config.PROMPT_LANG
        if lang == "ru":
            time_text = f"{hour} часов {minute} минут" if minute > 0 else f"{hour} часов"
        elif lang == "en":
            time_text = f"{hour} {minute}" if minute > 0 else f"{hour} o'clock"
        else:
            time_text = f"{hour} sati i {minute} minuta" if minute > 0 else f"{hour} sati"
        templates = config.TIME_TEMPLATES.get(lang, config.TIME_TEMPLATES["en"])
        return random.choice(templates).format(time=time_text)
    
    async def generate_custom_segment(self, topic: str, style: str = "informative") -> str:
        """Generate custom content segment"""
        lang_name = {"ru": "русском", "en": "English", "sr": "srpskom"}
        ln = lang_name.get(config.PROMPT_LANG, "English")
        prompt = f"""Write a short radio segment about: {topic}

STYLE: {style}
LENGTH: 50-100 words
LANGUAGE: {ln}
NO emoji or special characters"""

        if not self.client:
            return ""
        try:
            response = await self.client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a creative radio host."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.8,
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Custom segment error: {e}")
            return ""


# Test
async def main():
    from src.scraper import NewsScraper, WeatherFetcher
    
    writer = AIWriter()
    
    # Test news
    async with NewsScraper() as scraper:
        news = await scraper.fetch_all()
        if news:
            script = await writer.generate_news_segment(news[:3])
            print("=== NEWS SEGMENT ===")
            print(script)
            print()
    
    # Test weather
    async with WeatherFetcher() as weather:
        w = await weather.get_weather()
        if w:
            report = await writer.generate_weather_report(w)
            print("=== WEATHER REPORT ===")
            print(report)
            print()
    
    # Test intro
    intro = await writer.generate_intro()
    print("=== INTRO ===")
    print(intro)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
