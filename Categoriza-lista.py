import re

def procesar_m3u(archivo_entrada, archivo_salida):
    mapeo_paises = {
        # América
        'AR': 'Argentina', 'BO': 'Bolivia', 'BR': 'Brasil', 'CL': 'Chile', 'CO': 'Colombia',
        'EC': 'Ecuador', 'PY': 'Paraguay', 'PE': 'Perú', 'UY': 'Uruguay', 'VE': 'Venezuela',
        'CA': 'Canadá', 'US': 'EE.UU.', 'MX': 'México', 'CR': 'Costa Rica', 'CU': 'Cuba',
        'DO': 'Rep. Dominicana', 'SV': 'El Salvador', 'GT': 'Guatemala', 'HN': 'Honduras',
        'NI': 'Nicaragua', 'PA': 'Panamá', 'PR': 'Puerto Rico',
        # Europa
        'ES': 'España', 'FR': 'Francia', 'IT': 'Italia', 'DE': 'Alemania', 'UK': 'Reino Unido', 
        'GB': 'Reino Unido', 'PT': 'Portugal', 'RU': 'Rusia', 'UA': 'Ucrania',
        # Asia/Otros
        'CN': 'China', 'JP': 'Japón', 'KR': 'Corea del Sur', 'IL': 'Israel', 'IN': 'India'
    }

    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
    except FileNotFoundError:
        print(f"Error: No se encontró {archivo_entrada}")
        return

    canales_unicos = {}
    pais_por_seccion = None
    
    i = 0
    while i < len(lineas):
        linea = lineas[i].strip()
        
        # 1. Detectar cambio de país por sección (# --- AR ---)
        match_seccion = re.search(r'#\s*---\s*([A-Z]{2})\s*---', linea)
        if match_seccion:
            pais_por_seccion = match_seccion.group(1).upper()
            i += 1
            continue

        if linea.startswith('#EXTINF:'):
            info_linea = linea
            
            # 2. Detectar país por tvg-id (ej: AmericaTV.ar@SD)
            match_id = re.search(r'tvg-id="[^"]+\.([a-z]{2})@', info_linea, re.IGNORECASE)
            codigo_pais = None
            
            if match_id:
                codigo_pais = match_id.group(1).upper()
            elif pais_por_seccion:
                codigo_pais = pais_por_seccion
            
            nombre_pais = mapeo_paises.get(codigo_pais, codigo_pais) if codigo_pais else "General"

            # Extraer categoría original
            match_group = re.search(r'group-title="([^"]*)"', info_linea)
            cat_original = match_group.group(1) if match_group else ""
            
            # Construir nuevo group-title: "País, Categoría"
            if not cat_original or cat_original.strip() == "":
                nueva_cat = nombre_pais
            elif nombre_pais.lower() in cat_original.lower():
                nueva_cat = cat_original # Evita "Argentina, Argentina"
            else:
                nueva_cat = f"{nombre_pais}, {cat_original}"

            # Reemplazar en la línea
            if match_group:
                info_linea = info_linea.replace(f'group-title="{match_group.group(1)}"', f'group-title="{nueva_cat}"')
            else:
                # Si no tiene group-title, lo insertamos antes de la coma del nombre
                partes = info_linea.rsplit(',', 1)
                info_linea = f'{partes[0]} group-title="{nueva_cat}",{partes[1]}'

            # Recolectar opciones y URL
            opts = []
            i += 1
            while i < len(lineas) and lineas[i].startswith('#EXTVLCOPT:'):
                opt = lineas[i].strip()
                if "network-caching" not in opt and "gnutls-verify-trust" not in opt:
                    opts.append(opt)
                i += 1
            
            if i < len(lineas):
                url = lineas[i].strip()
                nombre_canal = info_linea.split(',')[-1].strip()
                
                # Unificar duplicados por URL
                if url not in canales_unicos:
                    opts.append("#EXTVLCOPT:network-caching=5000")
                    opts.append("#EXTVLCOPT:gnutls-verify-trust=0")
                    canales_unicos[url] = {'info': info_linea, 'opts': opts}
            
        i += 1

    # Escribir resultado
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n\n")
        for url, data in canales_unicos.items():
            f.write(f"{data['info']}\n")
            for o in data['opts']:
                f.write(f"{o}\n")
            f.write(f"{url}\n\n")

procesar_m3u('canales.m3u', 'canales_final.m3u')
print("Proceso finalizado. Revisa 'canales_final.m3u'")