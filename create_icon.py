from PIL import Image, ImageDraw, ImageFont
import os

# Crea un'icona LEGO stilizzata
size = 256
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Colore rosso LEGO
lego_red = (196, 30, 58)
lego_yellow = (255, 205, 3)
lego_white = (255, 255, 255)
shadow = (100, 20, 30)

# Disegna un mattoncino LEGO stilizzato
# Base del mattoncino
brick_width = 200
brick_height = 120
brick_x = (size - brick_width) // 2
brick_y = (size - brick_height) // 2 + 30

# Ombra
draw.rounded_rectangle(
    [(brick_x + 5, brick_y + 5), (brick_x + brick_width + 5, brick_y + brick_height + 5)],
    radius=10, fill=shadow
)

# Mattoncino principale
draw.rounded_rectangle(
    [(brick_x, brick_y), (brick_x + brick_width, brick_y + brick_height)],
    radius=10, fill=lego_red
)

# Studs (bottoni) sopra il mattoncino
stud_radius = 20
stud_spacing = 50
stud_y = brick_y - 15

for i in range(4):
    stud_x = brick_x + 25 + (i * stud_spacing)
    # Ombra stud
    draw.ellipse(
        [(stud_x - stud_radius + 2, stud_y - stud_radius + 2),
         (stud_x + stud_radius + 2, stud_y + stud_radius + 2)],
        fill=shadow
    )
    # Stud
    draw.ellipse(
        [(stud_x - stud_radius, stud_y - stud_radius),
         (stud_x + stud_radius, stud_y + stud_radius)],
        fill=lego_red
    )
    # Highlight sullo stud
    draw.ellipse(
        [(stud_x - stud_radius + 5, stud_y - stud_radius + 5),
         (stud_x - stud_radius + 12, stud_y - stud_radius + 12)],
        fill=(255, 100, 120)
    )

# Aggiungi highlight sul mattoncino
draw.rounded_rectangle(
    [(brick_x + 10, brick_y + 10), (brick_x + 80, brick_y + 30)],
    radius=5, fill=(255, 100, 120, 150)
)

# Salva l'icona in vari formati
output_path = 'lego_icon.png'
img.save(output_path, 'PNG')
print(f"✅ Icona PNG creata: {output_path}")

# Crea anche versione ICO (Windows)
sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
ico_images = []
for size_tuple in sizes:
    resized = img.resize(size_tuple, Image.Resampling.LANCZOS)
    ico_images.append(resized)

ico_path = 'lego_icon.ico'
ico_images[0].save(ico_path, format='ICO', sizes=[(s[0], s[1]) for s in sizes])
print(f"✅ Icona ICO creata: {ico_path}")

print("\n🎨 Icona LEGO creata con successo!")
