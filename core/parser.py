import json

def ensure_list(data, default_val="N/A"):
    if not data or not isinstance(data, list) or len(data) == 0:
        return [str(default_val)]
    return [str(x) for x in data]

def parse_httpx_line(line):
    line = line.strip()
    if not line or not line.startswith('{'): return None
    try:
        d = json.loads(line)
        asn = d.get('asn', {})
        kb = d.get('knowledgebase', {})
        return {
            'timestamp': d.get('timestamp'),
            'host': d.get('host'),
            'url': d.get('url'),
            'final_url': d.get('final_url'),
            'scheme': d.get('scheme'),
            'port': str(d.get('port')),
            'host_ip': d.get('host_ip'),
            'a': ensure_list(d.get('a', [])),
            'aaaa': ensure_list(d.get('aaaa', [])),
            'cname': ensure_list(d.get('cname', [])),
            'resolvers': ensure_list(d.get('resolvers', [])),
            'as_number': asn.get('as_number'),
            'as_name': asn.get('as_name'),
            'as_country': asn.get('as_country'),
            'as_range': ensure_list(asn.get('as_range', [])),
            'webserver': d.get('webserver'),
            'tech': ensure_list(d.get('tech', [])),
            'status_code': d.get('status_code'),
            'title': d.get('title', 'N/A'),
            'page_type': kb.get('PageType'),
            'time': d.get('time'),
            'words': d.get('words'),
            'lines': d.get('lines'),
            'method': d.get('method'),
            'content_type': d.get('content_type'),
            'content_length': d.get('content_length'),
            'chain_status_codes': ensure_list(d.get('chain_status_codes', []), default_val="N/A")
        }
    except: return None