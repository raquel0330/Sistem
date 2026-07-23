import sqlite3
import face_recognition
import pickle
import os


# ===========================
# CONFIGURAÇÕES
# ===========================

PASTA_FOTOS = "static/fotos"

ARQUIVO_ROSTOS = "modelos/rostos.pkl"


def gerar_rostos():

    # criar pasta modelos se não existir
    os.makedirs("modelos", exist_ok=True)


    # ===========================
    # CONECTAR AO BANCO
    # ===========================

    banco = sqlite3.connect("instance/banco.db")

    cursor = banco.cursor()


    # Buscar alunos cadastrados

    cursor.execute("""
    SELECT
        id,
        nome,
        foto

    FROM alunos
    """)


    alunos = cursor.fetchall()


    rostos = []


    # ===========================
    # LER CADA FOTO
    # ===========================

    for aluno in alunos:

        aluno_id = aluno[0]
        nome = aluno[1]
        foto = aluno[2]


        caminho = os.path.join(
            PASTA_FOTOS,
            foto
        )


        print("Processando:", nome)


        if os.path.exists(caminho):


            imagem = face_recognition.load_image_file(caminho)


            codificacoes = face_recognition.face_encodings(imagem)


            if len(codificacoes) > 0:


                rosto = {

                    "id": aluno_id,

                    "nome": nome,

                    "encoding": codificacoes[0]

                }


                rostos.append(rosto)


                print("Rosto encontrado:", nome)


            else:

                print("Nenhum rosto encontrado:", nome)


        else:

            print("Foto não encontrada:", caminho)



    # ===========================
    # SALVAR ARQUIVO
    # ===========================


    with open(ARQUIVO_ROSTOS, "wb") as arquivo:

        pickle.dump(
            rostos,
            arquivo
        )


    banco.close()


    print("==============================")
    print("Assinaturas faciais criadas!")
    print("Arquivo salvo em:")
    print(ARQUIVO_ROSTOS)
    print("==============================")



# Executa quando abrir pelo terminal
if __name__ == "__main__":

    gerar_rostos()