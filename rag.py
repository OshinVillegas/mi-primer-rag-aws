"""RAG sobre una Knowledge Base administrada de Amazon Bedrock.

Flujo:
  1. Retrieval:  bedrock-agent-runtime.retrieve() busca los fragmentos relevantes.
  2. Augmented:  se arma un prompt con la pregunta y los fragmentos.
  3. Generation: bedrock-runtime.converse() genera la respuesta con Amazon Nova Lite.

Nota: RetrieveAndGenerate no es compatible con Knowledge Bases administradas,
por eso la búsqueda y la generación se hacen en dos llamadas separadas.

Configuración por variables de entorno:
  KB_ID      ID de la Knowledge Base (obligatorio)
  MODEL_ID   Modelo de Bedrock (por defecto: amazon.nova-lite-v1:0)
  AWS_REGION Región (por defecto: us-east-1)
  MIN_SCORE  Puntaje mínimo de un fragmento para usarlo (por defecto: 0, sin filtro)

Uso:
  KB_ID=XXXXXXXXXX python3 rag.py
  KB_ID=XXXXXXXXXX python3 rag.py "¿Qué es AWS Sin Mapa?"
"""

import os
import sys

import boto3

KB_ID = os.getenv("KB_ID", "TU_KNOWLEDGE_BASE_ID")
MODEL_ID = os.getenv("MODEL_ID", "amazon.nova-lite-v1:0")
REGION = os.getenv("AWS_REGION", "us-east-1")
MIN_SCORE = float(os.getenv("MIN_SCORE", "0"))

PROMPT = """Responde la pregunta usando SOLO esta información de AWS Sin Mapa.
Si la respuesta no está en la información, di que no lo sabes.

Información:
{contexto}

Pregunta: {pregunta}"""

kb = boto3.client("bedrock-agent-runtime", region_name=REGION)
ia = boto3.client("bedrock-runtime", region_name=REGION)


def buscar(pregunta):
    """R - Retrieval: devuelve los fragmentos relevantes y sus fuentes."""
    resultados = kb.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalQuery={"text": pregunta},
    )["retrievalResults"]
    fragmentos = [r for r in resultados if r.get("score", 0) >= MIN_SCORE]
    contexto = "\n\n".join(r["content"]["text"] for r in fragmentos)
    fuentes = sorted({
        r["location"].get("s3Location", {}).get("uri", "desconocida") for r in fragmentos
    })
    return contexto, fuentes


def generar(pregunta, contexto):
    """A + G - Augmented Generation: arma el prompt y genera la respuesta."""
    respuesta = ia.converse(
        modelId=MODEL_ID,
        messages=[{
            "role": "user",
            "content": [{"text": PROMPT.format(contexto=contexto, pregunta=pregunta)}],
        }],
    )
    texto = respuesta["output"]["message"]["content"][0]["text"]
    return texto, respuesta.get("usage", {})


def main():
    pregunta = " ".join(sys.argv[1:]) or input("¿Qué quieres preguntarle a AWS Sin Mapa? ")
    contexto, fuentes = buscar(pregunta)
    texto, uso = generar(pregunta, contexto)

    print("\nRespuesta:\n")
    print(texto)
    print("\nFuentes:")
    for f in fuentes:
        print("-", f)
    if uso:
        print(f"\nTokens: entrada {uso.get('inputTokens')} · salida {uso.get('outputTokens')}")


if __name__ == "__main__":
    main()
