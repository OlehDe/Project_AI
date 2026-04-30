from google import genai

# Вставте свій ключ
API_KEY = "AIzaSyBhVdFCJUDyWXx9faKPm8YPH4oECnkCJm4"

client = genai.Client(api_key=API_KEY)

# Список моделей, які ТОЧНО працюють станом на квітень 2025
models = [
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-pro",
    "gemini-2.5-pro",
    "gemini-2-flash-lite",
    "gemini-2.5-flash-tts",
    "gemini-3.1-flash-lite",
]

for model_name in models:
    try:
        print(f"Тестуємо {model_name}...")
        response = client.models.generate_content(
            model=model_name,
            contents="Скажи привіт українською"
        )
        print(f"✅ {model_name} працює! Відповідь: {response.text}")
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            print(f"⏳ {model_name}: вичерпано квоту (спробуйте пізніше)")
        elif "404" in error_msg:
            print(f"❌ {model_name}: модель не знайдено")
        elif "403" in error_msg:
            print(f"🚫 {model_name}: ключ заблоковано")
        else:
            print(f"⚠️ {model_name}: {error_msg[:100]}")