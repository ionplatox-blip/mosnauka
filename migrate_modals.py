#!/usr/bin/env python3
"""Batch-migrate: replace inline modals with contact-modal.js."""
import os, re, sys, glob
ROOT = '/Users/shakhgildyangy/mosnauka'

def migrate_entity(fp, dry=False):
    with open(fp,'r',encoding='utf-8') as f: c=f.read()
    for m in ['<!-- Request Modal -->','<div class="modal-overlay" id="requestModal">']:
        p=c.find(m)
        if p!=-1: break
    else: return False
    b=c[:p].rstrip()
    b=re.sub(r'\s*\.modal-overlay\s*\{[^}]*\}','',b)
    b=re.sub(r'\s*\.modal-overlay\.active\s*\{[^}]*\}','',b)
    b=re.sub(r'\s*\.modal\s+\w[^{]*\{[^}]*\}','',b)
    b=re.sub(r'\s*\.modal\s*\{[^}]*\}','',b)
    b=re.sub(r'<style>\s*</style>','',b)
    r=b+'\n<script src="../contact-modal.js"></script>\n</body>\n</html>\n'
    if not dry:
        with open(fp,'w',encoding='utf-8') as f: f.write(r)
    return True

def migrate_passport(fp, dry=False):
    with open(fp,'r',encoding='utf-8') as f: c=f.read()
    c=re.sub(r'\s*<!-- Request Modal -->\s*','\n',c)
    c=re.sub(r'<div id="requestModal"[^>]*>.*?</div>\s*</div>\s*</div>','',c,flags=re.DOTALL)
    c=re.sub(r'<script>\s*(?:window\.addEventListener[^}]+\}\);)?\s*function openRequestModal\(context\).*?</script>','',c,flags=re.DOTALL)
    if 'contact-modal.js' not in c:
        c=c.replace('</body>','<script src="contact-modal.js"></script>\n</body>')
    if not dry:
        with open(fp,'w',encoding='utf-8') as f: f.write(c)
    return True

def find_entities():
    fs=[]
    for d in os.listdir(ROOT):
        sd=os.path.join(ROOT,d)
        if not os.path.isdir(sd) or d in ('dist','node_modules','data','backend','public'): continue
        for p in ['sci_*.html','lab_*.html','proj_*.html','rid_*.html']:
            fs.extend(glob.glob(os.path.join(sd,p)))
    return sorted(fs)

def main():
    a=sys.argv[1:]
    dry='--dry-run' in a
    de='--entities' in a or '--all' in a
    dp='--passports' in a or '--all' in a
    if not de and not dp: print("Usage: --entities|--passports|--all [--dry-run]"); return
    if dry: print("DRY RUN\n")
    if de:
        fs=find_entities(); print(f"Entity files: {len(fs)}")
        ok=sk=er=0
        for f in fs:
            try:
                if migrate_entity(f,dry): ok+=1
                else: sk+=1
            except Exception as x: er+=1; print(f"  ERR {os.path.relpath(f,ROOT)}: {x}")
        print(f"  OK:{ok} Skip:{sk} Err:{er}\n")
    if dp:
        fs=sorted(glob.glob(os.path.join(ROOT,'passport-*.html')))
        print(f"Passport files: {len(fs)}")
        ok=er=0
        for f in fs:
            try: migrate_passport(f,dry); ok+=1
            except Exception as x: er+=1; print(f"  ERR {os.path.relpath(f,ROOT)}: {x}")
        print(f"  OK:{ok} Err:{er}\n")
    print("Done!" if not dry else "Dry run done.")

if __name__=='__main__': main()
