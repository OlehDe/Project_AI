import asyncio
import logging
from ddgs import DDGS

logger = logging.getLogger(__name__)

def _sync_search(query: str, max_results: int) -> str:
    """Синхронна функція пошуку – виконується в окремому потоці."""
    try:
        with DDGS() as ddgs:
            results = []
            search_results = ddgs.text(query, max_results=max_results)
            for r in search_results:
                results.append(f"Заголовок: {r['title']}\nТекст: {r['body']}\n")
            if not results:
                return ""
            return "\n".join(results)
    except Exception as e:
        logger.error(f"Помилка пошуку в інтернеті: {e}")
        return ""

async def search_web(query: str, max_results: int = 3) -> str:
    """Асинхронна обгортка для пошуку – запускає синхронну функцію в потоці."""
    return await asyncio.to_thread(_sync_search, query, max_results)