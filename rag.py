# Mi primer RAG en AWS - AWS Sin Mapa
# Le hace preguntas a una Knowledge Base administrada de Amazon Bedrock.

import boto3

# Cambia esto por el ID de TU Knowledge Base (Bedrock > Bases de conocimientos)
KB_ID = "TU_KNOWLEDGE_BASE_ID"
MODELO = "amazon.nova-lite-v1:0"
REGION = "us-east-1"

kb = boto3.client("bedrock-agent-runtime", region_name=REGION)  # para buscar
ia = boto3.client("bedrock-runtime", region_name=REGION)        # para generar

pregunta = input("¿Qué quieres preguntarle a AWS Sin Mapa? ")

# R - RETRIEVAL (Buscar): traer los pedazos de los documentos que hablan del tema
resultados = kb.retrieve(
    knowledgeBaseId=KB_ID,
    retrievalQuery={"text": pregunta},
)

contexto = ""
fuentes = []
for r in resultados["retrievalResults"]:
    contexto += r["content"]["text"] + "\n\n"
    fuentes.append(r["location"].get("s3Location", {}).get("uri", "desconocida"))

# A - AUGMENTED (Aumentar): juntar la pregunta con la información encontrada
prompt = f"""Responde la pregunta usando SOLO esta información de AWS Sin Mapa.
Si la respuesta no está en la información, di que no lo sabes.

Información:
{contexto}

Pregunta: {pregunta}"""

# G - GENERATION (Generar): el modelo escribe la respuesta
respuesta = ia.converse(
    modelId=MODELO,
    messages=[{"role": "user", "content": [{"text": prompt}]}],
)

print("\nRespuesta:\n")
print(respuesta["output"]["message"]["content"][0]["text"])

print("\nFuentes:")
for f in set(fuentes):
    print("-", f)
