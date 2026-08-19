# Day 6 — RAG Evaluation

Built a basic evaluation pipeline for measuring RAG retrieval quality.

## Evaluation

Tested:

- Hit@K
- Retrieval performance across different K values
- Retrieval performance across different chunk sizes
- Basic answer groundedness

## Experiment

Compared:

| Chunk Size | Hit@2 |
|---:|---:|
| 100 | 0.000 |
| 300 | 0.750 |
| 500 | 0.500 |

## Key Takeaway

RAG performance depends on retrieval configuration.
Chunk size and Top-K selection can significantly affect
which information reaches the LLM.