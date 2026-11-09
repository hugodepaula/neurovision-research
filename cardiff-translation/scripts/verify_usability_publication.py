"""Check public artifacts against a private export without printing private values."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
from analyze_usability import private_file

def verify(private_export, artifacts):
    data=json.loads(private_export.read_text())
    protected=set()
    for row in data['data']['submissions']:
        for a in row['answers']:
            t=str(a.get('text_response') or '').strip()
            if a.get('caption') in {'QS1','QS3'} and len(t)>=5 and t.casefold() not in {'n/a','nenhum','nenhuma'}:
                protected.add(t)
            if a.get('caption')=='F2' and len(t)>=40:protected.add(t)
    problems=[]
    for p in artifacts:
        if not p.is_file():continue
        if p.suffix in {'.png','.pdf'}:continue  # PDFs are independently checked using extracted text.
        try:text=p.read_text()
        except UnicodeDecodeError:continue
        if any(t in text for t in protected):problems.append('private_text')
        if re.search(r'"submissions"\s*:\s*\[',text):problems.append('response_export')
        if re.search(r'"labels_by_submission_id"\s*:\s*\{\s*"\d+"',text):problems.append('individual_review')
    if problems:raise ValueError(f'Publication verification failed ({len(problems)} findings); inspect locally. No private values printed.')
    return len(protected)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--input',required=True,type=Path);ap.add_argument('artifacts',nargs='+',type=Path);args=ap.parse_args()
    files=[]
    for p in args.artifacts:files.extend(p.rglob('*') if p.is_dir() else [p])
    count=verify(private_file(args.input),files)
    print(f'Privacy scan passed for {len(files)} paths against {count} protected strings. Inspect aggregate schemas and PDF text separately.')
if __name__=='__main__':main()
