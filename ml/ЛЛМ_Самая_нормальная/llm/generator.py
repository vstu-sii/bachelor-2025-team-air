# llm/generator.py
from .ollama_utils import generate_from_ollama
import re


def generate_interview_questions(candidate_text: str, vacancy_text: str):
    """
    Генерирует вопросы с улучшенной обработкой ошибок
    """
    print("💭 Генерируем вопросы для собеседования...")

    # Подготавливаем текст кандидата
    candidate_preview = candidate_text[:300] + "..." if len(candidate_text) > 300 else candidate_text

    prompt = f"""Ты HR-специалист. Создай 5 технических вопросов для собеседования.

ВАКАНСИЯ: {vacancy_text}

РЕЗЮМЕ КАНДИДАТА: {candidate_preview}

Сгенерируй 5 релевантных вопросов. Вопросы не должны повторяться. Каждый вопрос должен быть пронумерован. 

Формат ответа:
1. Первый вопрос?
2. Второй вопрос?
3. Третий вопрос?
4. Четвертый вопрос?
5. Пятый вопрос?

Только вопросы, без лишнего текста. """

    response = generate_from_ollama(prompt)

    # ВАЖНО: Всегда возвращаем список, никогда не None
    if not response:
        print("⚠️  Не удалось сгенерировать вопросы, используем fallback")
        return get_fallback_questions(vacancy_text)

    questions = parse_questions(response)

    if len(questions) < 3:
        print("⚠️  Сгенерировано мало вопросов, используем fallback")
        questions = get_fallback_questions(vacancy_text)

    # Убедимся, что всегда возвращаем 5 вопросов
    while len(questions) < 5:
        questions.append("Расскажите о вашем опыте работы с требуемыми технологиями?")

    return questions[:5]


def parse_questions(response: str):
    """Парсит вопросы из ответа модели"""
    questions = []

    if not response:
        return questions

    for line in response.split('\n'):
        line = line.strip()
        # Ищем пронумерованные строки
        match = re.match(r'^(\d+[\.\)]\s*)(.+\?)', line)
        if match:
            question = match.group(2).strip()
            if question and len(question) > 10:
                questions.append(question)
        # Или строки с вопросами
        elif line.endswith('?') and len(line) > 15:
            clean_line = re.sub(r'^[\d\-•\s]+', '', line)
            if clean_line:
                questions.append(clean_line)

    return questions


def get_fallback_questions(vacancy_text: str):
    """Запасные вопросы на основе вакансии"""
    print("🔄 Используем стандартные вопросы...")

    tech_questions = {
        'python': "Расскажите о вашем опыте работы с Python?",
        'django': "Какие проекты разрабатывали с использованием Django?",
        'postgresql': "Какой опыт работы с базами данных PostgreSQL?",
        'docker': "Использовали ли вы Docker в рабочих проектах?",
        'sql': "Как вы оптимизируете SQL запросы?"
    }

    questions = []
    vacancy_lower = vacancy_text.lower()

    # Добавляем вопросы по технологиям из вакансии
    for tech, question in tech_questions.items():
        if tech in vacancy_lower and len(questions) < 5:
            questions.append(question)

    # Дополняем универсальными вопросами
    universal = [
        "С какими техническими сложностями сталкивались в проектах?",
        "Как вы оцениваете свой уровень владения требуемыми технологиями?",
        "Расскажите о самом интересном проекте в вашей карьере?",
        "Как вы подходите к решению сложных технических задач?",
        "Что для вас важно в работе разработчика?"
    ]

    for q in universal:
        if len(questions) < 5 and q not in questions:
            questions.append(q)

    return questions[:5]