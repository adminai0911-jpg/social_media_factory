import json, re

demands = []
with open(r'C:\Users\drsau\.gemini\antigravity-ide\brain\f1e0bf9b-6cae-43f1-8406-d597eba54773\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8-sig', errors='replace') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        try:
            obj = json.loads(line)
            if obj.get('type') == 'USER_INPUT' and obj.get('source') == 'USER_EXPLICIT':
                content = obj.get('content','')
                match = re.search(r'<USER_REQUEST>(.*?)</USER_REQUEST>', content, re.DOTALL)
                if match:
                    req = match.group(1).strip()
                    ts = obj.get('created_at', '')
                    if '2026-06-16' in ts:
                        demands.append({'ts': ts, 'req': req[:400]})
        except:
            pass

with open('output.txt', 'w', encoding='utf-8') as out_f:
    for i, d in enumerate(demands):
        out_f.write("--- DEMAND %d [%s] ---\n" % (i+1, d['ts']))
        out_f.write(d['req'] + "\n")
        out_f.write("\n")
