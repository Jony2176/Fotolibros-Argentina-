from bs4 import BeautifulSoup
import os

HTML_FILE = "debug_upload_fail.html"

if not os.path.exists(HTML_FILE):
    print("Archivo no encontrado")
    exit()

with open(HTML_FILE, "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

print("\n=== CONTENIDO MODAL (.windowComp) ===")
modals = soup.select(".windowComp")
for modal in modals:
    print(f"MODAL TEXT: {modal.get_text(separator='|', strip=True)}")
    # Buscar botones dentro del modal
    for btn in modal.find_all(["div", "button", "span"]):
        if btn.get("class"):
            print(f"  -> Posible botón: {btn.name} class={btn.get('class')} text='{btn.get_text(strip=True)}'")
# Buscar botones o elementos clickeables que parezcan de subida
for elem in soup.find_all(["button", "div", "span", "a"]):
    text = elem.get_text().lower()
    classes = str(elem.get("class", [])).lower()
    attrs = str(elem.attrs).lower()
    
    keywords = ["add", "agregar", "subir", "upload", "foto", "photo", "image", "img"]
    
    if any(k in text or k in classes or k in attrs for k in keywords):
        # Filtrar elementos irrelevantes
        if "footer" in classes or "menu" in classes: continue
        
        print(f"Elem: <{elem.name}> Text: '{elem.get_text()[:30].strip()}' Class: {elem.get('class')} ID: {elem.get('id')}")

print("\n=== IMAGES ===")
print(f"Total imágenes: {len(soup.find_all('img'))}")
