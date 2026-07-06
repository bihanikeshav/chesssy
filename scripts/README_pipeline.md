# Chess Theory Pipeline

End-to-end pipeline: scrape → classify → embed → ingest into Qdrant.

## Steps

### 1. Install dependencies

```bash
pip install -r scripts/requirements_pipeline.txt
```

### 2. Collect raw theory

Scrapes Wikipedia chess articles and includes the 70 hand-written seed docs.
Outputs `scripts/data/raw_theory.jsonl`.

```bash
python scripts/collect_theory.py
```

### 3. Classify documents

Applies keyword/heuristic rules to assign category, subcategory, difficulty,
and tags to each document.
Outputs `scripts/data/classified_theory.jsonl`.

```bash
python scripts/classify_theory.py
```

### 4. Embed and ingest to Qdrant

Embeds every document with `all-MiniLM-L6-v2` (384-dim), then uploads to
the `chess_theory` Qdrant collection with Cosine distance.

```bash
export QDRANT_URL=https://xxx.qdrant.io:6333
export QDRANT_KEY=your-admin-key
python scripts/embed_ingest.py
```

On Windows (PowerShell):

```powershell
$env:QDRANT_URL = "https://xxx.qdrant.io:6333"
$env:QDRANT_KEY = "your-admin-key"
python scripts/embed_ingest.py
```

## Model

| Setting        | Value                                   |
| -------------- | --------------------------------------- |
| Model          | `all-MiniLM-L6-v2`                      |
| Dimensions     | 384                                     |
| Distance       | Cosine                                  |
| Python package | `sentence-transformers`                 |
| Browser        | `@xenova/transformers` (ONNX, quantized ~8 MB) |

## Frontend (browser)

`static/js/knowledge/qdrant.js` uses Transformers.js loaded from the
jsDelivr CDN to embed queries in the browser using the quantized ONNX version
of the same model, then sends a `/points/search` request to Qdrant with the
resulting 384-dim vector.

- Call `preloadEmbedder()` on app init to warm up the model in the background.
- `getRelevantTheory(positionType, moveTags, queryHint)` is the main entry point.
- Falls back to filter-only scroll if the embedder fails to load.

## Data files

| File                                | Description                        |
| ----------------------------------- | ---------------------------------- |
| `scripts/data/raw_theory.jsonl`     | Raw collected text (seed + Wikipedia) |
| `scripts/data/classified_theory.jsonl` | With category / difficulty / tags  |

Both files are gitignored by convention; regenerate with the steps above.
