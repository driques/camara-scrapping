import sys
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI(title="Diputados Scraper API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScrapeRequest(BaseModel):
    url: str

@app.post("/api/v1/proyectos")
async def obtener_proyectos(request: ScrapeRequest):
    url = request.url
    print(f"--> Recibida petición para: {url}")
    
    if "camara.cl" not in url:
        raise HTTPException(status_code=400, detail="La URL no parece ser de camara.cl")

    async with async_playwright() as p:
        print("Iniciando navegador...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print(f"Navegando a la URL...")
            await page.goto(url, timeout=40000)
            selector_id = "#ContentPlaceHolder1_ContentPlaceHolder1_DetallePlaceHolder_ddlAnnos"
            try:
                await page.wait_for_selector(selector_id, timeout=10000)
            except:
                raise HTTPException(status_code=404, detail="No se encontró el selector de años en la página.")

            periodos_str = "No detectado"
            try:
                ul_periodos = page.locator("ul", has=page.locator("li", has_text="Periodos parlamentarios"))
                if await ul_periodos.count() > 0:
                    items = await ul_periodos.locator("li").all_inner_texts()
                    limpios = [x.strip() for x in items if "Periodos" not in x and x.strip()]
                    periodos_str = ", ".join(limpios)
            except Exception as e:
                print(f"Nota: No se extrajeron periodos ({e})")

            opciones = await page.locator(f"{selector_id} option").all()
            anos = []
            for opt in opciones:
                val = await opt.get_attribute("value")
                if val: anos.append(val)

            print(f"Años encontrados: {anos}")
            datos_totales = []

            for anno in anos:
                print(f"Procesando año {anno}...")
                await page.evaluate(f"document.querySelector('{selector_id}').value = '{anno}';")
                await page.evaluate(f"setTimeout('__doPostBack(\\'{selector_id.replace('#', '')}\\',\\'\\')', 0)")
                
                try:
                    await page.wait_for_load_state("networkidle", timeout=10000)
                except:
                    pass 
                await asyncio.sleep(0.5)
                filas = await page.locator("table.tabla tbody tr").all()
                for fila in filas:
                    celdas = await fila.locator("td").all()
                    if len(celdas) >= 4:
                        datos_totales.append({
                            "año": anno,
                            "tipo": "Admisible",
                            "boletin": (await celdas[0].inner_text()).strip(),
                            "fecha": (await celdas[1].inner_text()).strip(),
                            "titulo": (await celdas[2].inner_text()).strip(),
                            "estado": (await celdas[3].inner_text()).strip()
                        })
                try:
                    btn_inad = page.get_by_role("link", name="Inadmisibles")
                    if await btn_inad.is_visible():
                        await btn_inad.click()
                        await asyncio.sleep(1)
                        
                        vacio = await page.locator("h4", has_text="No existen Mociones Inadmisibles").is_visible()
                        if not vacio:
                            filas_inad = await page.locator("table.tabla tbody tr").all()
                            for fila in filas_inad:
                                celdas = await fila.locator("td").all()
                                if len(celdas) >= 4:
                                    datos_totales.append({
                                        "año": anno,
                                        "tipo": "Inadmisible",
                                        "boletin": (await celdas[0].inner_text()).strip(),
                                        "fecha": "",
                                        "titulo": (await celdas[2].inner_text()).strip(),
                                        "estado": (await celdas[3].inner_text()).strip()
                                    })
                except Exception as e:
                    print(f"Error leve en inadmisibles: {e}")

            await browser.close()
            print("Extracción finalizada con éxito.")
            
            return {
                "status": "success",
                "diputado": {"periodos": periodos_str, "url": url},
                "total": len(datos_totales),
                "data": datos_totales
            }

        except Exception as e:
            await browser.close()
            print(f"Error CRÍTICO: {e}")
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("--- INICIANDO SERVIDOR (Modo Producción Local) ---")
    uvicorn.run(app, host="127.0.0.1", port=8000)
