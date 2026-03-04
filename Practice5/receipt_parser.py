import re, json
from pathlib import Path

def money_to_float(s: str) -> float:
    return float(s.replace(" ", "").replace(",", "."))

MONEY = r"\d{1,3}(?: \d{3})*(?:[.,]\d{2})"     
QTY   = r"\d+(?:[.,]\d+)?"      



text = Path("raw.txt").read_text(encoding="utf-8", errors="ignore")
lines = [l.strip() for l in text.splitlines() if l.strip()]

prices_raw = re.findall(MONEY, text)
prices = [money_to_float(x) for x in prices_raw]

items = []
i = 0
while i < len(lines):
    if re.fullmatch(r"\d+\.", lines[i]):  
        name = lines[i + 1] if i + 1 < len(lines) else ""

        qty = None
        unit_price = None
        line_total = None

        qty_line = lines[i + 2] if i + 2 < len(lines) else ""

        m = re.search(rf"({QTY})\s*x\s*({MONEY})", qty_line)
        if m:
            qty = float(m.group(1).replace(",", "."))
            unit_price = money_to_float(m.group(2))

        tot_line = lines[i + 3] if i + 3 < len(lines) else ""
        m2 = re.fullmatch(MONEY, tot_line)
        if m2:
            line_total = money_to_float(m2.group(0))

        items.append({
            "name": name,
            "qty": qty,
            "unit_price": unit_price,
            "line_total": line_total,
        })
        i += 1
    i += 1

product_names = [x["name"] for x in items]

m_total = re.search(rf"^ИТОГО:\s*({MONEY})\s*$", text, flags=re.M)
if m_total:
    total = money_to_float(m_total.group(1))
else:
    total = round(sum(x["line_total"] for x in items if x["line_total"] is not None), 2) or None

datetime = re.search(r"Время:\s*(\d{2}[./]\d{2}[./]\d{4})\s+(\d{2}:\d{2}:\d{2})", text)
date = datetime.group(1) if datetime else None
time = datetime.group(2) if datetime else None

payment_method = None
if re.search(r"Банковская карта", text, re.I):
    payment_method = "Карта"
elif re.search(r"\bНалич", text, re.I):
    payment_method = "Наличные"

out = {
    "date": date,
    "time": time,
    "payment_method": payment_method,
    "prices": prices,                 
    "product_names": product_names,   
    "items": items,                   
    "total": total,
}

print(json.dumps(out, ensure_ascii=False, indent=2))