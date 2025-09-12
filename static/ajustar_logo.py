from rembg import remove
from PIL import Image, ImageOps

# Caminho da imagem original
input_path = "logo.png"               # coloque o nome da sua imagem aqui
output_path = "logo.png"  # saída final sem fundo

# Abrir imagem original
input_image = Image.open(input_path)

# Remover fundo
sem_fundo = remove(input_image)

# Uniformizar cor (azul #007BFF por exemplo)
azul = (0, 123, 255, 255)  # RGBA
logo_colorida = ImageOps.colorize(sem_fundo.convert("L"), black=(0, 0, 0, 0), white=azul)

# Salvar resultado
logo_colorida.save(output_path)

print("✅ Logo ajustada e salva como:", output_path)
