from rembg import remove
from PIL import Image

# Caminhos dos arquivos
input_path = "logo.png"              # imagem original
output_path = "logo.png"  # imagem sem fundo

# Abrir a imagem original
input_image = Image.open(input_path)

# Remover fundo
output_image = remove(input_image)

# Salvar resultado
output_image.save(output_path)

print("✅ Fundo removido com sucesso! Arquivo salvo como:", output_path)
