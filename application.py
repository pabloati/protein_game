import streamlit as st
from stmol import showmol
import py3Dmol
from Bio import pairwise2
from Bio.Seq import Seq
import random
import hashlib
import json
import os

# -----------------------------------------------------------------------------
# 1. CONFIGURATION & ASSETS
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Explorador BioDeco", layout="wide", page_icon="🧬")

# Custom CSS for the "Modern Art Deco" Aesthetic
# We import 'Josefin Sans' for that geometric 1920s look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@300;400;700&display=swap');

    /* Main Background - Creamy Off-White */
    .stApp {
        background-color: #FDFBF7;
        font-family: 'Josefin Sans', sans-serif;
        color: #2C3E50;
    }

    /* General Text Elements */
    p, div, span, label, .stMarkdown {
        color: #2C3E50;
    }

    /* Headings - Gold & Geometric */
    h1, h2, h3 {
        color: #2C3E50;
        font-family: 'Josefin Sans', sans-serif;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    h1 {
        border-bottom: 3px solid #D4AF37; /* Art Deco Gold Underline */
        padding-bottom: 10px;
        text-align: center;
    }

    /* Input Fields - Elegant Borders */
    .stTextInput > div > div > input {
        background-color: #FFFFFF;
        border: 2px solid #D4AF37;
        color: #2C3E50;
        border-radius: 0px; /* Sharp corners for Deco look */
        caret-color: #2C3E50; /* Ensure cursor is visible */
    }
    
    /* Input Focus State */
    .stTextInput > div > div > input:focus {
        border-color: #008080 !important;
        box-shadow: 0 0 5px rgba(0,128,128,0.5);
    }
    
    /* Placeholder Text Color */
    .stTextInput > div > div > input::placeholder {
        color: #A0A0A0;
        opacity: 1;
    }

    /* Buttons - Teal with White Text */
    div.stButton > button {
        background-color: #008080;
        color: #FFFFFF !important;
        border: 2px solid #008080;
        border-radius: 5px;
        padding: 10px 25px;
        font-family: 'Josefin Sans', sans-serif;
        font-weight: 700;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    div.stButton > button:hover {
        background-color: #FDFBF7;
        color: #008080 !important;
        border: 2px solid #008080;
    }

    /* Force white text on all inner elements of buttons (overrides global p/span/div rule) */
    div.stButton > button p,
    div.stButton > button span,
    div.stButton > button div {
        color: #FFFFFF !important;
    }

    div.stButton > button:hover p,
    div.stButton > button:hover span,
    div.stButton > button:hover div {
        color: #008080 !important;
    }

    /* Info Cards (Custom Container) */
    .deco-card {
        background-color: white;
        padding: 20px;
        border: 1px solid #E0E0E0;
        border-left: 5px solid #D4AF37;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. BIOINFORMATICS LOGIC
# -----------------------------------------------------------------------------

# A Simplified "Modified" Genetic Code (Amino Acid -> DNA Codon)
# You can edit this to match exactly what you give the students
AA_TO_DNA = {
    'A': 'GCT', 'B': 'GAT', 'C': 'TGT', 'D': 'ACC', 'E': 'GAG', 'F': 'TTT',
    'G': 'GGT', 'H': 'CAT', 'I': 'ATT', 'J': 'CTA', 'K': 'AAA', 'L': 'TTA',
    'M': 'ATG', 'N': 'AAT', 'Ñ': 'AGC', 'O': 'TAG', 'P': 'CCT', 'Q': 'CAA',
    'R': 'CGT', 'S': 'TCT', 'T': 'ACT', 'U': 'TGA', 'V': 'GTT', 'W': 'TGG',
    'X': 'GAA', 'Y': 'TAT', 'Z': 'GTG'
}

# Load protein database from JSON file
def load_protein_db():
    """Load the protein database from protein_db.json file."""
    db_path = os.path.join(os.path.dirname(__file__), 'protein_db.json')
    with open(db_path, 'r') as f:
        return json.load(f)

PROTEIN_DB = load_protein_db()

def validate_name(name):
    """Validates the input name to ensure it contains only alphabetic characters or spaces."""
    if not all(char.isalpha() or char.isspace() for char in name):
        st.error("Please enter a valid name containing only letters (A-Z) and spaces.")
        return False
    return True

def get_dna_from_name(name):
    """Converts a name (string) into a DNA sequence using the map."""
    clean_name = ''.join(filter(str.isalpha, name)).upper()
    dna_seq = ""
    for char in clean_name:
        dna_seq += AA_TO_DNA.get(char, 'NNN') # NNN if unknown
    return dna_seq

def find_best_match(query_dna):
    """
    Performs a Local Alignment (Smith-Waterman) against the database.
    Returns (best_protein_dict, debug_log_list).

    Selection logic:
      1. Pick the protein with the highest alignment score.
      2. Ties are broken alphabetically by protein name for determinism.
      3. If no alignment scores > 0, a deterministic random protein is
         chosen (seeded by SHA-256 of the query DNA) so the same input
         always returns the same result.
    """
    scored = []  # list of (score, protein_name, protein_dict, alignment_str)
    no_match = []  # proteins with no alignment

    for prot in PROTEIN_DB:
        alignments = pairwise2.align.localms(
            query_dna, prot['dna_sig'], 2, -1, -0.5, -0.1
        )
        if alignments:
            best_aln = alignments[0]
            score = best_aln.score
            aln_str = pairwise2.format_alignment(*best_aln)
            scored.append((score, prot['name'], prot, aln_str))
        else:
            no_match.append(prot)

    # Sort: highest score first, then alphabetically by name for determinism
    scored.sort(key=lambda x: (-x[0], x[1]))

    # Build debug log in score order (best → worst), then no-match entries
    debug_log = []
    for score, name, prot, aln_str in scored:
        debug_log.append(
            f"── {name}  (dna_sig={prot['dna_sig']})  "
            f"score={score:.2f}"
        )
        for line in aln_str.rstrip('\n').split('\n'):
            debug_log.append(f"   {line}")
        debug_log.append("")
    for prot in sorted(no_match, key=lambda p: p['name']):
        debug_log.append(
            f"── {prot['name']}  (dna_sig={prot['dna_sig']})  "
            f"score=--  [no alignment]"
        )
        debug_log.append("")

    if scored and scored[0][0] > 0:
        best_score, best_name, best_protein, best_aln_str = scored[0]
        debug_log.insert(0, f"QUERY DNA: {query_dna}")
        debug_log.insert(1, "=" * 70)
        debug_log.append("=" * 70)
        debug_log.append(f">>> SELECTED: {best_name}  (score={best_score:.2f})")
        debug_log.append("--- Winning alignment ---")
        debug_log.append(best_aln_str)
        # Store alignment string in the protein dict for UI access
        best_protein['alignment_str'] = best_aln_str
        return best_protein, debug_log

    # Deterministic random fallback
    seed = int(hashlib.sha256(query_dna.encode()).hexdigest(), 16)
    rng = random.Random(seed)
    sorted_db = sorted(PROTEIN_DB, key=lambda p: p['name'])
    fallback = rng.choice(sorted_db)
    debug_log.insert(0, f"QUERY DNA: {query_dna}")
    debug_log.append("")
    debug_log.append(
        f">>> No score > 0.  Deterministic random fallback -> {fallback['name']}"
    )
    # Add a dummy alignment string or explanation for fallback
    fallback['alignment_str'] = "No alignment significant found.\nRandom match selected."
    return fallback, debug_log

# -----------------------------------------------------------------------------
# 3. UI LAYOUT
# -----------------------------------------------------------------------------

st.title("¿Qué Proteína se esconde en tu nombre?")
st.markdown("<p style='text-align: center; color: #555;'>Traduce tu identidad al código de la vida</p>", unsafe_allow_html=True)

# Spacing
st.write("---")

# --- STEP 1: INPUT ---
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 1. Identifica")
    name_input = st.text_input("INTRODUCE TU NOMBRE", placeholder="ej. Ana Mena")
    
    if name_input and validate_name(name_input):
        user_dna = get_dna_from_name(name_input)
        
        st.markdown(f"""
        <div class='deco-card'>
            <strong>TU SECUENCIA DE ADN:</strong><br>
            <span style='font-family: monospace; color: #008080; font-size: 1.2em; word-wrap: break-word;'>
                {user_dna}
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # Search Button
        if st.button("BUSCAR EN LA BASE DE DATOS"):
            result, log = find_best_match(user_dna)
            st.session_state['search_done'] = True
            st.session_state['dna'] = user_dna
            st.session_state['match'] = result
            st.session_state['debug_log'] = log
            # Hide 3D and organism panels so user clicks to reveal them
            st.session_state['show_3d'] = False
            st.session_state['show_organism'] = False

# --- STEP 2: RESULTS ---
with col2:
    if st.session_state.get('search_done'):
        st.markdown("### 2. Resultado del Análisis")
        
        # Retrieve the cached result
        match = st.session_state['match']
        
        # row for detailed info & alignment
        row1_col1, row1_col2 = st.columns(2)
        
        with row1_col1:
            # Display Data Card (top part spanning full column)
            st.markdown(f"""
            <div class='deco-card' style='border-left: 5px solid #008080; height: 100%;'>
                <h3 style='margin-top:0;'>COINCIDENCIA: {match['name']}</h3>
                <p><strong>Organismo:</strong> {match['organism']}</p>
                <p><strong>Función:</strong> {match['desc']}</p>
                <p><strong>ID PDB:</strong> {match['pdb_id']}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with row1_col2:
            # Display Alignment Visualization
            # match['alignment_str'] was added in find_best_match
            align_text = match.get('alignment_str', 'No alignment data available.')
            
            # Ensure newlines are preserved by rendering them as individual lines or using strict pre-formatting
            # We replace newlines with <br> just in case, but <pre> usually handles \n. 
            # However, sometimes f-strings indentation in python multi-line strings can mess up formatting 
            # if we are not careful. Let's sanitize it.
            
            st.markdown(f"""
            <div class='deco-card' style='border-left: 5px solid #D4AF37; height: 100%;'>
                <h3 style='margin-top:0;'>ALINEAMIENTO VISUAL</h3>
                <div style='background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; font-family: monospace; white-space: pre;'>{align_text}</div>
                <p style='font-size: 0.8em; color: #888;'>*La mejor coincidencia local encontrada por el algoritmo de Smith-Waterman.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Create two sub-columns for the buttons and displays
        subcol1, subcol2 = st.columns(2)
        
        with subcol1:
            if st.button("VER ESTRUCTURA 3D"):
                st.session_state['show_3d'] = True
                st.session_state['show_organism'] = False
            
            if st.session_state.get('show_3d'):
                st.markdown("**ESTRUCTURA 3D**")
                # Create py3Dmol view
                view = py3Dmol.view(query=f"pdb:{match['pdb_id']}", width=350, height=400)
                view.setStyle({'cartoon': {'color': 'spectrum'}})
                view.spin(True)
                view.zoomTo()
                # Render - use width that fits the subcolumn
                showmol(view, height=400, width=350)
        
        with subcol2:
            if st.button("VER ORGANISMO"):
                st.session_state['show_organism'] = True
                st.session_state['show_3d'] = False
            
            if st.session_state.get('show_organism'):
                st.markdown("**IMAGEN DEL ORGANISMO**")
                # Display organism image
                if 'image_url' in match and match['image_url']:
                    try:
                        # Handle multiple images (random selection) or single image
                        img_source = match['image_url']
                        organism_name = match['organism']
                        if organism_name == "Homo sapiens (Humano)" and not match['name'] == "Sonic Hedgehog":
                            possible_images = ["https://upload.wikimedia.org/wikipedia/commons/2/2e/Baby.jpg",
                                               "https://divulgacioncientifica.uca.es/wp-content/uploads/2017/05/culturacientifica2.jpg",
                                               "https://www.unir.net/wp-content/uploads/2024/08/Caracteristicas-de-los-derechos-humanos-las-conoces1.webp"]
                            img_to_show = random.choice(possible_images)
                        else: 
                            img_to_show = img_source

                        # Use a spinner to indicate loading
                        with st.spinner(f"Cargando imagen de {match['organism']}..."):
                            st.image(img_to_show, caption=match['organism'], width="stretch")
                    except Exception as e:
                        st.error(f"No se pudo cargar la imagen. (Error: {str(e)})")
                        st.info(f"Puedes verla aquí: [Enlace]({(match['image_url'][0] if isinstance(match['image_url'], list) else match['image_url'])})")
                else:
                    st.info("No hay imagen disponible para este organismo.")
        
    else:
        # Placeholder before search
        st.info("← Introduce tu nombre para generar tu secuencia de ADN y escanear la base de datos.")

# -----------------------------------------------------------------------------
# 4. DEBUG LOG
# -----------------------------------------------------------------------------
if st.session_state.get('debug_log'):
    with st.expander("DEBUG: Alignment Log", expanded=False):
        st.code("\n".join(st.session_state['debug_log']), language="text")

# -----------------------------------------------------------------------------
# 5. FOOTER
# -----------------------------------------------------------------------------
st.markdown("<br><br><div style='text-align:center; font-size:0.8em; color:#888;'>Diseñado para Divulgación • Desarrollado con Python & Streamlit</div>", unsafe_allow_html=True)