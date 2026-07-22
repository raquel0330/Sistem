import cv2
import face_recognition
import pickle
import sqlite3
from datetime import datetime
import time

banco = sqlite3.connect("instance/banco.db")
cursor = banco.cursor()

# ===========================
# CARREGAR ASSINATURAS FACIAIS
# ===========================

with open("modelos/rostos.pkl", "rb") as arquivo:
    rostos = pickle.load(arquivo)

encodings = []
nomes = []
ids = []

for rosto in rostos:
    encodings.append(rosto["encoding"])
    nomes.append(rosto["nome"])
    ids.append(rosto["id"])

print(f"{len(nomes)} alunos carregados.")

# ===========================
# ABRIR CÂMERA
# ===========================

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Erro ao abrir a câmera.")
    exit()

while True:

    sucesso, frame = camera.read()

    if not sucesso:
        break

    # Reduz a imagem para processamento mais rápido
    frame_pequeno = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Converter BGR para RGB
    rgb = cv2.cvtColor(frame_pequeno, cv2.COLOR_BGR2RGB)

    # Localizar rostos
    localizacoes = face_recognition.face_locations(rgb)

    # Gerar encodings dos rostos encontrados
    encodings_camera = face_recognition.face_encodings(
        rgb,
        localizacoes
    )

    # Comparar cada rosto encontrado
    for encoding, (top, right, bottom, left) in zip(encodings_camera, localizacoes):

        resultados = face_recognition.compare_faces(
            encodings,
            encoding,
            tolerance=0.50
        )

        nome = "Desconhecido"

        if True in resultados:

            indice = resultados.index(True)
            nome = nomes[indice]

        # Voltar ao tamanho original
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Desenhar retângulo
        cv2.rectangle(
            frame,
            (left, top),
            (right, bottom),
            (0, 255, 0),
            2
        )

        # Escrever o nome
        cv2.putText(
            frame,
            nome,
            (left, top - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

    # Mostrar imagem
    cv2.imshow("Reconhecimento Facial", frame)

    tecla = cv2.waitKey(1)

    if tecla == 27:   # ESC
        break

camera.release()
cv2.destroyAllWindows()