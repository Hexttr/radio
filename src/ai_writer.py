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
        self.client = AsyncGroq(api_key=config.GROQ_API_KEY)
        
    async def generate_news_segment(self, news_items: List[NewsItem]) -> str:
        """Generate a complete news segment from news items"""
        
        if not news_items:
            return self._generate_filler()
        
        # Build news list for prompt
        news_text = "\n".join([
            f"{i+1}. [{item.category.upper()}] {item.title}\n   {item.summary[:200]}..."
            for i, item in enumerate(news_items)
        ])
        
        prompt = f"""Napiši kratak radio segment vijesti na osnovu sljedećih tema.
        
VIJESTI:
{news_text}

PRAVILA:
- Piši na srpskom jeziku (ćirilica ili latinica, svejedno)
- Svaka vijest maksimalno 2-3 rečenice
- Dodaj prirodne prelaze između vijesti ("A sada...", "U drugim vijestima...")
- Počni sa pozdravom slušaocima
- Završi sa "To su bile vijesti, vraćamo se muzici"
- Ukupno ne više od 300 riječi
- Ne koristi emoji ili specijalne znakove

STIL: {config.NEWS_STYLE}"""

        try:
            response = await self.client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": config.NEWS_SYSTEM_PROMPT.format(style=config.NEWS_STYLE)},
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
            return self._generate_filler()
    
    async def generate_weather_report(self, weather_data: dict) -> str:
        """Generate a weather report"""
        
        if not weather_data:
            return "Vremensku prognozu trenutno ne možemo da vam prenesemo."
        
        prompt = config.WEATHER_PROMPT.format(
            city=weather_data.get("city", "Beograd"),
            temp=weather_data.get("temp", "?"),
            description=weather_data.get("description", ""),
            humidity=weather_data.get("humidity", "?"),
            wind=weather_data.get("wind", "?"),
        )
        
        try:
            response = await self.client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "Ti si radio voditelj koji čita vremensku prognozu. Budi kratak i prirodan."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Weather generation error: {e}")
            return f"U {weather_data.get('city', 'gradu')} je trenutno {weather_data.get('temp', '?')} stepeni."
    
    async def generate_intro(self) -> str:
        """Generate a radio intro/jingle text"""
        intros = [
            "Dobrodošli na Pirate AI Radio! Vaš izvor muzike i informacija, dvadeset četiri sata dnevno.",
            "Ovo je Pirate Radio. Automatizovano. Beskonačno. Samo za vas.",
            "Pirate AI Radio na talasima! Ostanite s nama.",
            "Slušate Pirate Radio, gdje tehnologija sreće muziku.",
        ]
        return random.choice(intros)
    
    async def generate_outro(self) -> str:
        """Generate segment outro"""
        outros = [
            "To su bile vijesti. Nastavite da nas slušate.",
            "Hvala što ste bili s nama. Muzika se vraća.",
            "Pirate Radio nastavlja sa programom.",
            "Ostanite na vezi, vraćamo se nakon muzike.",
        ]
        return random.choice(outros)
    
    async def generate_time_announcement(self) -> str:
        """Generate current time announcement"""
        from datetime import datetime
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        
        time_text = f"{hour} sati i {minute} minuta" if minute > 0 else f"{hour} sati"
        
        templates = [
            f"Tačno je {time_text}.",
            f"Vrijeme je {time_text}. Slušate Pirate Radio.",
            f"Na Pirate Radiju je {time_text}.",
        ]
        return random.choice(templates)
    
    async def generate_custom_segment(self, topic: str, style: str = "informative") -> str:
        """Generate custom content segment"""
        prompt = f"""Napiši kratak radio segment na temu: {topic}

STIL: {style}
DUŽINA: 50-100 riječi
JEZIK: srpski
NE KORISTI: emoji, specijalne znakove"""

        try:
            response = await self.client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "Ti si kreativni radio voditelj."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.8,
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Custom segment error: {e}")
            return ""
    
    def _generate_filler(self) -> str:
        """Generate filler content when API fails"""
        fillers = [
            "Trenutno nemamo novih vijesti. Nastavite da uživate u muzici na Pirate Radiju.",
            "Vijesti se pripremaju. U međuvremenu, uživajte u muzici.",
            "Hvala što slušate Pirate Radio. Vijesti stižu uskoro.",
        ]
        return random.choice(fillers)


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
