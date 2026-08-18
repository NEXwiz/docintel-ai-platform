"""
RAGAS Evaluation Harness for Docintel AI Platform.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.run_config import RunConfig
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

GOLDEN_DATASET_PATH = os.path.join(os.path.dirname(__file__), "golden_dataset.json")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "results.json")
SCORE_THRESHOLD = float(os.getenv("RAGAS_THRESHOLD", "0.7"))
USE_LIVE_PIPELINE = os.getenv("EVAL_LIVE", "false").lower() == "true"


def load_golden_dataset():
    with open(GOLDEN_DATASET_PATH, "r") as f:
        data = json.load(f)
    return data


def get_live_answer(question):
    """Call the actual Docintel RAG pipeline directly."""
    from app.ai.retrieval import RetrievalService
    from app.ai.llm import LLMService

    retrieval = RetrievalService()
    llm = LLMService()

    # Use user_id=1 for eval (assumes test data exists)
    chunks = retrieval.search(query=question, user_id=1, limit=5)
    context = "\n\n".join(chunks)
    answer = llm.generate_answer(query=question, context=context)
    return answer, chunks


def build_eval_dataset(golden_data):
    questions = []
    answers = []
    contexts = []
    ground_truths = []

    for item in golden_data:
        questions.append(item["question"])
        ground_truths.append(item["ground_truth"])

        if USE_LIVE_PIPELINE:
            answer, retrieved_contexts = get_live_answer(item["question"])
            answers.append(answer)
            contexts.append(retrieved_contexts)
        else:
            contexts.append(item["contexts"])
            answers.append(item["ground_truth"])

    return Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    })


def run_evaluation():
    golden_data = load_golden_dataset()
    dataset = build_eval_dataset(golden_data)

    llm = LangchainLLMWrapper(ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
    ))
    embeddings = LangchainEmbeddingsWrapper(HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
    ))

    metrics = [faithfulness, answer_relevancy, context_precision, context_recall]

    result = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=llm,
        embeddings=embeddings,
        run_config=RunConfig(timeout=180, max_retries=10, max_workers=1),
    )

    scores = {}
    for row in result.scores:
        for k, v in row.items():
            if isinstance(v, (int, float)):
                scores.setdefault(k, []).append(v)
    scores = {k: round(sum(v) / len(v), 4) for k, v in scores.items()}
    scores["passed"] = all(v >= SCORE_THRESHOLD for k, v in scores.items() if k not in ("passed", "threshold"))
    scores["threshold"] = SCORE_THRESHOLD

    with open(RESULTS_PATH, "w") as f:
        json.dump(scores, f, indent=2)

    print("\n=== RAGAS Evaluation Results ===")
    for metric, score in scores.items():
        if metric in ("passed", "threshold"):
            continue
        status = "PASS" if score >= SCORE_THRESHOLD else "FAIL"
        print(f"  {metric}: {score:.4f} [{status}]")
    print(f"\n  Threshold: {SCORE_THRESHOLD}")
    print(f"  Overall: {'PASSED' if scores['passed'] else 'FAILED'}")

    return scores


if __name__ == "__main__":
    scores = run_evaluation()
    if not scores["passed"]:
        sys.exit(1)
