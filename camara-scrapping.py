import time
import pandas as pd
import matplotlib.pyplot as plt
from playwright.sync_api import sync_playwright

def generar_graficos(datos, periodos):
    if not datos:
        print("No hay datos suficientes para generar gráficos.")
        return

    print("\n--- Generando Gráficos ---")
    
    df = pd.DataFrame(datos)
    df['estado'] = df['estado'].str.strip()

    conteo = df['estado'].value_counts()
    print("Resumen de estados encontrados:")
    print(conteo)

    texto_periodos = f"Periodos en ejercicio: {periodos}" if periodos else "Periodos no detectados"

    plt.figure(figsize=(12, 8))
    colores = []
    for estado in conteo.index:
        est_lower = estado.lower()
        if 'publicado' in est_lower: colores.append('#2ecc71')
        elif 'archivado' in est_lower: colores.append('#95a5a6')
        elif 'tramitación' in est_lower: colores.append('#3498db')
        elif 'inadmisible' in est_lower: colores.append('#e74c3c')
        else: colores.append('#f1c40f')

    barras = conteo.plot(kind='bar', color=colores, edgecolor='black')
    
    plt.title('Cantidad de Proyectos por Estado', fontsize=16, pad=20)
    plt.suptitle(texto_periodos, fontsize=12, color='#555555')
    plt.xlabel('Estado del Proyecto', fontsize=12)
    plt.ylabel('Cantidad', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.subplots_adjust(top=0.88)

    for i, v in enumerate(conteo):
        plt.text(i, v + 0.1, str(v), ha='center', va='bottom', fontweight='bold')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig('proyectos_barras.png')
    print("Gráfico guardado: proyectos_barras.png")
    plt.close()

    plt.figure(figsize=(10, 10))
    
    conteo.plot(
        kind='pie',
        autopct='%1.1f%%',
        startangle=140,
        colors=colores,
        wedgeprops={'edgecolor': 'black'}
    )
    plt.ylabel('')
    plt.title('Distribución Porcentual de Proyectos', fontsize=16)
    plt.suptitle(texto_periodos, fontsize=12, color='#555555')
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig('proyectos_torta.png')
    print("Gráfico guardado: proyectos_torta.png")
    plt.close()

def obtener_proyectos():
    url = input("Ingrese la URL de la ficha del diputado: ").strip()
    
    if not url:
        print("Error: No ingresaste ninguna URL.")
        return

    datos_totales = []
    periodos_str = ""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print(f"--- Intentando acceder a: {url} ---")
        
        try:
            page.goto(url, timeout=15000)
            selector_id = "#ContentPlaceHolder1_ContentPlaceHolder1_DetallePlaceHolder_ddlAnnos"
            page.wait_for_selector(selector_id, timeout=5000)

            try:
                ul_periodos = page.locator("ul", has=page.locator("li", has_text="Periodos parlamentarios"))
                items_periodos = ul_periodos.locator("li").all_inner_texts()
                lista_limpia = [p.strip() for p in items_periodos if "Periodos" not in p and p.strip()]
                periodos_str = ", ".join(lista_limpia)
                print(f"Periodos parlamentarios encontrados: {periodos_str}")
            except Exception:
                print("No se pudieron extraer los periodos parlamentarios.")

        except Exception as e:
            print(f"ERROR CRÍTICO: No se pudo cargar la página o la URL no es válida.")
            print(f"Detalle del error: {e}")
            browser.close()
            return

        opciones = page.locator(f"{selector_id} option").all()
        anos_disponibles = [opt.get_attribute("value") for opt in opciones]
        anos_disponibles = [a for a in anos_disponibles if a]
        
        print(f"Años encontrados: {anos_disponibles}")

        for anno in anos_disponibles:
            print(f"Procesando año: {anno}...")
            
            page.select_option(selector_id, value=anno)
            
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except:
                print("Nota: Timeout esperando red, continuando...")
            
            time.sleep(1)

            filas = page.locator("table.tabla tbody tr").all()
            
            for fila in filas:
                celdas = fila.locator("td").all()
                if len(celdas) >= 4:
                    boletin = celdas[0].inner_text().strip()
                    estado = celdas[3].inner_text().strip()
                    titulo = celdas[2].inner_text().strip()
                    fecha = celdas[1].inner_text().strip()
                    
                    datos_totales.append({
                        "año": anno,
                        "tipo": "Admisible",
                        "boletin": boletin,
                        "fecha": fecha,
                        "titulo": titulo,
                        "estado": estado
                    })

            try:
                btn_inadmisibles = page.get_by_role("link", name="Inadmisibles")
                if btn_inadmisibles.is_visible():
                    btn_inadmisibles.click()
                    time.sleep(1)
                    
                    no_existen = page.locator("h4", has_text="No existen Mociones Inadmisibles").is_visible()
                    
                    if not no_existen:
                        filas_inad = page.locator("table.tabla tbody tr").all()
                        for fila in filas_inad:
                            celdas = fila.locator("td").all()
                            if len(celdas) >= 4:
                                boletin = celdas[0].inner_text().strip()
                                titulo = celdas[2].inner_text().strip()
                                estado_inad = celdas[3].inner_text().strip()
                                
                                datos_totales.append({
                                    "año": anno,
                                    "tipo": "Inadmisible",
                                    "boletin": boletin,
                                    "fecha": "",
                                    "titulo": titulo,
                                    "estado": estado_inad
                                })
            except Exception:
                pass

        browser.close()
        
        print(f"\n--- Extracción finalizada. Total proyectos: {len(datos_totales)} ---")
        generar_graficos(datos_totales, periodos_str)

if __name__ == "__main__":
    obtener_proyectos()
