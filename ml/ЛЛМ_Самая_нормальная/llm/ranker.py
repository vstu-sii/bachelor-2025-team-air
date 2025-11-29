from .ollama_utils import generate_from_ollama
import re

def extract_technologies_from_vacancy(vacancy_text):
    """Автоматически извлекает технологии из текста вакансии"""
    text_lower = vacancy_text.lower()

    # Словарь технологий для автоматического определения
    all_technologies = {
        'python': ['python', 'питон'],
        'django': ['django', 'джанго'],
        'postgresql': ['postgresql', 'postgres', 'постгрес'],
        'docker': ['docker', 'докер'],
        'sql': ['sql', 'баз данных', 'бд'],
        'flask': ['flask', 'фласк'],
        'fastapi': ['fastapi'],
        'javascript': ['javascript', 'js', '前端'],
        'react': ['react', 'реакт'],
        'vue': ['vue', 'вью'],
        'java': ['java', 'джава'],
        'spring': ['spring', 'спринг'],
        'c#': ['c#', 'c sharp', 'си шарп'],
        'php': ['php', 'пхп'],
        'laravel': ['laravel', 'ларавел'],
        'go': ['go', 'golang'],
        'rust': ['rust', 'раст'],
        'kubernetes': ['kubernetes', 'k8s', 'кубернетис'],
        'aws': ['aws', 'amazon web services'],
        'mongodb': ['mongodb', 'mongo'],
        'redis': ['redis', 'редис'],
        'git': ['git', 'гит'],
        'linux': ['linux', 'линукс'],
        'html': ['html', 'хтмл'],
        'css': ['css', 'каскадные'],
        'typescript': ['typescript', 'ts'],
        'node.js': ['node.js', 'nodejs', 'нод'],
        'angular': ['angular', 'ангуляр']
    }

    found_techs = []
    for tech, keywords in all_technologies.items():
        if any(keyword in text_lower for keyword in keywords):
            found_techs.append(tech)

    return found_techs


def extract_experience_from_vacancy(vacancy_text):
    """Автоматически извлекает требуемый опыт из вакансии"""
    text_lower = vacancy_text.lower()

    # Паттерны для поиска опыта
    experience_patterns = [
        (r'(\d+)[\s\-]*год[ау]?', 'года'),
        (r'(\d+)[\s\-]*лет', 'лет'),
        (r'опыт[\s\w]{0,20}(\d+)[\s\-]*год', 'года'),
        (r'(\d+)[\s\-]*years', 'years'),
        (r'от[\s]*(\d+)[\s]*год', 'года'),
        (r'не[\s]*менее[\s]*(\d+)[\s]*год', 'года'),
        (r'(\d+)[\+][\s]*год', 'года')
    ]

    for pattern, unit in experience_patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            try:
                years = int(matches[0])
                return years
            except:
                continue

    return None  # если опыт не указан


def identify_critical_technologies(vacancy_text, all_techs):
    """Определяет критически важные технологии для вакансии"""
    text_lower = vacancy_text.lower()
    critical_techs = []

    # Основная технология обычно упоминается первой
    if 'python' in text_lower and 'python' in all_techs:
        critical_techs.append('python')
    elif 'java' in text_lower and 'java' in all_techs:
        critical_techs.append('java')
    elif 'javascript' in text_lower and 'javascript' in all_techs:
        critical_techs.append('javascript')

    # Добавляем основные фреймворки если они явно указаны
    framework_keywords = ['django', 'spring', 'react', 'vue', 'angular', 'flask']
    for framework in framework_keywords:
        if framework in text_lower and framework in all_techs:
            critical_techs.append(framework)

    return critical_techs if critical_techs else all_techs[:2]


def filter_candidates_by_experience(candidates, required_experience):
    """Фильтрует кандидатов по требуемому опыту"""
    if required_experience is None:
        return candidates  # если опыт не указан, возвращаем всех

    filtered_candidates = []
    
    for candidate in candidates:
        candidate_data = candidate["candidate"]
        
        # Проверяем опыт кандидата
        if 'experience_years' in candidate_data and candidate_data['experience_years'] and str(candidate_data['experience_years']) != 'nan':
            try:
                # Пытаемся извлечь число из опыта кандидата
                candidate_exp_str = str(candidate_data['experience_years'])
                # Ищем число в строке (например, "3 года" -> 3)
                exp_match = re.search(r'(\d+)[\s\-\+]*', candidate_exp_str)
                if exp_match:
                    candidate_years = int(exp_match.group(1))
                    
                    # Кандидат проходит если его опыт >= требуемого
                    if candidate_years >= required_experience:
                        filtered_candidates.append(candidate)
                    else:
                        print(f"   ⚠️  Кандидат отфильтрован: опыт {candidate_years} < {required_experience}")
                else:
                    # Если не можем распарсить, оставляем кандидата
                    filtered_candidates.append(candidate)
            except (ValueError, AttributeError):
                # Если ошибка парсинга, оставляем кандидата
                filtered_candidates.append(candidate)
        else:
            # Если опыт не указан, оставляем кандидата
            filtered_candidates.append(candidate)
    
    print(f"📊 После фильтрации по опыту: {len(filtered_candidates)} кандидатов")
    return filtered_candidates


