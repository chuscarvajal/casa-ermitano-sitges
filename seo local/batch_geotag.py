#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Geoetiqueta en lote varias fotos para GBP (GPS Sitges + descripcion SEO + nombre).
Salida -> media_gbp/<nombre_optimizado>.jpg
"""
import os, piexif
from PIL import Image
from fractions import Fraction

DL = r"C:\Users\Usuario\Downloads"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media_gbp")
LAT, LON = 41.2371, 1.8055  # Sitges centro (geoetiqueta segura, no revela direccion)
ARTIST = "Casa del Ermitano - Eduardo Mangas"
COPYRIGHT = "Casa del Ermitano (afijo RSCE 8110)"
KW_COMMON = "criadero chihuahua;chihuahua;Sitges;Vilanova i la Geltru;Casa del Ermitano;RSCE 8110"

# (archivo_entrada, nombre_salida, descripcion)
JOBS = [
    ("camada chihuaua.jpg",
     "camada-cachorros-chihuahua-disponibles-casa-del-ermitano-sitges.jpg",
     "Nueva camada de cachorros de Chihuahua de Casa del Ermitano (afijo RSCE 8110), criados en casa "
     "con pedigri LOE. Criadero de Chihuahua en Sitges y Vilanova i la Geltru."),
    ("WhatsApp Image 2026-06-22 at 10.49.36 (1).jpeg",
     "eduardo-mangas-criador-camada-cachorros-chihuahua-casa-del-ermitano.jpg",
     "Eduardo Mangas, criador de Casa del Ermitano (afijo RSCE 8110), con su camada de cachorros de "
     "Chihuahua. Criadero de Chihuahua en Sitges y Vilanova i la Geltru."),
    ("588733666_25044664085200230_6982500515773425501_n.jpg",
     "criadero-chihuahua-best-of-breed-podio-dinamarca-2025-casa-del-ermitano.jpg",
     "Chihuahua de Casa del Ermitano (afijo RSCE 8110) premiado Best of Breed en exposicion internacional "
     "en Dinamarca 2025. Criadero de Chihuahua con lineas campeonas en Sitges y Vilanova i la Geltru."),
    ("518375010_10171797293520052_2245354680932551891_n.jpg",
     "criadero-chihuahua-exposicion-danish-kennel-club-casa-del-ermitano.jpg",
     "Chihuahua de Casa del Ermitano exhibido en exposicion de la Danish Kennel Club. Criadero de Chihuahua "
     "con pedigri, afijo RSCE 8110, en Sitges y Vilanova i la Geltru."),
    # 18 oct 2026: quitadas las dos fotos del cachorro blanco en la mesa roja (camiseta gris):
    # es el perro de un amigo de Eduardo en Italia, no suyo. No volver a usarlas.
]

def dms(dec):
    dec = abs(dec); d = int(dec); m = int((dec-d)*60); s = round((dec-d-m/60)*3600,4)
    sf = Fraction(s).limit_denominator(10000)
    return ((d,1),(m,1),(sf.numerator,sf.denominator))

def process(inp, outname, desc):
    img = Image.open(inp).convert("RGB")
    gps = {
        piexif.GPSIFD.GPSVersionID:(2,3,0,0),
        piexif.GPSIFD.GPSLatitudeRef:"N", piexif.GPSIFD.GPSLatitude:dms(LAT),
        piexif.GPSIFD.GPSLongitudeRef:"E", piexif.GPSIFD.GPSLongitude:dms(LON),
    }
    zeroth = {
        piexif.ImageIFD.ImageDescription: desc.encode("utf-8"),
        piexif.ImageIFD.Artist: ARTIST.encode("utf-8"),
        piexif.ImageIFD.Copyright: COPYRIGHT.encode("utf-8"),
        piexif.ImageIFD.XPKeywords: KW_COMMON.encode("utf-16le"),
        piexif.ImageIFD.XPComment: desc.encode("utf-16le"),
    }
    exif_bytes = piexif.dump({"0th":zeroth,"Exif":{},"GPS":gps,"1st":{},"thumbnail":None})
    out = os.path.join(OUT_DIR, outname)
    img.save(out, "JPEG", quality=92, exif=exif_bytes)
    return out

if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    ok, miss = [], []
    for fn, outname, desc in JOBS:
        p = os.path.join(DL, fn)
        if not os.path.exists(p):
            miss.append(fn); continue
        out = process(p, outname, desc)
        ok.append(os.path.basename(out))
    print("=== OK ({}) ===".format(len(ok)))
    for o in ok: print("  +", o)
    if miss:
        print("=== NO ENCONTRADOS ===")
        for m in miss: print("  -", m)
