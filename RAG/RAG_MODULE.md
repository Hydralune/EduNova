# GraphRAG 360

> A versatile Retrieval-Augmented-Generation pipeline that turns **any course material**
> – PDF ▪ Word ▪ legacy *.doc* ▪ plain text ▪ even MP4 lectures – into a searchable
> vector database **plus** an auto-generated knowledge graph.

---

## 1  Why GraphRAG 360 ?

1. **Broad-format ingestion**  Automatically handles PDFs, modern *docx*,
   legacy *doc*, and MP4 videos (audio is extracted → Whisper STT → text).
2. **Accurate retrieval**  Texts are chunked with overlap and embedded with a
   state-of-the-art model (`BAAI/bge-large-zh-v1.5` by default).  Combined with
   Chroma DB it yields high-recall semantic search.
3. **Knowledge-graph aware**  Each chunk is sent to an LLM that extracts
   entities & relations and writes a GraphML file – great for curriculum maps
   and downstream analytics.
4. **Pluggable LLM / Embedding**  Remote SiliconFlow endpoints *or* local
   Ollama models can be switched via *.env* – zero code change.
5. **Concurrency & batch tunable**  `LLM_CONCURRENCY`, `CHUNK_SIZE`,
   `EMBED_BATCH_SIZE` let you trade speed vs. cost on the fly.
6. **Self-healing pipeline**  Failed files are logged, removed from the processed
   list and retried next run; `.doc` → PDF conversion and audio extraction are
   wrapped with clear fall-backs.

---

## 2  Directory layout

```
RAG/
 ├─ documents/           # raw course materials organised by course_id
 ├─ data/                # one sub-dir per course – vector DB & graph live here
 ├─ create_db.py         # main entry: build or update a course DB
 ├─ rag_query.py         # query-time RAG chain
 ├─ embedding_util.py    # wraps SiliconFlow embedding API
 └─ ...
```

---

## 3  Setup

```bash
# 1. install deps
conda env create -f environment.yml   # or  pip install -r requirements.txt

# 2. FFmpeg is required for .mp4 -> .wav extraction
choco install -y ffmpeg   # Windows users

# 3. Whisper optional – remote STT is used by default
#    pip install faster-whisper

# 4. environment variables (.env or system)
LLM_API_KEY     = sk-xxx                       # SiliconFlow key
LLM_API_BASE    = https://api.siliconflow.cn/v1
LLM_MODEL       = deepseek-ai/DeepSeek-V3      # remote KG extractor

# optional switches
CHUNK_SIZE      = 1000     # chars per chunk
LLM_CONCURRENCY = 8        # parallel chat calls
LOCAL_KG        = true     # use local Ollama instead of remote
LOCAL_KG_MODEL  = deepseek-r1:7b
FFMPEG_PATH     = C:/Program Files/ffmpeg/bin/ffmpeg.exe
```

---

## 4  Build a course database

```bash
python create_db.py --course_id 003          # initial load
python create_db.py --course_id 003 --rebuild  # force re-scan & graph rebuild
```
Outputs
* `data/003/chroma.sqlite3`   – vector store
* `data/003/knowledge_graph.gml` – entity-relation graph

---

## 5  Query with RAG

```python
from rag_query import ask_course

print(ask_course(course_id="003", query="解释下 Q-Learning 和 SARSA 的区别"))
```
The chain will:
1. identify graph entities in the query → optional graph search
2. vector search top-k chunks
3. feed context into the LLM specified by `LLM_MODEL`

---

## 6  Performance tips

| lever                  | effect                                         |
|------------------------|------------------------------------------------|
| `CHUNK_SIZE`           | bigger → fewer LLM calls; watch token limit    |
| `LLM_CONCURRENCY`      | up to 6 RPS safely on SiliconFlow              |
| `LOCAL_KG=true`        | zero network latency; good for large graphs   |
| Whisper local          | save STT cost, ~1-2× realtime on GPU          |

---

## 7  Road-map

* Caching per-chunk KG extraction results
* Batch upload of audio to SiliconFlow `/batch` API
* Front-end graph visualiser (d3.js)

Contributions & issues welcome! Open a PR or ping us 😄 