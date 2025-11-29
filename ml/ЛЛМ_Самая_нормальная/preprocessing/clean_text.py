import re

def clean_text(text: str) -> str:
    """
    Простейшая очистка текста:
    - убираем лишние пробелы и переносы строк
    - приводим к нижнему регистру
    """
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text.lower()
