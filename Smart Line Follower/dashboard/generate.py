#!/usr/bin/env python3
"""
Generador de assets de ejemplo para el dashboard
Crea imágenes placeholder cuando no se tienen los assets reales
Requiere: Pillow (PIL)

Instalación: pip install Pillow
Uso: python generate_assets.py
"""

import os
from PIL import Image, ImageDraw, ImageFont

# Configuración
ASSETS_DIR = "assets"
COLORS = {
    "background": "#10232A",
    "panel": "#3D4D55",
    "text": "#D3C3B9",
    "accent": "#B58863",
    "secondary": "#A79E9C",
    "black": "#18161B",
    "green": "#00FF00",
    "red": "#FF0000"
}

def create_directory():
    """Crea el directorio de assets si no existe"""
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)
        print(f"✅ Directorio '{ASSETS_DIR}' creado")
    else:
        print(f"ℹ️  Directorio '{ASSETS_DIR}' ya existe")

def create_arrow_images():
    """Crea imágenes de flechas direccionales"""
    size = (100, 100)
    arrows = {
        "up": "↑",
        "down": "↓",
        "left": "←",
        "right": "→"
    }
    
    for direction, symbol in arrows.items():
        # Flecha normal
        img = Image.new('RGBA', size, COLORS["secondary"])
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        # Centrar texto
        bbox = draw.textbbox((0, 0), symbol, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2 - 10)
        
        draw.text(position, symbol, fill=COLORS["text"], font=font)
        
        # Agregar borde redondeado
        draw.rounded_rectangle([(0, 0), size], radius=15, outline=COLORS["accent"], width=3)
        
        img.save(os.path.join(ASSETS_DIR, f"arrow_{direction}.png"))
        print(f"✅ Creado: arrow_{direction}.png")
        
        # Flecha activa (verde)
        img_active = Image.new('RGBA', size, COLORS["accent"])
        draw_active = ImageDraw.Draw(img_active)
        draw_active.text(position, symbol, fill=COLORS["text"], font=font)
        draw_active.rounded_rectangle([(0, 0), size], radius=15, outline=COLORS["green"], width=4)
        
        img_active.save(os.path.join(ASSETS_DIR, f"arrow_{direction}_active.png"))
        print(f"✅ Creado: arrow_{direction}_active.png")

