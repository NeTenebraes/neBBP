import os, yaml, re, datetime

class NoteManager:
    def __init__(self, base_output):
        self.base_output = base_output

    def get_path(self, host):
        parts = host.split('.')
        root = ".".join(parts[-2:]) if len(parts) > 2 else host
        sub = ".".join(parts[-3:]) if len(parts) > 2 else host
        path = os.path.join(self.base_output, root, sub)
        os.makedirs(path, exist_ok=True)
        return os.path.join(path, f"{host}.md")

    def load(self, path):
        if not os.path.exists(path): return {}, ""
        with open(path, 'r', encoding='utf-8') as f: content = f.read()
        fm_match = re.match(r"^---[\s\S]*?---", content)
        if fm_match:
            fm = yaml.safe_load(fm_match.group(0).strip('-')) or {}
            return fm, content[fm_match.end():].strip()
        return {}, content.strip()

    def merge_and_track(self, current_fm, new_data, template_props):
        if current_fm.get('lock'): return current_fm, ""
        
        final_props = {**template_props, **new_data, **current_fm}
        changes = []
        watch = ['status_code', 'host_ip', 'webserver', 'title']

        for k, v in new_data.items():
            if v in [None, "", [], "N/A"]: continue
            old_v = current_fm.get(k)
            if k in watch and old_v and str(old_v) != str(v) and old_v != "N/A":
                changes.append(f"Cambio en `{k}`: {old_v} ➡️ {v}")
            if isinstance(v, list):
                final_props[k] = list(set(current_fm.get(k, []) + v))
            else:
                final_props[k] = v

        changelog = ""
        if changes:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            changelog = f"\n\n> [!INFO] **Changelog {now}**\n" + "\n".join([f"> - {c}" for c in changes])
        return final_props, changelog