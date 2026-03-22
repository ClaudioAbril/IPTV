from collections import defaultdict

# Ruta del archivo original
file_path = r"C:\Users\Usuario\Downloads\canales-4k.m3u"

# Diccionario para agrupar por país
channels_by_country = defaultdict(list)
seen = set()

with open(file_path, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

for i in range(len(lines)):
    if lines[i].startswith("#EXTINF"):
        # Extraer país del tvg-id
        parts = lines[i].split('tvg-id="')
        if len(parts) > 1:
            tvg_id = parts[1].split('"')[0]
            country = tvg_id.split(".")[-1].split("@")[0]  # ej: "ar", "ec", "us"
        else:
            country = "Unknown"

        # Canal + URL
        channel_block = lines[i] + "\n" + (lines[i+1] if i+1 < len(lines) else "")

        # Evitar duplicados
        if channel_block not in seen:
            seen.add(channel_block)
            channels_by_country[country].append(channel_block)

# Crear archivo ordenado por país
output_file = r"C:\Users\Usuario\Downloads\canales_por_pais.m3u"
with open(output_file, "w", encoding="utf-8") as out:
    out.write("#EXTM3U\n")
    for country in sorted(channels_by_country.keys()):
        out.write(f"\n# --- {country.upper()} ---\n")
        for channel in channels_by_country[country]:
            out.write(channel + "\n")

print("Archivo generado:", output_file)
