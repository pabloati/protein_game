import json

# Dictionary mapping exact protein names to their new 12-char dna_sig
UPDATES = {
    "Proteína Fluorescente Verde (GFP)": "ATGGCTCGTATT",
    "Pikachurina": "GCTAATACTTAG",
    "Spidroína": "CTATAGTCTGAG",
    "Dsup (Supresor de Daño)": "TGTGCTCGTTTA",
    "Luciferasa": "TTATGAATTTCT",
    "Sonic Hedgehog": "ACCGCTAATATT",
    "Hemocianina": "CTATGAGCTAAT",
    "Cas9": "GCTTTAGAGGAA",
    "Draculina": "TTTGAGCGTAAT",
    "Queratina": "TCTGCTCGTGCT",
    "Rubisco": "CCTGCTGATTTA",
    "Criptocromo": "ATGATTGGTTGA",
    "Taq Polimerasa": "TTAGCTTGACGT",
    "Miosina": "ACCGCTGTTATT",
    "Bacteriorrodopsina": "ATGGCTCGTACT"
}

def apply_fun_signatures():
    try:
        with open('protein_db.json', 'r', encoding='utf-8') as f:
            db = json.load(f)
            
        updated_count = 0
        for protein in db:
            if protein['name'] in UPDATES:
                protein['dna_sig'] = UPDATES[protein['name']]
                updated_count += 1
                
        with open('protein_db.json', 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
            
        print(f"Success! Updated the dna_sig for {updated_count} common proteins.")
        
    except FileNotFoundError:
        print("Error: 'protein_db.json' not found in the current directory.")

if __name__ == "__main__":
    apply_fun_signatures()
