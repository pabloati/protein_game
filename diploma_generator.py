import os
import requests
import tempfile
from fpdf import FPDF

def fit_text_line(pdf, text, max_width, start_size, font="Helvetica", style=""):
    """
    Helper function to dynamically reduce font size so a single line of text 
    fits within a specified width, preventing awkward word-wraps for titles.
    """
    size = start_size
    pdf.set_font(font, style=style, size=size)
    while pdf.get_string_width(text) > max_width and size > 4:
        size -= 0.5  # Reduce by half a point and check again
        pdf.set_font(font, style=style, size=size)
    return size

def create_diploma_pdf(user_name, user_dna, match_data):
    """
    Generates a PDF diploma in memory and returns its bytes.
    Uses 'fpdf2' to construct the layout and embed the organism image.
    """
    pdf = FPDF(orientation="L", unit="mm", format="A4") # Landscape A4
    pdf.add_page()
    
    # 1. Art Deco style golden border
    pdf.set_draw_color(212, 175, 55) # Gold (#D4AF37)
    pdf.set_line_width(2)
    pdf.rect(10, 10, 277, 190)
    pdf.rect(12, 12, 273, 186) # Double border!
    
    # 2. Main Title
    pdf.set_font("Helvetica", style="B", size=24)
    pdf.set_text_color(44, 62, 80) # Dark Teal / Deco Navy
    pdf.cell(0, 25, text="¿Qué proteína se esconde en tu nombre?", align="C", new_x="LMARGIN", new_y="NEXT")
    
    # 3. Presentation text
    pdf.set_font("Helvetica", size=14)
    pdf.cell(0, 10, text=f"Se certifica que el nombre de:", align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", style="B", size=20)
    pdf.cell(0, 15, text=user_name.upper(), align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, text="Se traduce en el siguiente ADN:", align="C", new_x="LMARGIN", new_y="NEXT")
    
    # ADN Sequence (Monospace)
    pdf.set_font("Courier", size=10)
    pdf.set_text_color(0, 128, 128) # Teal
    pdf.multi_cell(0, 8, text=user_dna, align="C", new_x="LMARGIN", new_y="NEXT")
    
    # 4. Three-Column Layout (Bottom Half)
    start_y = 90
    col_width = 80
    col1_x = 15
    col2_x = 108
    col3_x = 202
    
    # ---------------------------------------------------------
    # LEFT COLUMN: Description & Alignment
    # ---------------------------------------------------------
    pdf.set_xy(col1_x, start_y)
    pdf.set_text_color(44, 62, 80)
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.multi_cell(col_width, 6, text="Descripción de la función", align="C")
    
    pdf.set_xy(col1_x, pdf.get_y() + 2)
    
    # Dynamically scale description font if it's too long
    desc_text = match_data.get('desc', 'Sin descripción')
    desc_len = len(desc_text)
    desc_font_size = 9 if desc_len < 150 else (8 if desc_len < 300 else 7)
    pdf.set_font("Helvetica", size=desc_font_size)
    pdf.multi_cell(col_width, desc_font_size * 0.5, text=desc_text, align="C")
    
    pdf.set_xy(col1_x, pdf.get_y() + 10)
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.multi_cell(col_width, 5, text="Alineamiento", align="C")
    
    pdf.set_xy(col1_x, pdf.get_y() + 2)
    # The alignment can be wide. dynamically reduce font size to fit width of column
    align_text = match_data.get('alignment_str', 'Sin datos')
    # Split alignment into lines and find the longest line to calculate width
    longest_align_line = max(align_text.split('\n'), key=len) if align_text else ""
    # Start with a bigger default size (e.g. 10 instead of 8)
    align_font_size = fit_text_line(pdf, longest_align_line, max_width=col_width, start_size=10, font="Courier")
    pdf.set_font("Courier", size=align_font_size)
    pdf.set_text_color(100, 100, 100) # Lighter grey for alignment
    # Center the alignment block
    pdf.multi_cell(col_width, align_font_size * 0.4, text=align_text, align="C")
    
    # ---------------------------------------------------------
    # CENTER COLUMN: Protein Name & PDB 3D Image
    # ---------------------------------------------------------
    pdf.set_xy(col2_x, start_y)
    pdf.set_text_color(44, 62, 80)
    prot_name = match_data['name']
    
    # Fit the protein name dynamically
    prot_font_size = fit_text_line(pdf, prot_name, max_width=col_width, start_size=16, font="Helvetica", style="B")
    pdf.multi_cell(col_width, 6, text=prot_name, align="C")
    
    current_y = pdf.get_y() + 5
    pdb_id = match_data.get('pdb_id')
    if pdb_id:
        pdb_img_url = f"https://cdn.rcsb.org/images/structures/{pdb_id.lower()}_assembly-1.jpeg"
        try:
            resp = requests.get(pdb_img_url, timeout=5)
            resp.raise_for_status()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_file.write(resp.content)
                tmp_pdb = tmp_file.name
            
            # Dynamic image sizing: Width fits column (w=70), 
            # OR height avoids overflowing the page border (Y max = 190)
            max_h = 190 - current_y - 5
            pdf.image(tmp_pdb, x=col2_x + 5, y=current_y, w=70, h=max_h, keep_aspect_ratio=True)
            os.remove(tmp_pdb)
        except:
            pdf.set_xy(col2_x, current_y + 10)
            pdf.set_font("Helvetica", size=9)
            pdf.multi_cell(col_width, 5, text="(Imagen 3D no disponible)", align="C")

    # ---------------------------------------------------------
    # RIGHT COLUMN: Organism & Image
    # ---------------------------------------------------------
    pdf.set_xy(col3_x, start_y)
    organism = match_data.get('organism', '')
    
    if '(' in organism and ')' in organism:
        parts = organism.split('(', 1)
        sci_name = parts[0].strip()
        com_name = '(' + parts[1].strip()
    else:
        sci_name = organism
        com_name = ""
        
    sci_font_size = fit_text_line(pdf, sci_name, max_width=col_width, start_size=14, font="Helvetica", style="I")
    pdf.multi_cell(col_width, 6, text=sci_name, align="C")
    
    current_y = pdf.get_y()
    if com_name:
        pdf.set_xy(col3_x, current_y)
        com_font_size = fit_text_line(pdf, com_name, max_width=col_width, start_size=12, font="Helvetica")
        pdf.multi_cell(col_width, 6, text=com_name, align="C")
        current_y = pdf.get_y()
        
    current_y += 5
    if 'image_url' in match_data and match_data['image_url']:
        img_url = match_data['image_url']
        if isinstance(img_url, list):
            img_url = img_url[0]
            
        try:
            resp = requests.get(img_url, timeout=5)
            resp.raise_for_status()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_file.write(resp.content)
                tmp_img = tmp_file.name
            
            # Dynamic image sizing: keep within boundaries
            max_h = 190 - current_y - 5
            pdf.image(tmp_img, x=col3_x + 5, y=current_y, w=70, h=max_h, keep_aspect_ratio=True)
            os.remove(tmp_img)
        except:
            pass # Ignore if download fails
            
    pdf_bytes = pdf.output(dest='S')
    return bytes(pdf_bytes)