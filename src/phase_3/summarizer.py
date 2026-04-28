"""
Phase 3: Summarization
Uses LLMs to transform clusters into meaningful themes, action items, and verbatim quotes.
Supports Gemini with automatic failover to Groq if rate limits are hit.
"""

import os
import re
import json
import time
import traceback
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class Quote:
    """A verbatim quote extracted from a review, with its review_id for traceability."""
    text: str
    review_id: str

@dataclass
class ThemeSummary:
    """The LLM-generated summary for a single cluster."""
    cluster_id: int
    theme_name: str
    problem_statement: str
    why_this_matters: str
    impact_level: str                    # "High", "Medium", "Low"
    sentiment: str                       # "positive", "negative", "mixed"
    review_count: int
    product_recommendations: List[str] = field(default_factory=list)
    quotes: List[Quote] = field(default_factory=list)
    who_this_helps: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# PII Safety Gate
# ---------------------------------------------------------------------------

_PII_PATTERNS = [
    re.compile(r'\b[\w.-]+@[\w.-]+\.\w{2,}\b'),                 # email
    re.compile(r'\b(?:\+91[\-\s]?)?[6-9]\d{9}\b'),              # Indian phone
    re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),             # Aadhaar-like
    re.compile(r'\b[A-Z]{5}\d{4}[A-Z]\b'),                      # PAN-like
]


def _contains_pii(text: str) -> bool:
    """Return True if any PII pattern is found."""
    for pat in _PII_PATTERNS:
        if pat.search(text):
            return True
    return False


# ---------------------------------------------------------------------------
# LLM Client Abstraction with Failover
# ---------------------------------------------------------------------------

class LLMClient:
    """
    Unified interface to call Gemini with automatic failover to multiple Groq keys.
    """

    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key_1 = os.getenv("GROQ_API_KEY")
        self.groq_key_2 = os.getenv("GROQ_API_KEY_2")
        self.openai_key = os.getenv("OPENAI_API_KEY")

        if not self.gemini_key and not self.groq_key_1:
            raise EnvironmentError(
                "No primary LLM API keys found. Please set GEMINI_API_KEY or GROQ_API_KEY."
            )

        # Initialize models lazily
        self._gemini_model = None
        self._groq_client_1 = None
        self._groq_client_2 = None
        self._openai_client = None

    def _init_gemini(self):
        if self._gemini_model is None and self.gemini_key:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_key)
            self._gemini_model = genai.GenerativeModel("gemini-2.0-flash")

    def _init_groq(self, key_num=1):
        if key_num == 1 and self._groq_client_1 is None and self.groq_key_1:
            from groq import Groq
            self._groq_client_1 = Groq(api_key=self.groq_key_1)
        elif key_num == 2 and self._groq_client_2 is None and self.groq_key_2:
            from groq import Groq
            self._groq_client_2 = Groq(api_key=self.groq_key_2)

    def _init_openai(self):
        if self._openai_client is None and self.openai_key:
            import openai
            self._openai_client = openai.OpenAI(api_key=self.openai_key)

    def _call_groq(self, prompt: str, key_num: int) -> str:
        self._init_groq(key_num)
        client = self._groq_client_1 if key_num == 1 else self._groq_client_2
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a product analyst."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
        )
        return chat_completion.choices[0].message.content.strip()

    def generate(self, prompt: str) -> str:
        """
        Attempts to generate content using Gemini -> Groq 1 -> Groq 2.
        """
        # 1. Try Gemini
        if self.gemini_key:
            try:
                self._init_gemini()
                response = self._gemini_model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                print(f"  [LLM] Gemini failed, trying Groq Key 1...")

        # 2. Try Groq Key 1
        if self.groq_key_1:
            try:
                return self._call_groq(prompt, 1)
            except Exception as e:
                if self.groq_key_2:
                    print(f"  [LLM] Groq Key 1 failed, trying Groq Key 2...")
                else:
                    print(f"  [LLM] Groq Key 1 failed: {e}")

        # 3. Try Groq Key 2
        if self.groq_key_2:
            try:
                return self._call_groq(prompt, 2)
            except Exception as e:
                print(f"  [LLM] Groq Key 2 failed: {e}")

        raise RuntimeError("All LLM providers (Gemini, Groq 1, Groq 2) failed or are not configured.")


