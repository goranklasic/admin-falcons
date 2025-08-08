# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 11:18:19 2025
@author: goranklasic
"""

import os, time
from datetime import datetime
from docxtpl import DocxTemplate
from docx2pdf import convert
from PyPDF2 import PdfMerger
import pythoncom

# 📆 Safe date formatting helper
def format_date(val):
    if isinstance(val, datetime):
        return val.strftime('%Y-%m-%d')
    try:
        return datetime.fromisoformat(str(val)).strftime('%Y-%m-%d')
    except Exception:
        return str(val or '')

# 🧩 Main processor entry point
def process_player_record(player):
    player_id, player_name, gender_id, player_address, player_dob, player_email, _, medical, train, play, consent, role, phone1, contact1, phone2, contact2, pname, paddress, pdob, pmobile = player

    context = {
        'playername': player_name,
        'playergender': gender_id,
        'playeraddress': player_address,
        'playerdob': format_date(player_dob),
        'contactemail': player_email,
        'medicalconditions': medical,
        'participation_training': 'YES' if train == 1 else 'NO',
        'participation_play_matches': 'YES' if play == 1 else 'NO',
        'photo_cons': 'YES' if consent == 1 else 'NO',
        'player_role': role,
        'primary_phonenumber': phone1,
        'primary_contact': contact1,
        'secondary_phonenumber': phone2 or '',
        'secondary_contact': contact2 or '',
        'parentname': pname or '',
        'parentaddress': paddress or '',
        'parentdob': format_date(pdob),
        'parentphonenumber': pmobile or '',
        'currentdate': datetime.now().strftime('%Y-%m-%d')
    }

    safe_name = '_'.join(player_name.split())
    base_name = f"membership_template_{safe_name}_{context['currentdate']}"
    template_dir = os.path.join('static', 'templates')
    output_dir = os.path.join('static', 'documents')
    os.makedirs(output_dir, exist_ok=True)

    doc_paths = {
        'docx1': os.path.join(template_dir, 'membership_template.docx'),
        'docx2': os.path.join(template_dir, 'membership_template_extend.docx'),
        'filled1': os.path.join(output_dir, f"{base_name}_1.docx"),
        'filled2': os.path.join(output_dir, f"{base_name}_2.docx"),
        'pdf1': os.path.join(output_dir, f"{base_name}_1.pdf"),
        'pdf2': os.path.join(output_dir, f"{base_name}_2.pdf"),
        'merged': os.path.join(output_dir, f"{base_name}.pdf")
    }

    # 📝 Fill templates using DocxTemplate
    tpl1 = DocxTemplate(doc_paths['docx1'])
    tpl1.render(context)
    tpl1.save(doc_paths['filled1'])

    tpl2 = DocxTemplate(doc_paths['docx2'])
    tpl2.render(context)
    tpl2.save(doc_paths['filled2'])

    # 📄 Convert to PDF
    pythoncom.CoInitialize()
    try:
        convert(doc_paths['filled1'], doc_paths['pdf1'])
        convert(doc_paths['filled2'], doc_paths['pdf2'])
    finally:
        pythoncom.CoUninitialize()

    # 🔗 Merge PDFs
    merger = PdfMerger()
    merger.append(doc_paths['pdf1'])
    merger.append(doc_paths['pdf2'])
    merger.write(doc_paths['merged'])
    merger.close()

    # 🧹 Clean temp files
    for temp in ['filled1', 'filled2', 'pdf1', 'pdf2']:
        try:
            time.sleep(0.2)
            if os.path.exists(doc_paths[temp]):
                os.remove(doc_paths[temp])
        except Exception as e:
            print(f"⚠️ Cleanup failed: {temp} — {e}")

    print(f"✅ Generated PDF for {player_name} → {doc_paths['merged']}")
    return {
        'player_id': player_id,
        'pdf_path': doc_paths['merged'],
        'contactemail': player_email,
        'playername': player_name
    }