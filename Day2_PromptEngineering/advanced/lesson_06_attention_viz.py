"""
╔══════════════════════════════════════════════════════════════════╗
║  LESSON 6 — ADVANCED: Attention Visualization with PyTorch      ║
║  Topic: Inspect Real Self-Attention Maps (GPT-2)                ║
╚══════════════════════════════════════════════════════════════════╝

You will:
  1. Load GPT-2 locally using HuggingFace Transformers
  2. Run your 5 prompt variants through it
  3. Extract and visualize self-attention weight matrices per layer
  4. Compare how each prompt structure concentrates attention
     on tool-relevant tokens vs. distractor tokens

Run: python lesson_06_attention_viz.py
Prereq: pip install transformers torch matplotlib seaborn
"""

import math, json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# ─────────────────────────────────────────────────────────────────
# STEP 1 ▶ Define 5 Prompt Strings for GPT-2 to Process
# ─────────────────────────────────────────────────────────────────
# Note: GPT-2 doesn't follow instructions, but we can observe
# HOW it distributes attention across different prompt structures.
# That mechanism is IDENTICAL to modern LLMs.

PROMPTS = {
    "Barebones":    "Agent: call get_weather for Paris. User: weather Paris?",
    "FewShot":      'Example: {"tool":"get_weather","location":"London"}\nUser: weather Paris?',
    "ChainOfThought":"Think: need weather tool. Step: call get_weather. User: weather Paris?",
    "XMLDelimited": "<tool>get_weather</tool><location>Paris</location> User: weather Paris?",
    "Diluted":      "Note1: check email. Note2: backup files. Note3: call get_weather for Paris. Note4: greet user. User: weather Paris?",
}

# ─────────────────────────────────────────────────────────────────
# STEP 2 ▶ Utility: Compute Attention Statistics
# ─────────────────────────────────────────────────────────────────

def entropy(weights: np.ndarray) -> float:
    """Shannon entropy of attention distribution. Lower = more focused."""
    w = np.clip(weights, 1e-10, 1.0)
    return float(-np.sum(w * np.log2(w)))

def tool_token_weight(attn_row: np.ndarray, tokens: list) -> float:
    """Sum of attention weights on tokens containing tool-relevant words."""
    keywords = {"get", "weather", "tool", "call", "location", "<", ">", "{", "}"}
    weight = 0.0
    for i, t in enumerate(tokens):
        if any(k in t.lower() for k in keywords):
            weight += attn_row[i]
    return float(weight)

# ─────────────────────────────────────────────────────────────────
# STEP 3 ▶ Build Attention Heatmap for One Prompt
# ─────────────────────────────────────────────────────────────────

def get_attention_map(model, tokenizer, text: str, layer: int = -1):
    """
    Returns:
      tokens      : list of token strings
      mean_attn   : (seq_len, seq_len) array averaged over heads
    """
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        out = model(**inputs)

    # attentions: tuple of (batch, heads, seq, seq) per layer
    attn = out.attentions[layer][0]        # (heads, seq, seq)
    mean_attn = attn.mean(dim=0).cpu().numpy()  # (seq, seq)
    tokens = [tokenizer.decode([i]) for i in inputs["input_ids"][0]]
    return tokens, mean_attn

# ─────────────────────────────────────────────────────────────────
# STEP 4 ▶ Visualise All 5 Variants Side-by-Side
# ─────────────────────────────────────────────────────────────────

def plot_comparison(all_data: dict, save_path: str = "attention_comparison.png"):
    n = len(all_data)
    fig = plt.figure(figsize=(5 * n, 5), facecolor="#0f172a")
    gs  = gridspec.GridSpec(1, n, figure=fig, hspace=0.4, wspace=0.5)

    for idx, (name, (tokens, mean_attn)) in enumerate(all_data.items()):
        ax = fig.add_subplot(gs[0, idx])
        # Show last token's attention (what the model attends to when generating next)
        row = mean_attn[-1]
        # Trim tokens to fit chart
        display_tokens = [t[:6] for t in tokens]
        ax.barh(range(len(row)), row[::-1], color="#38bdf8", alpha=0.85)
        ax.set_yticks(range(len(row)))
        ax.set_yticklabels(display_tokens[::-1], fontsize=7, color="white")
        ax.set_title(name.replace("_"," "), color="#38bdf8", fontsize=9, pad=8)
        ax.set_facecolor("#1e293b")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_edgecolor("#334155")

    fig.suptitle("Last-Token Attention Distribution per Prompt Variant (GPT-2, Final Layer)",
                 color="white", fontsize=11, y=1.02)
    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  [+] Saved: {save_path}")