def calculate_smart_tech_score(text, skills, required_techs, critical_techs):
    """Умная оценка соответствия технологий"""
    if not required_techs:
        return 0.6  # базовый балл если не определили технологии

    total_techs = len(required_techs)
    found_techs = []

    # Считаем найденные технологии
    for tech in required_techs:
        if tech in text or tech in skills:
            found_techs.append(tech)

    # ЩАДЯЩАЯ оценка по проценту совпадений
    base_ratio = len(found_techs) / total_techs

    # Бонусы и штрафы
    bonus = 0
    penalty = 0

    # Бонус за критические технологии
    critical_matches = sum(1 for tech in critical_techs if tech in found_techs)
    if critical_matches == len(critical_techs):
        bonus += 0.4  # ВСЕ критические технологии есть
    elif critical_matches >= 1:
        bonus += 0.25  # хотя бы одна критическая

    # МЕНЬШИЙ штраф за отсутствие критических технологий
    if critical_techs and critical_matches == 0:
        penalty -= 0.2

    # Бонус за множество технологий
    if len(found_techs) >= total_techs - 1:
        bonus += 0.3
    elif len(found_techs) >= total_techs - 2:
        bonus += 0.2
    elif len(found_techs) >= 1:
        bonus += 0.1

    # ЩАДЯЩАЯ формула
    final_score = base_ratio * 0.4 + bonus + penalty
    return max(0.3, min(final_score, 1.0))


def parse_ranked_with_scores(response: str, candidates: list, top_n: int):
    """Улучшенный парсинг ответа AI - понимает разные форматы"""
    if not response:
        print("❌ Пустой ответ от AI")
        return None

    print(f"🔍 Парсим ответ AI: {response[:200]}...")

    ranked = []
    lines = response.strip().split('\n')

    for line in lines:
        line = line.strip()

        # Пробуем разные форматы ответа AI
        formats_to_try = [
            r'(\d+)[\.\)]\s*(?:Кандидат\s+)?(\d+)\s*:\s*([0-9]*\.?[0-9]+)',
            r'(\d+)[\.\)]?\s*(\d+)?\s*:\s*([0-9]*\.?[0-9]+)',
            r'\*?\*?Кандидат\s+(\d+)\*?\*?\s*:\s*([0-9]*\.?[0-9]+)',
            r'(\d+)[\.\)]\s*([0-9]*\.?[0-9]+)',
            r'Кандидат\s+(\d+)\s*:\s*([0-9]*\.?[0-9]+)',
            r'^\s*(\d+)\s*:\s*([0-9]*\.?[0-9]+)\s*$',
            r'[Кк]андидат\s+(\d+)\s*[-–]\s*([0-9]*\.?[0-9]+)'
        ]

        for pattern in formats_to_try:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    if len(match.groups()) == 3:
                        candidate_idx = int(match.group(2)) - 1
                        score = float(match.group(3))
                    else:
                        candidate_idx = int(match.group(1)) - 1
                        score = float(match.group(2))

                    if 0 <= candidate_idx < len(candidates) and 0 <= score <= 1:
                        print(f"✅ Распарсено: кандидат {candidate_idx + 1} -> оценка {score}")
                        ranked.append({
                            "candidate": candidates[candidate_idx]["candidate"],
                            "score": score,
                            "original_score": candidates[candidate_idx].get('score', 0),
                            "source": "AI"
                        })
                        break

                except (ValueError, IndexError) as e:
                    continue

    # Если нашли кандидатов, сортируем по оценке
    if ranked:
        ranked.sort(key=lambda x: x["score"], reverse=True)
        print(f"🎉 Успешно распарсено {len(ranked)} кандидатов от AI")

        # Дополняем если нужно
        if len(ranked) < top_n:
            selected_indices = [candidates.index(item["candidate"]) for item in ranked]
            for i in range(len(candidates)):
                if i not in selected_indices and len(ranked) < top_n:
                    ranked.append({
                        "candidate": candidates[i]["candidate"],
                        "score": candidates[i].get('score', 0),
                        "original_score": candidates[i].get('score', 0),
                        "source": "auto_added"
                    })

        return ranked[:top_n]
    else:
        print("❌ Не удалось распарсить ни одного кандидата из ответа AI")
        return None


