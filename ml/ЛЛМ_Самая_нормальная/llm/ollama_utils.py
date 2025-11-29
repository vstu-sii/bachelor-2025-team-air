# llm/ollama_utils.py
import subprocess
import time

MODEL_NAME = "gemma3:1b"
TIMEOUT = 75  # Увеличим таймаут для больших промптов

def generate_from_ollama(prompt: str):
    """
    Запуск Ollama через stdin
    """
    cmd = ["ollama", "run", MODEL_NAME]

    try:
        start_time = time.time()

        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            encoding='utf-8',
            errors='ignore'
        )

        end_time = time.time()
        print(f"⏱️  Ответ за {end_time - start_time:.2f} сек")

        if result.returncode != 0:
            print(f"❌ Ошибка Ollama: {result.stderr}")
            return ""

        output = result.stdout.strip()
        return output

    except subprocess.TimeoutExpired:
        print(f"⏰ Таймаут {TIMEOUT} сек")
        return ""
    except Exception as e:
        print(f"⚠️  Ошибка: {e}")
        return ""