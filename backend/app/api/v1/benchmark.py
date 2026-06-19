import logging
import time
from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from app.intelligence.sentiment import SentimentAnalyzer, get_transformer_pipeline

logger = logging.getLogger("app.api.v1.benchmark")
router = APIRouter(prefix="/intelligence", tags=["Intelligence Benchmark"])


class BenchmarkRequest(BaseModel):
    texts: Optional[List[str]] = None


class ModelStats(BaseModel):
    total_time_ms: float
    avg_time_ms: float


class ModelResult(BaseModel):
    label: str
    score: float
    confidence: float


class BenchmarkResultItem(BaseModel):
    text: str
    heuristic: ModelResult
    transformer: ModelResult


class BenchmarkResponse(BaseModel):
    samples_processed: int
    heuristic: ModelStats
    transformer: ModelStats
    transformer_loaded: bool
    transformer_error: Optional[str]
    results: List[BenchmarkResultItem]


DEFAULT_BENCHMARK_TEXTS = [
    "This product is absolutely amazing! I love using it every day.",
    "The application crashed during checkout and I lost my session. Terrible bug!",
    "Could you please add dark mode and Google SSO integration in the next release?",
    "Where is the invoice history tab in the settings dashboard? I cannot find it.",
    "The service was incredibly slow and laggy, but customer support was very helpful."
]


@router.post("/benchmark", response_model=BenchmarkResponse, summary="Benchmark Sentiment Analysis Models")
async def benchmark_sentiment(request: BenchmarkRequest):
    """Compare performance metrics between heuristic and transformer-based sentiment models."""
    texts = request.texts or DEFAULT_BENCHMARK_TEXTS
    analyzer = SentimentAnalyzer()

    # Make sure transformer is initialized
    pipeline = get_transformer_pipeline()
    from app.intelligence.sentiment import _transformer_load_error
    err_str = _transformer_load_error

    results = []

    # 1. Warm-up run for transformer if loaded
    if pipeline is not None:
        try:
            pipeline("Warm up text")
        except Exception:
            pass

    # 2. Benchmark Heuristic Model
    t0 = time.perf_counter()
    for text in texts:
        analyzer.analyze(text, force_heuristic=True)
    t1 = time.perf_counter()
    heuristic_total = (t1 - t0) * 1000

    # 3. Benchmark Transformer Model
    t0 = time.perf_counter()
    for text in texts:
        analyzer.analyze(text, force_heuristic=False)
    t1 = time.perf_counter()
    transformer_total = (t1 - t0) * 1000

    # 4. Gather detailed labels/scores
    for text in texts:
        heu = analyzer.analyze(text, force_heuristic=True)
        tra = analyzer.analyze(text, force_heuristic=False)

        results.append(BenchmarkResultItem(
            text=text,
            heuristic=ModelResult(label=heu.label, score=heu.score, confidence=heu.confidence),
            transformer=ModelResult(label=tra.label, score=tra.score, confidence=tra.confidence)
        ))

    num_samples = len(texts)
    return BenchmarkResponse(
        samples_processed=num_samples,
        heuristic=ModelStats(
            total_time_ms=round(heuristic_total, 3),
            avg_time_ms=round(heuristic_total / num_samples, 3)
        ),
        transformer=ModelStats(
            total_time_ms=round(transformer_total, 3),
            avg_time_ms=round(transformer_total / num_samples, 3)
        ),
        transformer_loaded=(pipeline is not None),
        transformer_error=err_str,
        results=results
    )