def rank_top_candidates(vacancy_text: str, candidates: list, top_n=10):
    """
    Умная система ранжирования с фильтрацией по опыту
    """
    print(f"🎯 Ранжируем {len(candidates)} кандидатов для вакансии...")

    # Анализируем вакансию
    required_techs = extract_technologies_from_vacancy(vacancy_text)
    required_experience = extract_experience_from_vacancy(vacancy_text)

    print(f"🔍 Анализ вакансии:")
    print(f"   📅 Требуемый опыт: {required_experience if required_experience else 'не указан'}")
    print(f"   🔧 Ключевые технологии: {', '.join(required_techs) if required_techs else 'не определены'}")

    # ФИЛЬТРАЦИЯ: убираем кандидатов с недостаточным опытом
    filtered_candidates = filter_candidates_by_experience(candidates, required_experience)

    if not filtered_candidates:
        print("⚠️  После фильтрации по опыту не осталось кандидатов. Используем всех кандидатов.")
        filtered_candidates = candidates

    # Улучшенный промпт с акцентом на требования вакансии
    prompt = f"""ВАКАНСИЯ: {vacancy_text}

ТРЕБОВАНИЯ ВАКАНСИИ:
- Требуемый опыт: {required_experience if required_experience else 'не указан'}
- Ключевые технологии: {', '.join(required_techs) if required_techs else 'не определены'}

ПРОЦЕСС ОЦЕНКИ:
1. Сравни навыки кандидатов с ТРЕБОВАНИЯМИ ВАКАНСИИ
2. Оцени соответствие ОСНОВНЫМ ТЕХНОЛОГИЯМ из вакансии
3. Учитывай опыт работы (кандидаты с недостаточным опытом уже отфильтрованы)
4. ЦЕНИ соответствие КЛЮЧЕВЫМ ТЕХНОЛОГИЯМ вакансии
5. НЕ наказывай за отсутствие 1-2 второстепенных технологий

КАНДИДАТЫ ДЛЯ ОЦЕНКИ:"""

    for idx, candidate in enumerate(filtered_candidates, 1):
        candidate_data = candidate["candidate"]
        vector_score = candidate.get('score', 0)

        skills = candidate_data.get('skills', 'не указаны')
        experience_years = candidate_data.get('experience_years', 'не указаны')
        work_experience = candidate_data.get('work_experience', 'не указан')
        profession = candidate_data.get('profession', 'не указана')

        prompt += f"\n--- Кандидат {idx} ---"
        prompt += f"\nПрофессия: {profession}"
        prompt += f"\nОпыт (лет): {experience_years}"
        prompt += f"\nНавыки: {skills}"
        prompt += f"\nПредыдущие места работы: {work_experience}"
        if vector_score > 0:
            prompt += f"\nПредварительная оценка: {vector_score:.3f}"
        prompt += "\n"

    prompt += f"""
Верни номера ТОП-{top_n} кандидатов с их итоговыми оценками.

Формат ответа:
1. номер: оценка
2. номер: оценка
...
{top_n}. номер: оценка

Оценивай по шкале 0.0-1.0, ОСНОВЫВАЯСЬ НА ТРЕБОВАНИЯХ ВАКАНСИИ:

КРИТЕРИИ ОЦЕНКИ:
- 0.9-1.0: ИДЕАЛЬНО - все ключевые технологии вакансии + хороший опыт
- 0.7-0.9: ОТЛИЧНО - большинство ключевых технологий (минус 1-2) 
- 0.5-0.7: ХОРОШО - есть основные технологии вакансии
- 0.3-0.5: УДОВЛЕТВОРИТЕЛЬНО - базовое соответствие
- 0.0-0.3: СЛАБО - минимальное соответствие

ВАЖНО: Оценивай строго относительно требований вакансии!"""

    response = generate_from_ollama(prompt)
    print(f"🤖 Ответ AI получен")

    # Парсим результаты
    ranked_candidates = parse_ranked_with_scores(response, filtered_candidates, top_n)

    if ranked_candidates:
        print(f"✅ Используем оценки от AI")
        return ranked_candidates
    else:
        print("⚠️  Не удалось распарсить ответ AI, используем улучшенный автоматический рейтинг")
        ranked_candidates = enhanced_automatic_ranking(filtered_candidates, required_techs, vacancy_text, top_n)
        return ranked_candidates


def enhanced_automatic_ranking(candidates, required_techs, vacancy_text, top_n):
    """Улучшенный автоматический рейтинг"""
    print("🔧 Используем улучшенный автоматический анализ...")

    scored_candidates = []
    vacancy_lower = vacancy_text.lower()

    for candidate in candidates:
        candidate_data = candidate["candidate"]
        text = candidate_data.get('combined_text', '').lower()
        skills = candidate_data.get('skills', '').lower()

        # Базовый score из векторного поиска
        base_score = candidate.get('score', 0)

        # Определяем критически важные технологии
        critical_techs = identify_critical_technologies(vacancy_text, required_techs)

        # Умная оценка технологий
        tech_score = calculate_smart_tech_score(text, skills, required_techs, critical_techs)

        # Финальная оценка (технологии 80%, база 20%)
        final_score = base_score * 0.2 + tech_score * 0.8
        final_score = min(final_score, 1.0)

        scored_candidates.append({
            "candidate": candidate_data,
            "score": round(final_score, 3),
            "tech_score": round(tech_score, 3),
            "source": "auto"
        })

    # Сортируем по убыванию оценки
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)

    if scored_candidates:
        best = scored_candidates[0]
        print(f"📊 Лучший кандидат: {best['score']:.3f} (технологии: {best['tech_score']:.3f})")

    return scored_candidates[:top_n]