from PIL import Image

# Caminho para a imagem dentro da pasta 'static'
img_path = "logo1.png"  # Caminho correto, pois já estamos na pasta 'static'
img = Image.open(img_path)

# Converter para RGBA para suportar transparência
img = img.convert("RGBA")

# Processar a imagem para remover o fundo branco
data = img.getdata()

# Criar novos dados de imagem com fundo transparente para os pixels brancos
new_data = []
for item in data:
    if item[0] in range(200, 256) and item[1] in range(200, 256) and item[2] in range(200, 256):
        new_data.append((255, 255, 255, 0))  # Tornar os pixels brancos transparentes
    else:
        new_data.append(item)

# Aplicar os novos dados e salvar a imagem resultante
img.putdata(new_data)
img.save("logo_no_bg.png")  # Imagem será salva diretamente na pasta 'static'

