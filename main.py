import argparse, os, yaml, sys, requests
from core.note_manager import NoteManager
from core.parser import parse_httpx_line
from core.methodology import get_template_data, sync_smart_content

GITHUB_TEMPLATE_URL = "https://raw.githubusercontent.com/NeTenebraes/neBBP/main/templates/main_template.md"

def ensure_templates(tpl_dir):
    main_tpl_path = os.path.join(tpl_dir, "main_template.md")
    if not os.path.exists(main_tpl_path):
        print(f"[*] Template no encontrado. Descargando de GitHub...")
        os.makedirs(tpl_dir, exist_ok=True)
        try:
            r = requests.get(GITHUB_TEMPLATE_URL, timeout=10)
            r.raise_for_status()
            with open(main_tpl_path, "w", encoding="utf-8") as f:
                f.write(r.text)
        except Exception as e:
            print(f"[ERROR] No se pudo obtener el template: {e}")
            sys.exit(1)
    return main_tpl_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()

    tpl_dir = os.path.join(os.getcwd(), "templates")
    main_tpl_path = ensure_templates(tpl_dir)

    nm = NoteManager(args.output)
    main_tpl = get_template_data(main_tpl_path)
    all_tpls = [get_template_data(os.path.join(tpl_dir, f)) 
                for f in os.listdir(tpl_dir) if f.endswith(".md") and f != "main_template.md"]

    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            data = parse_httpx_line(line)
            if not data: continue
            
            path = nm.get_path(data['host'])
            current_fm, current_body = nm.load(path)
            if current_fm.get('lock'): continue

            final_props, changelog = nm.merge_and_track(current_fm, data, main_tpl['fields'])
            body = current_body if current_body else main_tpl['body'].replace("{{HOST}}", data['host']).replace("{{URL}}", data['url'])
            
            new_fm_str = "---\n" + yaml.dump(final_props, sort_keys=False, allow_unicode=True) + "---"
            final_content = sync_smart_content(new_fm_str + "\n\n" + body, all_tpls)

            with open(path, 'w', encoding='utf-8') as fn:
                fn.write(final_content.strip() + (changelog if changelog else ""))
            print(f"[OK] {data['host']}")

if __name__ == "__main__":
    main()