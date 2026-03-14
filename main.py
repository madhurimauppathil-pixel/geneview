from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os

from models import Sequence, get_db
from parser import parse_fasta, parse_csv, find_mutations, find_exons, calc_gc
from ncbi   import search_gene, fetch_by_accession

app = FastAPI(title="DNA Sequence Viewer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/images", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/upload")
async def upload_sequence(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = (await file.read()).decode("utf-8")
    if file.filename.endswith(".fasta") or file.filename.endswith(".fa"):
        sequences = parse_fasta(content)
    elif file.filename.endswith(".csv"):
        sequences = parse_csv(content)
    else:
        raise HTTPException(status_code=400, detail="Only .fasta or .csv files supported")
    saved = []
    for seq in sequences:
        record = Sequence(name=seq["name"], sequence=seq["sequence"])
        db.add(record)
        db.commit()
        db.refresh(record)
        seq["db_id"] = record.id
        saved.append(seq)
    return {"sequences": saved}

@app.get("/sequences")
def get_sequences(db: Session = Depends(get_db)):
    records = db.query(Sequence).all()
    return [{"id": r.id, "name": r.name, "length": len(r.sequence)} for r in records]

@app.get("/sequences/{seq_id}")
def get_sequence(seq_id: int, db: Session = Depends(get_db)):
    record = db.query(Sequence).filter(Sequence.id == seq_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Sequence not found")
    from parser import annotate_nucleotides
    return {
        "id":          record.id,
        "name":        record.name,
        "sequence":    record.sequence,
        "length":      len(record.sequence),
        "gc_content":  calc_gc(record.sequence),
        "exons":       find_exons(record.sequence),
        "nucleotides": annotate_nucleotides(record.sequence),
    }

@app.get("/compare/{id1}/{id2}")
def compare_sequences(id1: int, id2: int, db: Session = Depends(get_db)):
    s1 = db.query(Sequence).filter(Sequence.id == id1).first()
    s2 = db.query(Sequence).filter(Sequence.id == id2).first()
    if not s1 or not s2:
        raise HTTPException(status_code=404, detail="Sequence not found")
    mutations = find_mutations(s1.sequence, s2.sequence)
    return {"mutations": mutations, "total": len(mutations)}

@app.get("/ncbi/search")
def ncbi_search(gene: str, organism: str = "human"):
    result = search_gene(gene, organism)
    if not result:
        raise HTTPException(status_code=404, detail="Gene not found in NCBI")
    sequences = parse_fasta(result["fasta"])
    return {"ncbi_id": result["ncbi_id"], "sequences": sequences}

@app.get("/ncbi/accession/{acc}")
def ncbi_accession(acc: str):
    fasta = fetch_by_accession(acc)
    sequences = parse_fasta(fasta)
    return {"sequences": sequences}