"""Validation intégrée des artefacts reproductibles de la séquence 1."""
import csv, hashlib, os, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ENV = os.environ | {"PYTHONPATH": str(ROOT / "src")}
def run(*args): subprocess.run([sys.executable, *map(str,args)], cwd=ROOT, env=ENV, check=True)
def main():
    sample=ROOT/"data/samples/batch001_messages.jsonl"
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory); raw=tmp/"raw.jsonl"; table=tmp/"data.csv"; chart=tmp/"chart.png"
        run("-m","iot_decision.baseline_cli","extract-sample",sample,raw)
        
        import difflib

        raw_text = raw.read_text(encoding="utf-8")
        sample_text = sample.read_text(encoding="utf-8")

        print("=== SAMPLE ===")
        print(sample_text)

        print("=== RAW ===")
        print(raw_text)

        print("=== DIFF ===")
        print(
            "".join(    
                difflib.unified_diff(
                    sample_text.splitlines(keepends=True),
                    raw_text.splitlines(keepends=True),
                    fromfile="sample",
                    tofile="raw",
                )
            )
        )

        run("-m","iot_decision.baseline_cli","transform",raw,table)
        run("-m","iot_decision.visualize_baseline",table,chart)
        assert hashlib.sha256(raw.read_bytes()).digest()==hashlib.sha256(sample.read_bytes()).digest()
        with table.open(encoding="utf-8",newline="") as stream: rows=list(csv.DictReader(stream))
        assert len(rows)==15 and len({r["zone"] for r in rows})==5
        assert max(float(r["value"]) for r in rows)==35.4 and chart.stat().st_size>10000
        notebook=ROOT/"notebooks/s01_baseline_pipeline.ipynb"
        code=("import nbformat; from nbclient import NotebookClient; "+f"n=nbformat.read(r'{notebook}',as_version=4); "+"NotebookClient(n,timeout=120,kernel_name='python3').execute()")
        run("-c",code)
    print("S01 valide: données, pipeline, figure et notebook exécutables.")
if __name__=="__main__": main()