# ─────────────────────────────────────────────────────────────────
# STEP 5 ▶ Print Metrics Table
# ─────────────────────────────────────────────────────────────────

def print_metrics(all_data: dict):
    print(f"\n  {'Variant':<20}  {'Entropy':>10}  {'Tool Attn%':>12}  {'Tokens':>8}")
    print(f"  {'─'*60}")
    for name, (tokens, mean_attn) in all_data.items():
        last_row = mean_attn[-1]
        ent      = entropy(last_row)
        tw       = tool_token_weight(last_row, tokens) * 100
        print(f"  {name:<20}  {ent:>10.3f}  {tw:>11.1f}%  {len(tokens):>8}")
    print()

# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def run():
    MODEL_NAME = "gpt2"
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  LESSON 6: SELF-ATTENTION VISUALISATION (GPT-2 Local Model)     ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"\n  Loading model '{MODEL_NAME}' locally (no API key needed)...")

    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model     = AutoModelForCausalLM.from_pretrained(MODEL_NAME, output_attentions=True)
        model.eval()
    except Exception as e:
        print(f"  [Error] Could not load model: {e}")
        print("  Run: pip install transformers torch")
        return

    print("  [+] Model loaded. Extracting attention maps...\n")
    all_data = {}

    for name, text in PROMPTS.items():
        tokens, mean_attn = get_attention_map(model, tokenizer, text)
        all_data[name] = (tokens, mean_attn)
        print(f"  [+] Processed: {name:<20}  ({len(tokens)} tokens)")

    # ── Metrics table ──
    print_metrics(all_data)

    # ── Side-by-side visualisation ──
    print("  [+] Generating attention comparison chart...")
    plot_comparison(all_data, save_path="attention_comparison.png")

    # ── Individual heatmaps ──
    for name, (tokens, mean_attn) in all_data.items():
        fig, ax = plt.subplots(figsize=(8, 6), facecolor="#0f172a")
        n = min(len(tokens), 20)  # cap for readability
        sns.heatmap(mean_attn[:n, :n],
                    xticklabels=[t[:8] for t in tokens[:n]],
                    yticklabels=[t[:8] for t in tokens[:n]],
                    cmap="rocket", ax=ax, cbar=True, linewidths=0.3)
        ax.set_title(f"Attention Heatmap — {name}", color="#38bdf8", pad=12)
        ax.set_facecolor("#1e293b")
        plt.xticks(color="white", fontsize=7, rotation=45, ha="right")
        plt.yticks(color="white", fontsize=7)
        plt.tight_layout()
        fname = f"heatmap_{name.lower()}.png"
        plt.savefig(fname, dpi=120, facecolor=fig.get_facecolor())
        plt.close()
        print(f"  [+] Saved heatmap: {fname}")

    print("""
╔══════════════════════════════════════════════════════════════╗
║  HOW TO READ THE OUTPUT                                     ║
╠══════════════════════════════════════════════════════════════╣
║  ENTROPY (lower = more focused):                            ║
║    • Low entropy → model strongly focused on specific tokens║
║    • High entropy → attention spread thin across all tokens ║
║                                                             ║
║  TOOL ATTENTION %:                                          ║
║    • % of attention budget going to tool-relevant tokens   ║
║    • Higher % = better structured prompt for tool calling  ║
╠══════════════════════════════════════════════════════════════╣
║  CODING CHALLENGES                                          ║
╠══════════════════════════════════════════════════════════════╣
║  1. Repeat for LAYER 0 vs LAYER 11. Does early layer        ║
║     attention differ from late layer attention?             ║
║                                                             ║
║  2. Add a causal mask to the heatmap (lower triangle only). ║
║     This is what real decoder models actually compute.      ║
║                                                             ║
║  3. Compare INDIVIDUAL HEADS instead of the mean.          ║
║     Plot head 0 vs head 4 — what patterns differ?          ║
╚══════════════════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    run()
