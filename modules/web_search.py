from duckduckgo_search import DDGS
import logging

logger = logging.getLogger(__name__)

def search_web(query: str, max_results: int = 3) -> str:
    """
    Виконує пошук через DuckDuckGo і повертає текст з результатів.
    Якщо сталася помилка, повертає порожній рядок.
    """
    try:
        with DDGS() as ddgs:
            results = []
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"Заголовок: {r['title']}\nТекст: {r['body']}\n")
            if not results:
                return ""
            return "\n".join(results)
    except Exception as e:
        logger.error(f"Помилка пошуку в інтернеті: {e}")
        return ""