# ---------------------------------------------------------------------------
# Prompt Design
# ---------------------------------------------------------------------------

CLUSTER_SUMMARY_PROMPT = """You are a senior Product Manager and UX content designer for a fintech app called "{product_name}".

Below are {review_count} user reviews that belong to the same thematic cluster. Your job is to transform this raw feedback into a highly polished, stakeholder-ready insight.

**Reviews:**
{reviews_block}

**Instructions — respond ONLY with valid JSON, no markdown fences:**
{{
  "theme_name": "<short, descriptive theme name, max 6 words>",
  "problem_statement": "<Clear, concise 1-2 sentence problem statement summarizing the user pain point or praise>",
  "why_this_matters": "<1-2 sentences explaining the business or UX impact (e.g., churn, revenue, trust)>",
  "impact_level": "<High | Medium | Low>",
  "sentiment": "<positive | negative | mixed>",
  "product_recommendations": [
    "<concrete, product-focused recommendation 1>",
    "<concrete, product-focused recommendation 2>"
  ],
  "quotes": [
    {{"text": "<exact verbatim quote from one review>", "review_id": "<review_id>"}},
    {{"text": "<exact verbatim quote from another review>", "review_id": "<review_id>"}},
    {{"text": "<exact verbatim quote from another review>", "review_id": "<review_id>"}}
  ],
  "who_this_helps": ["<team or role, e.g. Product, Engineering, Support, Finance>"]
}}

**Rules:**
1. The "quotes" MUST be exact, verbatim substrings from the reviews above. Do NOT paraphrase.
2. Each quote must include the correct review_id from the data.
3. If you detect any PII (emails, phone numbers, national IDs) in a quote, replace it with [REDACTED].
4. Provide exactly 3 quotes if possible. If the cluster has fewer than 3 reviews, provide as many as available.
5. Provide 1-3 concrete product recommendations.
"""


# ---------------------------------------------------------------------------
# Quote Validation
# ---------------------------------------------------------------------------

def _validate_quotes(
    quotes: List[Dict[str, str]],
    reviews_lookup: Dict[str, str],
) -> List[Quote]:
    """
    Validate that each quote actually exists in the original review text.
    Only keeps quotes that are verified verbatim substrings.
    """
    validated: List[Quote] = []
    for q in quotes:
        text = q.get("text", "")
        rid = q.get("review_id", "")

        if _contains_pii(text):
            for pat in _PII_PATTERNS:
                text = pat.sub("[REDACTED]", text)

        original_review = reviews_lookup.get(rid, "")
        raw_text = q.get("text", "")
        if raw_text and raw_text in original_review:
            validated.append(Quote(text=text, review_id=rid))
        else:
            found = False
            for r_id, r_content in reviews_lookup.items():
                if raw_text and raw_text in r_content:
                    validated.append(Quote(text=text, review_id=r_id))
                    found = True
                    break
            if not found:
                # Still add it but strip PII as a precaution
                pass

    return validated


# ---------------------------------------------------------------------------
# Core Summarization Pipeline
# ---------------------------------------------------------------------------

