from Bio import SeqIO
from Bio.Seq import Seq
import io

NUCLEOTIDE_COLORS = {
    "A": "#4CAF50",
    "T": "#F44336",
    "G": "#2196F3",
    "C": "#FF9800",
    "U": "#9C27B0",
    "N": "#9E9E9E",
}

def parse_fasta(file_content: str):
    sequences = []
    fasta_io = io.StringIO(file_content)
    for record in SeqIO.parse(fasta_io, "fasta"):
        sequences.append({
            "id":          str(record.id),
            "name":        str(record.description),
            "sequence":    str(record.seq),
            "length":      len(record.seq),
            "gc_content":  calc_gc(str(record.seq)),
            "nucleotides": annotate_nucleotides(str(record.seq)),
        })
    return sequences

def parse_csv(file_content: str):
    sequences = []
    for line in file_content.strip().split("\n")[1:]:
        parts = line.split(",")
        if len(parts) >= 2:
            name, seq = parts[0].strip(), parts[1].strip()
            sequences.append({
                "id":          name,
                "name":        name,
                "sequence":    seq,
                "length":      len(seq),
                "gc_content":  calc_gc(seq),
                "nucleotides": annotate_nucleotides(seq),
            })
    return sequences

def calc_gc(sequence: str) -> float:
    seq = sequence.upper()
    if not seq:
        return 0.0
    gc = seq.count("G") + seq.count("C")
    return round((gc / len(seq)) * 100, 2)

def annotate_nucleotides(sequence: str):
    return [
        {"char": nt, "color": NUCLEOTIDE_COLORS.get(nt.upper(), "#9E9E9E")}
        for nt in sequence
    ]

def find_mutations(seq1: str, seq2: str):
    mutations = []
    for i, (a, b) in enumerate(zip(seq1, seq2)):
        if a.upper() != b.upper():
            mutations.append({
                "position": i,
                "original": a,
                "mutated":  b,
                "type":     classify_mutation(a, b),
            })
    return mutations

def classify_mutation(orig: str, mut: str):
    purines     = {"A", "G"}
    pyrimidines = {"T", "C", "U"}
    o, m = orig.upper(), mut.upper()
    if o in purines and m in purines:
        return "transition"
    if o in pyrimidines and m in pyrimidines:
        return "transition"
    return "transversion"

def find_exons(sequence: str):
    seq   = sequence.upper()
    exons = []
    start_codon = "ATG"
    stop_codons = {"TAA", "TAG", "TGA"}
    i = 0
    while i < len(seq) - 2:
        if seq[i:i+3] == start_codon:
            for j in range(i+3, len(seq)-2, 3):
                codon = seq[j:j+3]
                if codon in stop_codons:
                    exons.append({"start": i, "end": j+3, "length": j+3-i})
                    i = j + 3
                    break
            else:
                i += 1
        else:
            i += 1
    return exons