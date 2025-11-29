import pandas as pd
from llm.vector_search import VectorSearch
from llm.ranker import rank_top_candidates
from llm.generator import generate_interview_questions
import os

VACANCY_TEXT = "Python разработчик с опытом работы НЕ МЕНЬШЕ 3 года, требуемые навыки: Django, SQL, Git"


def display_complete_resume(candidate):
    """Выводит ПОЛНОЕ резюме со всеми полями"""
    print("📋 ПОЛНОЕ РЕЗЮМЕ:")
    print("-" * 80)

    important_fields = [
        'full_name', 'age', 'city', 'profession',
        'experience_years', 'experience_level',
        'work_experience', 'skills', 'salary',
        'education', 'languages', 'job_expectations'
    ]

    for field in important_fields:
        if field in candidate and candidate[field] and str(candidate[field]) != 'nan':
            value_str = str(candidate[field])
            if field == 'work_experience' and len(value_str) > 500:
                value_str = value_str[:500] + "... [полный текст обрезан]"
            elif len(value_str) > 300:
                value_str = value_str[:300] + "..."
            print(f"   🔹 {field.upper()}: {value_str}")

    for field, value in candidate.items():
        if field not in important_fields and value and str(value) != 'nan' and str(value).strip():
            value_str = str(value)
            if len(value_str) > 200:
                value_str = value_str[:200] + "..."
            print(f"   ▪️  {field}: {value_str}")

    print("-" * 80)


def analyze_candidate_experience(candidate, vacancy_text):
    """Анализирует опыт кандидата относительно вакансии"""
    print("\n🔍 АНАЛИЗ ОПЫТА:")

    experience_info = []

    # Извлекаем требуемый опыт из вакансии
    import re
    vacancy_lower = vacancy_text.lower()
    required_experience = None
    
    # Поиск требуемого опыта в вакансии
    experience_patterns = [
        (r'(\d+)[\s\-]*год[ау]?', 'года'),
        (r'(\d+)[\s\-]*лет', 'лет'),
        (r'опыт[\s\w]{0,20}(\d+)[\s\-]*год', 'года'),
        (r'(\d+)[\s\-]*years', 'years'),
        (r'от[\s]*(\d+)[\s]*год', 'года')
    ]

    for pattern, unit in experience_patterns:
        matches = re.findall(pattern, vacancy_lower)
        if matches:
            required_experience = int(matches[0])
            break

    # Опыт кандидата
    if 'experience_years' in candidate and candidate['experience_years'] and str(candidate['experience_years']) != 'nan':
        try:
            candidate_years = float(str(candidate['experience_years']).split()[0])
            experience_info.append(f"📅 {candidate_years} лет опыта")

            # Сравнение с требуемым опытом
            if required_experience:
                if candidate_years >= required_experience:
                    experience_info.append(f"✅ Соответствует требуемому опыту ({required_experience}+ года)")
                elif candidate_years >= required_experience - 1:
                    experience_info.append(f"⚠️  Близко к требуемому ({required_experience} года)")
                else:
                    experience_info.append(f"❌ Меньше требуемого опыта ({required_experience} года)")
            else:
                experience_info.append("ℹ️  Требуемый опыт не указан в вакансии")
        except:
            experience_info.append("📅 Опыт указан (формат не распознан)")

    # Уровень опыта
    if 'experience_level' in candidate and candidate['experience_level'] and str(candidate['experience_level']) != 'nan':
        experience_info.append(f"🎯 Уровень: {candidate['experience_level']}")

    if experience_info:
        for info in experience_info:
            print(f"   {info}")
    else:
        print("   ❌ Опыт не указан")


