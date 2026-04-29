import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def generar_con_ia(prompt: str) -> str:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "llama3:instruct",
                "prompt": prompt,
                "stream": False
            },
            timeout=300
        )

        response.raise_for_status()

        return response.json().get("response", "Sin respuesta del modelo")

    except Exception as e:
        print("❌ Error con Ollama:", e)
        return "Error generando análisis con IA local"