def create_function_buttons():
    """Crea botones de funciones especiales"""
    size = (200, 200)
    
    functions = {
        1: ("🚀", "Turbo"),
        2: ("🤖", "Auto"),
        3: ("🛡️", "Shield"),
        4: ("⚠️", "Stop")
    }
    
    for num, (emoji, label) in functions.items():
        img = Image.new('RGBA', size, COLORS["panel"])
        draw = ImageDraw.Draw(img)
        
        try:
            font_emoji = ImageFont.truetype("seguiemj.ttf", 80)
            font_label = ImageFont.truetype("arial.ttf", 24)
        except:
            font_emoji = ImageFont.load_default()
            font_label = ImageFont.load_default()
        
        # Emoji centrado arriba
        bbox = draw.textbbox((0, 0), emoji, font=font_emoji)
        text_width = bbox[2] - bbox[0]
        emoji_pos = ((size[0] - text_width) // 2, 40)
        draw.text(emoji_pos, emoji, fill=COLORS["accent"], font=font_emoji)
        
        # Label centrado abajo
        bbox = draw.textbbox((0, 0), label, font=font_label)
        text_width = bbox[2] - bbox[0]
        label_pos = ((size[0] - text_width) // 2, 140)
        draw.text(label_pos, label, fill=COLORS["text"], font=font_label)
        
        # Borde
        draw.rounded_rectangle([(0, 0), size], radius=20, outline=COLORS["accent"], width=4)
        
        img.save(os.path.join(ASSETS_DIR, f"func{num}.png"))
        print(f"✅ Creado: func{num}.png")

def create_camera_placeholder():
    """Crea placeholder para cámara"""
    size = (800, 600)
    img = Image.new('RGB', size, COLORS["black"])
    draw = ImageDraw.Draw(img)
    
    # Dibujar icono de cámara simple
    camera_size = 150
    camera_pos = ((size[0] - camera_size) // 2, (size[1] - camera_size) // 2 - 50)
    
    # Cuerpo de cámara
    draw.rounded_rectangle(
        [camera_pos, (camera_pos[0] + camera_size, camera_pos[1] + camera_size - 30)],
        radius=10,
        fill=COLORS["panel"],
        outline=COLORS["accent"],
        width=3
    )
    
    # Lente
    lens_center = (camera_pos[0] + camera_size // 2, camera_pos[1] + camera_size // 2 - 15)
    lens_radius = 40
    draw.ellipse(
        [
            (lens_center[0] - lens_radius, lens_center[1] - lens_radius),
            (lens_center[0] + lens_radius, lens_center[1] + lens_radius)
        ],
        fill=COLORS["secondary"],
        outline=COLORS["accent"],
        width=3
    )
    
    # Texto
    try:
        font = ImageFont.truetype("arial.ttf", 32)
    except:
        font = ImageFont.load_default()
    
    text = "📷 Cámara Desconectada"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_pos = ((size[0] - text_width) // 2, camera_pos[1] + camera_size + 30)
    draw.text(text_pos, text, fill=COLORS["text"], font=font)
    
    img.save(os.path.join(ASSETS_DIR, "camera_placeholder.jpg"))
    print("✅ Creado: camera_placeholder.jpg")

def create_login_background():
    """Crea fondo para pantalla de login"""
    size = (1200, 800)
    img = Image.new('RGB', size, COLORS["background"])
    draw = ImageDraw.Draw(img)
    
    # Crear degradado visual simple con círculos
    for i in range(5):
        radius = 100 + i * 80
        alpha = 20 - i * 3
        overlay = Image.new('RGBA', size, (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        
        # Círculo en esquina superior derecha
        draw_overlay.ellipse(
            [(size[0] - radius, -radius//2), (size[0] + radius//2, radius)],
            fill=(*hex_to_rgb(COLORS["accent"]), alpha)
        )
        
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    # Título decorativo
    try:
        font = ImageFont.truetype("arial.ttf", 48)
    except:
        font = ImageFont.load_default()
    
    text = "Smart Line Follower"
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_pos = ((size[0] - text_width) // 2, 100)
    
    # Sombra
    draw.text((text_pos[0] + 3, text_pos[1] + 3), text, fill=COLORS["black"], font=font)
    # Texto principal
    draw.text(text_pos, text, fill=COLORS["accent"], font=font)
    
    img.save(os.path.join(ASSETS_DIR, "bg_login.jpg"))
    print("✅ Creado: bg_login.jpg")

def create_icon():
    """Crea icono de la aplicación"""
    size = (128, 128)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Círculo de fondo
    draw.ellipse([(10, 10), (118, 118)], fill=COLORS["accent"])
    
    # Dibujar línea (representando seguidor de línea)
    line_width = 8
    draw.line([(30, 64), (98, 64)], fill=COLORS["text"], width=line_width)
    
    # Dibujar "carro" simple
    car_color = COLORS["panel"]
    # Cuerpo
    draw.rounded_rectangle([(45, 50), (85, 70)], radius=5, fill=car_color)
    # Ruedas
    draw.ellipse([(48, 68), (58, 78)], fill=COLORS["text"])
    draw.ellipse([(72, 68), (82, 78)], fill=COLORS["text"])
    
    img.save(os.path.join(ASSETS_DIR, "icon.png"))
    print("✅ Creado: icon.png")

def hex_to_rgb(hex_color):
    """Convierte color hex a tupla RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def main():
    """Función principal"""
    print("🎨 Generador de Assets para Smart Line Follower Dashboard")
    print("=" * 60)
    
    try:
        # Verificar Pillow
        print("\n📦 Verificando dependencias...")
        print("✅ Pillow instalado correctamente")
        
        # Crear directorio
        print("\n📁 Creando directorio de assets...")
        create_directory()
        
        # Generar assets
        print("\n🎨 Generando imágenes...")
        print("\n1️⃣ Flechas direccionales:")
        create_arrow_images()
        
        print("\n2️⃣ Botones de funciones:")
        create_function_buttons()
        
        print("\n3️⃣ Placeholder de cámara:")
        create_camera_placeholder()
        
        print("\n4️⃣ Fondo de login:")
        create_login_background()
        
        print("\n5️⃣ Icono de aplicación:")
        create_icon()
        
        print("\n" + "=" * 60)
        print("✅ ¡Todos los assets han sido generados exitosamente!")
        print(f"📂 Los archivos se encuentran en: {os.path.abspath(ASSETS_DIR)}")
        print("\n💡 Puedes reemplazar estos assets con tus propias imágenes personalizadas")
        
    except ImportError:
        print("❌ Error: Pillow no está instalado")
        print("📦 Instálalo con: pip install Pillow")
        return 1
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())