def analyze_candidate_skills(candidate, vacancy_text):
    """Анализирует навыки кандидата относительно требований вакансии"""
    print("\n🔧 АНАЛИЗ НАВЫКОВ:")

    # Извлекаем технологии из вакансии
    from llm.ranker import extract_technologies_from_vacancy
    required_techs = extract_technologies_from_vacancy(vacancy_text)
    
    candidate_text = ""

    # Собираем весь текст кандидата из ключевых полей
    text_fields = ['skills', 'work_experience', 'job_expectations', 'ml_text', 'profession']
    for field in text_fields:
        if field in candidate and candidate[field] and str(candidate[field]) != 'nan':
            candidate_text += str(candidate[field]).lower() + " "

    # Анализируем совпадения
    matches = []
    missing = []

    for tech in required_techs:
        if tech in candidate_text:
            matches.append(tech)
        else:
            missing.append(tech)

    print(f"   🎯 Требуемые технологии: {', '.join(required_techs) if required_techs else 'не определены'}")
    print(f"   ✅ Есть у кандидата: {', '.join(matches) if matches else 'нет совпадений'}")
    print(f"   ❌ Отсутствуют: {', '.join(missing) if missing else 'все технологии присутствуют'}")

    # Оценка соответствия
    if required_techs:
        match_percentage = len(matches) / len(required_techs) * 100
        if match_percentage >= 80:
            print(f"   🎯 Соответствие: ОТЛИЧНОЕ ({match_percentage:.0f}%)")
        elif match_percentage >= 60:
            print(f"   🎯 Соответствие: ХОРОШЕЕ ({match_percentage:.0f}%)")
        elif match_percentage >= 40:
            print(f"   🎯 Соответствие: УДОВЛЕТВОРИТЕЛЬНОЕ ({match_percentage:.0f}%)")
        else:
            print(f"   🎯 Соответствие: СЛАБОЕ ({match_percentage:.0f}%)")
    else:
        print("   ℹ️  Не удалось определить требуемые технологии")


def main():
    print("🚀 Запускаем универсальную систему подбора кандидатов...")
    print(f"🎯 Вакансия: {VACANCY_TEXT}")

    # Загружаем данные
    df = pd.read_csv("data/resume_dataset_fixed.csv")
    print(f"📊 Загружено {len(df)} кандидатов")

    # Покажем структуру данных
    print(f"📋 Колонки в датасете: {df.columns.tolist()}")

    # Создаем combined_text из ключевых полей
    print("\n🔧 Создаем объединенный текст резюме...")
    text_fields = ['skills', 'work_experience', 'job_expectations', 'ml_text']
    available_fields = [field for field in text_fields if field in df.columns]
    print(f"   Используем поля: {available_fields}")

    df['combined_text'] = df.apply(
        lambda row: " ".join([
            str(row[field]) for field in available_fields
            if field in row and pd.notna(row[field])
        ]),
        axis=1
    )

    candidates = df.to_dict(orient="records")

    # Инициализируем векторный поиск
    vs = VectorSearch()

    # Строим или загружаем индекс
    index_path = 'data/faiss_index'
    if os.path.exists(f"{index_path}/index.faiss"):
        vs.load_index(index_path)
    else:
        print("🔨 Строим индекс для быстрого поиска...")
        vs.build_index(candidates)
        vs.save_index(index_path)

    print("\n⚡ Запускаем быстрый векторный поиск...")

    # Быстрый поиск топ-100 кандидатов
    similar_candidates = vs.search(VACANCY_TEXT, top_k=100)
    print(f"🔍 Найдено {len(similar_candidates)} перспективных кандидатов")

    # AI выбирает топ-10 из 100 с учетом требований вакансии
    print("🤖 Уточняем выбор с помощью AI...")
    top_10_candidates = rank_top_candidates(VACANCY_TEXT, similar_candidates, top_n=10)

    # Выводим результаты
    print(f"\n🏆 ТОП-10 КАНДИДАТОВ:")
    print("=" * 100)

    for idx, item in enumerate(top_10_candidates, start=1):
        c = item["candidate"]
        score = item["score"]
        source = item.get("source", "unknown")

        print(f"\n🎖️  КАНДИДАТ #{idx} | ОЦЕНКА: {score:.3f} | ИСТОЧНИК: {source}")
        print("=" * 80)

        # Выводим ПОЛНОЕ резюме со всеми полями
        display_complete_resume(c)

        # Анализируем опыт относительно вакансии
        analyze_candidate_experience(c, VACANCY_TEXT)

        # Анализируем навыки относительно вакансии
        analyze_candidate_skills(c, VACANCY_TEXT)

        # Генерируем вопросы
        print("\n❓ ВОПРОСЫ ДЛЯ СОБЕСЕДОВАНИЯ:")
        questions = generate_interview_questions(c.get("combined_text", ""), VACANCY_TEXT)

        if questions is None:
            questions = ["Не удалось сгенерировать вопросы"]

        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q}")

        print("\n" + "=" * 100)

    print(f"\n✅ Анализ завершен! Найдено {len(top_10_candidates)} лучших кандидатов.")


if __name__ == "__main__":
    main()