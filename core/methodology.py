def get_template_data(full_path):
    if not os.path.exists(full_path): return None
    order = 999
    fm_data = {}
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    fm_match = re.match(r"^---[\s\S]*?---", content)
    body = content
    if fm_match:
        try:
            fm_text = fm_match.group(0).strip('-')
            fm_data = yaml.safe_load(fm_text) or {}
            order = int(fm_data.get('order', 999))
            body = content[fm_match.end():].strip()
        except: pass
    return {"body": body, "order": order, "fields": fm_data}

def sync_smart_content(current_content, all_templates):
    header_anchor = "## ⚙️ METODOLOGÍA"
    footer_anchor = "#AUTOGENERAR"
    
    existing_states = {}
    found_tasks = re.findall(r"- (\[[ xX]\]) (.*)", current_content)
    for status, text in found_tasks:
        existing_states[text.strip()] = status

    if header_anchor in current_content:
        base_note = current_content.split(header_anchor)[0].strip()
    else:
        base_note = current_content.strip()

    manual_notes = ""
    if "## 📓 NOTAS" in current_content:
        notes_parts = current_content.split("## 📓 NOTAS")
        manual_notes = "## 📓 NOTAS" + notes_parts[-1]

    all_templates.sort(key=lambda x: x['order'])
    new_methodology = ""
    for t in all_templates:
        lines = t['body'].split('\n')
        for line in lines:
            if "- [ ]" in line:
                task_text = line.replace("- [ ]", "").strip()
                status = existing_states.get(task_text, "[ ]")
                mark = "[x]" if "x" in status.lower() else "[ ]"
                new_methodology += line.replace("[ ]", mark) + "\n"
            else:
                new_methodology += line + "\n"
        new_methodology += "\n"

    final_output = (
        f"{base_note}\n\n"
        f"{header_anchor}\n\n"
        f"{new_methodology.strip()}\n\n"
        f"{footer_anchor}\n\n"
        f"{manual_notes.strip()}"
    )
    return final_output.strip() + "\n"
