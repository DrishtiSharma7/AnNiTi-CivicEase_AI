import json
from pathlib import Path

import pandas as pd


def md_table(df: pd.DataFrame, floatfmt: str = "{:.3f}") -> str:
    if df.empty:
        return "_none_\n"
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(floatfmt.format(v) if isinstance(v, float) else str(v) for v in r) + " |")
    return "\n".join(lines) + "\n"


def write(outdir: Path, name: str, title: str, metrics: dict, gate_rows: list, tables: dict, notes: list = ()) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / f"{name}_metrics.json").write_text(json.dumps(metrics, indent=2, default=float))
    for t, df in tables.items():
        df.to_csv(outdir / f"{name}_{t}.csv", index=False)
    md = [f"# {title}", ""] + [f"> {n}" for n in notes] + ["", "## Acceptance gates", "", md_table(pd.DataFrame(gate_rows))]
    for t, df in tables.items():
        if len(df) <= 60:
            md += [f"## {t.replace('_', ' ').title()}", "", md_table(df)]
    path = outdir / f"{name}_report.md"
    path.write_text("\n".join(md), encoding="utf-8")
    return path
