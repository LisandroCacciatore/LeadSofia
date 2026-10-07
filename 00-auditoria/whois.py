import socket, sys, json
def q(server, domain):
    try:
        s = socket.create_connection((server, 43), timeout=15)
        s.sendall((domain + "\r\n").encode())
        buf = b""
        while True:
            d = s.recv(4096)
            if not d: break
            buf += d
        s.close()
        return buf.decode("utf-8", "replace")
    except Exception as e:
        return f"ERROR {e}"
res = {}
for dom in ["sofiastrafile.com.ar", "sofiastrafile.ar"]:
    r = q("whois.nic.ar", dom)
    res[dom] = r
    print("="*70); print(dom); print(r[:900])
for dom in ["sofiastrafile.com", "strafile.com", "sofia-strafile.com"]:
    r = q("whois.verisign-grs.com", dom)
    res[dom] = r
    print("="*70); print(dom)
    print("\n".join([l for l in r.splitlines() if any(k in l for k in ("Domain Name","No match","Creation","Registrar:","Expiry","Registrant"))][:8]) or r[:400])
open("00-auditoria/whois.json","w",encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=2))
