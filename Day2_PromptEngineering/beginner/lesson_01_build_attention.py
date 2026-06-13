"""
╔══════════════════════════════════════════════════════════════════╗
║  LESSON 1 — BEGINNER: Build Attention From Scratch              ║
║  Topic: Transformer Internals + Prompt Anatomy                  ║
╚══════════════════════════════════════════════════════════════════╝

You will BUILD the core attention mechanism step-by-step in code,
then call Gemini's API to observe the same effect in a real model.

Run: python lesson_01_build_attention.py
Prereq: pip install google-generativeai numpy
"""

import os, math, json, re
import numpy as np

# ─────────────────────────────────────────────────────────────────
# PART 1 ▶ Implement Scaled Dot-Product Attention
# ─────────────────────────────────────────────────────────────────
# Formula: Attention(Q, K, V) = softmax( Q·Kᵀ / √dₖ ) · V
#
# Think of it as a soft database lookup:
#   Q = what you're searching for
#   K = the index of every token
#   V = the actual content of every token

def softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max())          # subtract max for numerical stability
    return e / e.sum()

def attention(Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> tuple:
    """
    Q: (seq_len, d_k)
    K: (seq_len, d_k)
    V: (seq_len, d_v)
    Returns: (output, attention_weights)
    """
    d_k = K.shape[-1]
    scores = Q @ K.T / math.sqrt(d_k)       # (seq_len, seq_len)
    weights = np.apply_along_axis(softmax, 1, scores)   # row-wise softmax
    output = weights @ V                     # (seq_len, d_v)
    return output, weights


# ── EXERCISE 1A: Attend over a 4-token sentence ──────────────────
np.random.seed(42)
tokens = ["[SYS]", "get_weather", "location=Paris", "[USER]"]
d_k    = 4

# Each token has a random embedding — in real transformers
# these come from learned projection matrices W_Q, W_K, W_V
K = np.random.randn(len(tokens), d_k)
V = np.random.randn(len(tokens), d_k)
Q = np.random.randn(len(tokens), d_k)

output, weights = attention(Q, K, V)

print("╔══════════════════════════════════════════════════════════╗")
print("║  EXERCISE 1A: Attention Weight Matrix                   ║")
print("╚══════════════════════════════════════════════════════════╝")
print(f"\n  Tokens: {tokens}\n")
print("  Each row shows what % attention each token pays to others:")
print(f"  {'':15}", " ".join(f"{t:>15}" for t in tokens))
for i, row_token in enumerate(tokens):
    bar_row = " ".join(f"{w:>15.3f}" for w in weights[i])
    print(f"  {row_token:>15}  {bar_row}")

print("\n  [Key insight]: The [SYS] token heavily influences the")
print("  'get_weather' token — just like in a real system prompt.\n")


# ─────────────────────────────────────────────────────────────────
# PART 2 ▶ Multi-Head Attention — Why Multiple Heads?
# ─────────────────────────────────────────────────────────────────
# A single attention head can only capture ONE type of relationship.
# Multiple heads capture: syntax, semantics, coreference, format…

def multi_head_attention(X: np.ndarray, num_heads: int, d_model: int) -> np.ndarray:
    """
    X: (seq_len, d_model)
    Splits d_model into num_heads sub-spaces, runs attention in each,
    then concatenates results.
    """
    assert d_model % num_heads == 0
    d_k = d_model // num_heads
    outputs = []

    np.random.seed(0)
    for head in range(num_heads):
        # Each head has its own learned projections
        W_Q = np.random.randn(d_model, d_k) * 0.1
        W_K = np.random.randn(d_model, d_k) * 0.1
        W_V = np.random.randn(d_model, d_k) * 0.1

        Q = X @ W_Q
        K = X @ W_K
        V = X @ W_V
        out, _ = attention(Q, K, V)
        outputs.append(out)

    # Concatenate all head outputs
    return np.concatenate(outputs, axis=-1)   # (seq_len, d_model)


# ── EXERCISE 1B: Run multi-head attention ────────────────────────
seq_len = 4
d_model = 8
X = np.random.randn(seq_len, d_model)

mha_output = multi_head_attention(X, num_heads=2, d_model=d_model)

print("╔══════════════════════════════════════════════════════════╗")
print("║  EXERCISE 1B: Multi-Head Attention Output Shape         ║")
print("╚══════════════════════════════════════════════════════════╝")
print(f"\n  Input  shape : {X.shape}    (seq_len=4, d_model=8)")
print(f"  Output shape : {mha_output.shape}  (same — heads split then recombine)\n")
print("  First token's MHA output vector:")
print("  ", np.round(mha_output[0], 4))
print()


# ─────────────────────────────────────────────────────────────────
# PART 3 ▶ Real API — System Prompt as an Attention Map
# ─────────────────────────────────────────────────────────────────
# Now see how the system prompt you write directly controls
# which tokens the model "pays attention to" when generating.

def call_gemini(system_prompt: str, user_msg: str, api_key: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-1.5-flash",
        system_instruction=system_prompt
    )
    return model.generate_content(user_msg).text.strip()


# ── EXERCISE 1C: Two extremes — vague vs. structured prompt ──────
VAGUE = "You are a helpful assistant."
STRUCTURED = (
    "You are a tool-calling agent.\n"
    "TASK: Output ONLY valid JSON for tool calls. No prose.\n\n"
    "FORMAT:\n"
    '{"tool":"get_weather","parameters":{"location":"<city>","unit":"celsius"}}\n\n'
    "RULE: If user asks about weather → call get_weather. Otherwise say 'N/A'."
)

USER_MSG = "What is the weather in Paris?"

api_key = os.environ.get("GEMINI_API_KEY", "")
if api_key:
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  EXERCISE 1C: Vague vs Structured Prompt (Gemini API)   ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"\n  User: {USER_MSG}\n")

    r_vague = call_gemini(VAGUE, USER_MSG, api_key)
    print(f"  [VAGUE prompt response]\n  {r_vague[:300]}\n")

    r_structured = call_gemini(STRUCTURED, USER_MSG, api_key)
    print(f"  [STRUCTURED prompt response]\n  {r_structured[:300]}\n")

    print("  → Structured prompt forces attention onto the JSON format tokens.")
    print("  → Vague prompt leaves the model free to attend to conversational patterns.\n")
else:
    print("  [!] Set GEMINI_API_KEY env var to run Exercise 1C\n")

# ─────────────────────────────────────────────────────────────────
# CODING CHALLENGES — try these yourself
# ─────────────────────────────────────────────────────────────────
print("""
╔══════════════════════════════════════════════════════════════╗
║  CODING CHALLENGES                                          ║
╠══════════════════════════════════════════════════════════════╣
║  1. Modify the attention() function to add a MASK that      ║
║     prevents tokens from attending to future tokens         ║
║     (causal / autoregressive masking).                      ║
║     Hint: Use np.tril(np.ones(...)) to create the mask.     ║
║                                                             ║
║  2. Change d_k in Exercise 1A to 1 and 64. Observe how     ║
║     attention scores become spiky (1) or flat (64).         ║
║     Why does √dₖ matter?                                    ║
║                                                             ║
║  3. In Exercise 1C: add 5 irrelevant policy sentences to    ║
║     the STRUCTURED prompt. Does compliance drop?            ║
╚══════════════════════════════════════════════════════════════╝
""")
