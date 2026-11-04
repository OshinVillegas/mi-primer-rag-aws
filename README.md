# 🗺️ Mi primer RAG en AWS — AWS Sin Mapa

> Le enseñé a la IA quién soy: un chat que responde con **mis propios guiones** usando Amazon Bedrock.
> Hecho desde cero, por alguien que recién está aprendiendo. Si yo pude, tú también. 💪

## 🤔 ¿Qué problema resuelve?

Le pregunté a un modelo de IA: *"¿Qué es AWS Sin Mapa?"*. No sabía. Intentó adivinar.

Los modelos solo conocen lo que vieron al entrenarse. **No conocen tu información.**
Un **RAG** soluciona eso: antes de responder, el modelo **busca en tus documentos**.

| Sin RAG | Con RAG |
|---|---|
| "AWS Sin Mapa no es un término reconocido..." | "AWS Sin Mapa es un proyecto creado por una ingeniera de software que..." |

<!-- Agrega aquí tus capturas del "antes" y el "después" -->

## 🧠 ¿Qué es RAG? (explicado fácil)

- **R – Retrieval (Buscar):** busca en tus documentos los pedazos que hablan del tema.
- **A – Augmented (Aumentar):** junta tu pregunta con esos pedazos. Es como darle un machete al modelo antes del examen.
- **G – Generation (Generar):** el modelo lee el machete y escribe la respuesta.

## 🏗️ Arquitectura

```
Tus guiones (.txt) → Amazon S3 → Knowledge Base administrada (Bedrock) → rag.py → Nova Lite → Respuesta + fuentes
```

## 🧰 Servicios que usé

- **Amazon S3:** guarda los documentos.
- **Amazon Bedrock – Knowledge Base administrada:** convierte los documentos en algo que se puede buscar y hace la búsqueda.
- **Amazon Nova Lite:** el modelo que escribe la respuesta (barato y rápido).
- **AWS CloudShell:** la terminal dentro de AWS para ejecutar Python sin instalar nada.

## 🚀 Paso a paso

### 1. Sube tus documentos a S3
1. Abre **S3** → **Crear bucket** (nombre en minúsculas, deja "Bloquear todo el acceso público" activado).
2. Entra al bucket → **Cargar** → sube tus archivos `.txt` (puedes usar los de la carpeta [`documentos/`](documentos/)).

### 2. Crea la Knowledge Base
1. Abre **Amazon Bedrock** → **Bases de conocimientos** → **Crear base de conocimiento administrada**.
2. Origen de datos: **Amazon S3** → elige tu bucket.
3. Deja la configuración recomendada → **Crear**.
4. En **Origen de datos**, marca la casilla y presiona **Sincronizar**.
5. Copia el **ID de la base de conocimiento**.

### 3. Pruébala en la consola
Botón **Probar** → pregunta algo de tus documentos. Fíjate en las citas **[1] [2]**: muestran de dónde salió cada respuesta.

### 4. Ejecuta el código
1. Abre **CloudShell** (abajo a la izquierda en la consola).
2. `nano rag.py` → pega el código de [`rag.py`](rag.py) → cambia `TU_KNOWLEDGE_BASE_ID` por tu ID.
3. Guarda con **Ctrl+O**, **Enter**, **Ctrl+X**.
4. Ejecuta: `python3 rag.py`

## 🧪 Pruebas que hice

| Pregunta | Resultado |
|---|---|
| ¿Qué es AWS Sin Mapa? | ✅ Respondió con mi historia y citó `que-es-aws-sin-mapa.txt` |
| ¿Con qué ejemplo explica AWS Sin Mapa la nube? | ✅ "Netflix vs. comprar un DVD" |
| ¿Qué pasa si llega Juan al equipo? | ✅ Encontró solo el guion de grupos IAM |
| ¿Qué es Amazon EC2? (no está en mis guiones) | ✅ "No lo sé" — no inventó |

## ✅ Buenas prácticas de AI Engineering

- **Mostrar las fuentes:** cada respuesta dice de qué archivo salió, así se puede verificar.
- **Evitar que invente:** el prompt le dice que responda *solo* con la información y que diga "no lo sé" si no la tiene.
- **Mínimo acceso:** el bucket es privado.
- **Medir:** tokens de entrada/salida y latencia (se ven en el Playground de Bedrock).
- **Controlar costos:** presupuesto con alertas en AWS Budgets y etiquetas en los recursos (`proyecto = IA-desde-0`).

## 💸 ¿Cuánto cuesta?

La Knowledge Base administrada cobra por uso (datos guardados y búsquedas), sin un mínimo mensual. Con unos pocos `.txt` el costo es de centavos.
Revisa siempre la [página de precios de Amazon Bedrock](https://aws.amazon.com/bedrock/pricing/).

## 🐞 Errores que tuve (y cómo los resolví)

- **`This operation is not supported for managed knowledge bases`:** `retrieve_and_generate` no funciona con Knowledge Bases administradas. La solución fue separar los pasos: `retrieve` (buscar) + `converse` (generar).
- **`bash: syntax error`:** pegué el código en la terminal en vez de dentro de `nano`. La terminal da órdenes; `nano` es para escribir el código.

## 🔜 Lo que mejoraría

- Las **fuentes** aparecen aunque no se hayan usado (la búsqueda siempre devuelve el resultado más parecido). Se puede filtrar por el **score** de cada resultado.
- Convertirlo en un **agente** que use esta Knowledge Base como herramienta (próximo proyecto).

## 🧹 Cómo borrar todo

1. Bedrock → Bases de conocimientos → elige la tuya → **Eliminar**.
2. S3 → vacía el bucket → **Eliminar** el bucket.

---

Hecho por **Oshin Villegas** como parte de **AWS Sin Mapa · IA desde 0**.
*"Porque para comenzar a aprender, no necesitas tener un mapa."*
