import json
import requests
import argparse

def check_images(mode="both"):
    with open("protein_db.json", "r", encoding="utf-8") as f:
        db = json.load(f)
        
    print(f"Checking images for {len(db)} proteins (Mode: {mode})...\n")
    
    failed_proteins = []
    
    for p in db:
        name = p.get('name', 'Unknown')
        pdb_id = p.get('pdb_id')
        image_url = p.get('image_url')
        
        failures = []
        
        # 1. Check PDB Image mimicking the diploma_generator.py logic
        if mode in ["pdb", "both"]:
            if pdb_id:
                pdb_lower = pdb_id.lower()
                base_url = "https://cdn.rcsb.org/images/structures"
                image_suffixes = [
                    f"{pdb_lower}_assembly-1.jpeg",
                    f"{pdb_lower}_model-1.jpeg",
                    f"{pdb_lower}_chain-A.jpeg",
                    f"{pdb_lower}.jpeg"
                ]
                
                pdb_success = False
                for suffix in image_suffixes:
                    try:
                        resp = requests.get(f"{base_url}/{suffix}", timeout=5)
                        if resp.status_code == 200:
                            pdb_success = True
                            break
                    except Exception:
                        continue
                
                if not pdb_success:
                    failures.append("PDB image failed")
            else:
                failures.append("No pdb_id provided")

        # 2. Check Organism Image
        if mode in ["wiki", "both"]:
            if image_url:
                if isinstance(image_url, list):
                    image_url = image_url[0]
                try:
                    # We use a user-agent because some wikimedia or other sites block simple python requests
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                    resp = requests.get(image_url, headers=headers, timeout=10)
                    resp.raise_for_status()
                except Exception as e:
                    failures.append(f"Organism image failed ({type(e).__name__})")
            else:
                failures.append("No image_url provided")
            
        if failures:
            failed_proteins.append({
                "name": name,
                "failures": failures
            })
            
    if not failed_proteins:
        print("✅ All checked images downloaded successfully for all proteins!")
    else:
        print(f"❌ Found issues in {len(failed_proteins)} proteins:\n")
        for fp in failed_proteins:
            print(f"🔹 {fp['name']}:")
            for fail in fp['failures']:
                print(f"   - {fail}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check image links for proteins.")
    parser.add_argument("--mode", choices=["pdb", "wiki", "both"], default="both", 
                        help="Select what to check: 'pdb', 'wiki', or 'both'")
    args = parser.parse_args()
    
    check_images(mode=args.mode)