def summarize_cluster(
    cluster_id: int,
    reviews: List[Dict[str, str]],
    llm: LLMClient,
    product_name: str = "Groww",
) -> Optional[ThemeSummary]:
    """
    Summarize a single cluster using the LLM with failover logic.
    """
    if not reviews:
        return None

    reviews_block_lines = []
    reviews_lookup: Dict[str, str] = {}
    for r in reviews:
        rid = r["review_id"]
        content = r["content"]
        reviews_lookup[rid] = content
        display = content[:500] if len(content) > 500 else content
        reviews_block_lines.append(f"[review_id={rid}] {display}")

    reviews_block = "\n".join(reviews_block_lines)

    prompt = CLUSTER_SUMMARY_PROMPT.format(
        product_name=product_name,
        review_count=len(reviews),
        reviews_block=reviews_block,
    )

    try:
        raw_response = llm.generate(prompt)

        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)

        result = json.loads(cleaned)

        raw_quotes = result.get("quotes", [])
        validated_quotes = _validate_quotes(raw_quotes, reviews_lookup)

        return ThemeSummary(
            cluster_id=cluster_id,
            theme_name=result.get("theme_name", f"Cluster {cluster_id}"),
            problem_statement=result.get("problem_statement", ""),
            why_this_matters=result.get("why_this_matters", ""),
            impact_level=result.get("impact_level", "Medium"),
            sentiment=result.get("sentiment", "mixed"),
            review_count=len(reviews),
            product_recommendations=result.get("product_recommendations", []),
            quotes=validated_quotes,
            who_this_helps=result.get("who_this_helps", []),
        )

    except Exception as e:
        print(f"  [ERROR] Cluster {cluster_id} summarization failed: {e}")
        return None


def run_summarization_pipeline(
    clustered_df,
    product_name: str = "Groww",
    max_reviews_per_cluster: int = 50,
    max_clusters: int = 7,
) -> List[ThemeSummary]:
    """
    Run the full summarization pipeline over clustered review data.

    Args:
        clustered_df: A pandas DataFrame from Phase 2 with columns
                      ['review_id', 'content', 'cluster'].
        product_name: Product name for prompt context.
        max_reviews_per_cluster: Cap reviews sent to LLM per cluster.
        max_clusters: Max number of clusters to summarize (Top N by size).
    """
    if clustered_df is None or clustered_df.empty:
        print("No clustered data to summarize.")
        return []

    llm = LLMClient()

    from concurrent.futures import ThreadPoolExecutor, as_completed

    # Get unique non-noise clusters, sorted by size (largest first)
    cluster_ids = (
        clustered_df[clustered_df['cluster'] != -1]['cluster']
        .value_counts()
        .index.tolist()
    )

    # Limit to top N clusters to control cost/calls
    cluster_ids = cluster_ids[:max_clusters]

    print(f"\n--- Phase 3: Summarizing Top {len(cluster_ids)} clusters ---")

    summaries: List[ThemeSummary] = []
    
    def process_cluster(cluster_id):
        subset = clustered_df[clustered_df['cluster'] == cluster_id]
        review_count = len(subset)

        if review_count > max_reviews_per_cluster:
            subset = subset.sample(n=max_reviews_per_cluster, random_state=42)

        reviews = [
            {"review_id": row["review_id"], "content": row["content"]}
            for _, row in subset.iterrows()
        ]

        print(f"  Processing Cluster {cluster_id} ({review_count} reviews)...")

        summary = summarize_cluster(
            cluster_id=cluster_id,
            reviews=reviews,
            llm=llm,
            product_name=product_name,
        )
        if summary:
            summary.review_count = review_count
        return cluster_id, summary

    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_cluster = {executor.submit(process_cluster, cid): cid for cid in cluster_ids}
        for future in as_completed(future_to_cluster):
            cid = future_to_cluster[future]
            try:
                _, summary = future.result()
                if summary:
                    summaries.append(summary)
                    try:
                        theme_disp = summary.theme_name.encode('ascii', 'ignore').decode('ascii')
                        print(f"    -> Theme: \"{theme_disp}\"")
                    except:
                        print(f"    -> Theme identified for Cluster {cid}")
                else:
                    print(f"    -> Skipped Cluster {cid} (LLM error)")
            except Exception as exc:
                print(f"    -> Cluster {cid} generated an exception: {exc}")

    print(f"\n--- Summarization complete: {len(summaries)}/{len(cluster_ids)} summarized ---")
    return summaries
