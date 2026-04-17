import json
import random

# New proteins to add
new_proteins = [
  {
    "name": "Dsup (Supresor de Daño)",
    "organism": "Ramazzottius varieornatus (Tardígrado)",
    "pdb_id": "6C2P",
    "dna_sig": "ATGCGTACCGTA",
    "desc": "¡El escudo de los ositos de agua! Esta proteína 'abraza' el ADN para protegerlo de la radiación extrema.",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Waterbear.jpg/800px-Waterbear.jpg"
  },
  {
    "name": "Proteína Verde Fluorescente (GFP)",
    "organism": "Aequorea victoria (Medusa)",
    "pdb_id": "1EMA",
    "dna_sig": "TTGACAGCTAGC",
    "desc": "La linterna del océano. Esta proteína brilla con luz verde bajo luz UV.",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Aequorea_victoria.jpg/640px-Aequorea_victoria.jpg"
  },
  {
    "name": "Luciferasa",
    "organism": "Photinus pyralis (Luciérnaga)",
    "pdb_id": "1LCI",
    "dna_sig": "GGCTATTCGATA",
    "desc": "La química del amor luminoso. Esta enzima cataliza la reacción que hace brillar a las luciérnagas.",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Firefly_composition.jpg/800px-Firefly_composition.jpg"
  },
  {
    "name": "Hemocianina",
    "organism": "Enteroctopus dofleini (Pulpo Gigante)",
    "pdb_id": "1JS8",
    "dna_sig": "CCAAATTGGCCG",
    "desc": "¿Sangre azul? ¡Sí! Los pulpos usan cobre en esta proteína para transportar oxígeno.",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Giant_Pacific_Octopus_02.jpg/800px-Giant_Pacific_Octopus_02.jpg"
  },
  {
    "name": "Espidroína (Seda de Araña)",
    "organism": "Nephila clavipes (Araña de Seda de Oro)",
    "pdb_id": "3B4P",
    "dna_sig": "GGTACCGGTACC",
    "desc": "Más fuerte que el acero. Esta proteína forma la seda de las telarañas.",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Nephila_clavipes_female.jpg/640px-Nephila_clavipes_female.jpg"
  },
  {
    "name": "RuBisCO",
    "organism": "Spinacia oleracea (Espinaca)",
    "pdb_id": "8RUB",
    "dna_sig": "ATGCTAGCTAGC",
    "desc": "La encargada de capturar el CO2 de la atmósfera durante la fotosíntesis.",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Spinacia_oleracea_Spinach.jpg/640px-Spinacia_oleracea_Spinach.jpg"
  },
  {
    "name": "Proteína Anticongelante",
    "organism": "Zoarces americanus (Pez de Hielo)",
    "pdb_id": "1KDF",
    "dna_sig": "AAATTTCCCGGG",
    "desc": "¡Anticongelante natural! Impide que la sangre de estos peces polares se congele.",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Ocean_pout.jpg/800px-Ocean_pout.jpg"
  },
  {
    "name": "Cas9",
    "organism": "Streptococcus pyogenes (Bacteria)",
    "pdb_id": "4UN3",
    "dna_sig": "GATTACAGATTA",
    "desc": "El bisturí molecular. La herramienta CRISPR más famosa para editar genes.",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Streptococcus_pyogenes.jpg/640px-Streptococcus_pyogenes.jpg"
  },
  {
    "name": "Termoliesina",
    "organism": "Bacillus thermoproteolyticus (Bacteria Termófila)",
    "pdb_id": "1TLP",
    "dna_sig": "CGTACGTACGTAG",
    "desc": "Una proteína a prueba de calor que vive en manantiales termales y volcanes.",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Grand_Prismatic_Spring_2006.jpg/800px-Grand_Prismatic_Spring_2006.jpg"
  },
  {
    "name": "Bacteriorrodopsina",
    "organism": "Halobacterium salinarum (Arquea)",
    "pdb_id": "1AP9",
    "dna_sig": "ATATATGCGCGC",
    "desc": "Una bomba de protones púrpura que convierte la luz solar en energía química.",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Salt_Ponds_-_South_Bay_SF.jpg/800px-Salt_Ponds_-_South_Bay_SF.jpg"
  }
]

# Alternate human images
human_images = [
    "https://upload.wikimedia.org/wikipedia/commons/2/2e/Baby.jpg", # Original
    "https://upload.wikimedia.org/wikipedia/commons/2/22/Da_Vinci_Vitruve_Luc_Viatour.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/b/b5/1_face_of_a_woman.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/c/c7/Crowd_at_Shibuya_Crossing_%283120669228%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/2/2d/Laboratory_Science_Biomedical.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/6/6e/Child_playing_in_the_sand.jpg"
]

# Load existing DB
try:
    with open('protein_db.json', 'r') as f:
        db = json.load(f)
except FileNotFoundError:
    db = []

# Update existing human entries to have a LIST of images
for entry in db:
    if "Homo sapiens" in entry['organism']:
        # Change image_url to the list of human images
        entry['image_url'] = human_images

# Add new proteins (avoid duplicates if name exists)
existing_names = {p['name'] for p in db}
for p in new_proteins:
    if p['name'] not in existing_names:
        db.append(p)

# Save back to file
with open('protein_db.json', 'w') as f:
    json.dump(db, f, indent=4, ensure_ascii=False)

print("Database updated successfully!")
