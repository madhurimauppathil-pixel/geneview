import requests

NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def search_gene(gene_name: str, organism: str = "human"):
    search_url = f"{NCBI_BASE}/esearch.fcgi"
    params = {
        "db":      "nucleotide",
        "term":    f"{gene_name}[Gene Name] AND {organism}[Organism]",
        "retmax":  5,
        "retmode": "json",
    }
    res = requests.get(search_url, params=params)
    ids = res.json().get("esearchresult", {}).get("idlist", [])
    if not ids:
        return None

    fetch_url = f"{NCBI_BASE}/efetch.fcgi"
    fetch_params = {
        "db":      "nucleotide",
        "id":      ids[0],
        "rettype": "fasta",
        "retmode": "text",
    }
    seq_res = requests.get(fetch_url, params=fetch_params)
    return {"fasta": seq_res.text, "ncbi_id": ids[0]}

def fetch_by_accession(accession: str):
    fetch_url = f"{NCBI_BASE}/efetch.fcgi"
    params = {
        "db":      "nucleotide",
        "id":      accession,
        "rettype": "fasta",
        "retmode": "text",
    }
    res = requests.get(fetch_url, params=params)
    return res.text