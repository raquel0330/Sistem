import cv2
import face_recognition
import pickle
import sqlite3
from datetime import datetime


def iniciar_camera(aula, turma):
    print("Turma:", turma)
    print("Aula:", aula)

    banco = sqlite3.connect("instance/banco.db")
    cursor = banco.cursor()

    mensagem = ""


    # ===========================
    # CARREGAR ROSTOS
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



    print("Reconhecimento iniciado")
    print("Aula:", aula)



    # ===========================
    # CÂMERA
    # ===========================

    nome_janela = "Sistema de Presenca Escolar - Reconhecimento Facial"

    camera = cv2.VideoCapture(0)

    cv2.namedWindow(nome_janela, cv2.WINDOW_NORMAL)

    cv2.resizeWindow(nome_janela, 1000, 700)


    if not camera.isOpened():

        print("Erro ao abrir câmera")
        return



    while True:


        sucesso, frame = camera.read()


        if not sucesso:
            break



        frame_pequeno = cv2.resize(
            frame,
            (0,0),
            fx=0.25,
            fy=0.25
        )


        rgb = cv2.cvtColor(
            frame_pequeno,
            cv2.COLOR_BGR2RGB
        )


        localizacoes = face_recognition.face_locations(rgb)


        encodings_camera = face_recognition.face_encodings(
            rgb,
            localizacoes
        )



        for encoding, (top, right, bottom, left) in zip(
            encodings_camera,
            localizacoes
        ):


            resultados = face_recognition.compare_faces(
                encodings,
                encoding,
                tolerance=0.50
            )


            nome = "Desconhecido"



            if True in resultados:


                indice = resultados.index(True)


                nome = nomes[indice]


                aluno_id = ids[indice]


                data = datetime.now().strftime("%d/%m/%Y")

                hora = datetime.now().strftime("%H:%M")



                cursor.execute("""
                SELECT id
                FROM presencas
                WHERE aluno_id = ?
                AND data = ?
                AND aula = ?

                """,
                (
                    aluno_id,
                    data,
                    aula
                ))



                existe = cursor.fetchone()



                if existe is None:


                    cursor.execute("""
                    INSERT INTO presencas
                    (
                        aluno_id,
                        data,
                        hora,
                        aula,
                        status
                    )

                    VALUES (?, ?, ?, ?, ?)

                    """,
                    (
                        aluno_id,
                        data,
                        hora,
                        aula,
                        "Presente"
                    ))


                    banco.commit()


                    mensagem = "Presenca registrada!"


                else:

                    mensagem = "Presenca ja registrada!"



            top *= 4
            right *= 4
            bottom *= 4
            left *= 4



            cv2.rectangle(
                frame,
                (left, top),
                (right, bottom),
                (0,255,0),
                2
            )



            cv2.putText(
                frame,
                nome,
                (left, top-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0,255,0),
                2
            )

            cv2.putText(
    frame,
    mensagem,
    (left, bottom + 30),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.7,
    (0,255,0),
    2
)



        cv2.imshow(
            nome_janela,
            frame
)



        tecla = cv2.waitKey(1)



        if tecla == 27:
            break



    camera.release()

    cv2.destroyAllWindows()



if __name__ == "__main__":

    iniciar_camera("1ª Aula")