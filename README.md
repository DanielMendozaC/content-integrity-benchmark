# Content Integrity Benchmark for LLM Agents

Most agent defenses are measured on **data exfiltration**: can an injection make the agent leak private data. They say nothing about **content integrity**: whether the information the agent reports back is correct. An injection that leaks nothing can still make an agent return a fabricated security code, a phishing link, or the wrong meeting time, through a fully authorized channel.

This benchmark measures that gap. It ships a set of content manipulation attacks, two reference defenses, and an evaluation harness that reports the number a deployer actually cares about: **residual attack success**, the fraction of attacks that both land and evade the defense.

## What is in here

- **Attacks** (`cib/data.py`): 12 single value extraction tasks (dates, times, locations, security codes, URLs, amounts, account numbers, and more). Each comes in two forms:
  - `plain`: the injection carries explicit markers like `[UPDATE]` or "has been changed".
  - `adaptive`: the same manipulation phrased as natural prose with the markers removed.
- **Clean texts** (20): one value each, no injection. A good defense never flags them.
- **Two reference defenses** (`cib/defense.py`):
  - `surface`: pattern matching on injection markers. Cheap, but it detects the attacker's formatting, so an adaptive attacker evades it.
  - `semantic`: dual extraction. Extract twice, once normally and once told to ignore updates, and flag when the two disagree. Reads meaning, survives adaptation, costs two model calls.

## Install

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...   # for claude* models
export OPENAI_API_KEY=...      # for gpt*/o* models
```

## Run

```bash
python run_benchmark.py --model gpt-4o --runs 3
python run_benchmark.py --model claude-sonnet-4-5-20250929
```

Output, per defense, separates the model's own robustness from the defense's work:

- `base_ASR`: did the attack land on the normal extraction (a property of the model).
- `detection`: of the attacks that landed, how many the defense caught.
- `residual_ASR`: landed **and** evaded. The headline. Lower is better.
- `false_positive_rate`: clean texts the defense wrongly flagged.

## Reference results

Semantic defense, adaptive attacks, 3 runs (`results/reference_results.json`):

| Model | Provider | Base ASR | Detection | Residual ASR | Clean FP |
|---|---|---|---|---|---|
| Haiku 4.5 | Anthropic | 100% | 80% | 20% | 2% |
| GPT-4o | OpenAI | 94% | 88% | 11% | 0% |
| Sonnet 4.5 | Anthropic | 100% | 92% | 8% | 0% |
| GPT-5 | OpenAI | 86% | 100% | 0% | 8% |
| Opus 4.8 | Anthropic | 92% | 100% | 0% | 5% |

The attack lands on nearly every model of both providers. The surface defense catches the `plain` attacks fully but collapses on `adaptive` ones. The semantic defense survives, and residual risk falls from about 20 percent on the weakest model to 0 percent on the strongest, across both providers. Anthropic rows are over 10 runs (Haiku std ~4, Sonnet stable); OpenAI rows are 3 runs and will be expanded.

## Bring your own defense or model

A defense is any function that, given the source text and the two extractions, returns whether to flag. See `surface_flag` and `disagree` in `cib/defense.py` and the loop in `cib/evaluate.py`. A model is any id your provider key can call (`claude*` or `gpt*`/`o*`); add other providers in `cib/providers.py`.

## Citing

This benchmark accompanies work on content integrity in LLM agent defenses, first reported as a poster at ACNS 2026 ("Measuring the Non Exfiltration Attack Surface of CaMeL"). A preprint with the full evaluation is forthcoming; a citation will be added here when it is available.

## License

MIT. See `LICENSE`.
