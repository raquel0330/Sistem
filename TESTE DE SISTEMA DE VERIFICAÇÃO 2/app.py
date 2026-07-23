from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import camera
from werkzeug.utils import secure_filename
import gerar_rostos
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from flask import send_file
import io

app = Flask(__name__)

# ===========================
# CONFIGURAÇÕES
# ===========================

app.secret_key = "sistema_presenca_escolar"

app.config["UPLOAD_FOLDER"] = "static/fotos"


# ===========================
# BANCO DE DADOS
# ===========================

def conectar():
    return sqlite3.connect("instance/banco.db")


# ===========================
# LOGIN
# ===========================

@app.route("/")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def entrar():

    usuario = request.form["usuario"]
    senha = request.form["senha"]
    turma = request.form["turma"]

    if usuario == "admin" and senha == "123456":

        session["professor"] = usuario
        session["turma"] = turma

        return redirect(url_for("inicio"))

    return "Usuário ou senha incorretos"


# ===========================
# PAINEL
# ===========================

@app.route("/inicio")
def inicio():

    professor = session.get("professor")
    turma = session.get("turma")

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("SELECT COUNT(*) FROM alunos")

    total_alunos = cursor.fetchone()[0]

    banco.close()

    return render_template(
        "painel.html",
        professor=professor,
        turma=turma,
        total_alunos=total_alunos
    )


# ===========================
# CADASTRAR ALUNO
# ===========================

@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():

    if request.method == "POST":

        nome = request.form["nome"]
        turma_id = request.form["turma_id"]
        responsavel = request.form["responsavel"]
        telefone = request.form["telefone"]
        email = request.form["email"]

        foto = request.files["foto"]

        nome_foto = secure_filename(foto.filename)

        os.makedirs(
            app.config["UPLOAD_FOLDER"],
            exist_ok=True
        )

        caminho = os.path.join(
            app.config["UPLOAD_FOLDER"],
            nome_foto
        )

        foto.save(caminho)

        banco = conectar()
        cursor = banco.cursor()

        cursor.execute("""
        INSERT INTO alunos
        (
            nome,
            turma_id,
            foto,
            responsavel,
            telefone,
            email
        )

        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            nome,
            turma_id,
            nome_foto,
            responsavel,
            telefone,
            email
        ))

        banco.commit()
        banco.close()

        gerar_rostos.gerar_rostos()

        return redirect(url_for("listar_alunos"))

    return render_template("cadastrar.html")


# ===========================
# LISTAR ALUNOS
# ===========================

@app.route("/alunos")
def listar_alunos():

    banco = conectar()
    cursor = banco.cursor()

    cursor.execute("""

    SELECT
        id,
        nome,
        turma_id,
        foto,
        responsavel,
        telefone,
        email

    FROM alunos

    ORDER BY nome

    """)

    alunos = cursor.fetchall()

    banco.close()

    turma = session.get("turma")

    return render_template(
        "alunos.html",
        alunos=alunos,
        turma=turma
    )

# ===========================
# EDITAR ALUNO
# ===========================

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    banco = conectar()
    cursor = banco.cursor()

    if request.method == "POST":

        nome = request.form["nome"]
        turma_id = request.form["turma_id"]
        responsavel = request.form["responsavel"]
        telefone = request.form["telefone"]
        email = request.form["email"]

        # Busca a foto atual
        cursor.execute(
            "SELECT foto FROM alunos WHERE id = ?",
            (id,)
        )

        foto_atual = cursor.fetchone()[0]

        foto = request.files["foto"]

        # Se o usuário escolheu uma nova foto
        if foto and foto.filename != "":

            nome_foto = secure_filename(foto.filename)

            caminho = os.path.join(
                app.config["UPLOAD_FOLDER"],
                nome_foto
            )

            foto.save(caminho)

        else:

            # Mantém a foto antiga
            nome_foto = foto_atual

        cursor.execute("""

        UPDATE alunos

        SET

            nome = ?,
            turma_id = ?,
            foto = ?,
            responsavel = ?,
            telefone = ?,
            email = ?

        WHERE id = ?

        """,
        (
            nome,
            turma_id,
            nome_foto,
            responsavel,
            telefone,
            email,
            id
        ))

        banco.commit()
        banco.close()

        gerar_rostos.gerar_rostos()

        return redirect(url_for("listar_alunos"))

    cursor.execute("""

    SELECT
        id,
        nome,
        turma_id,
        foto,
        responsavel,
        telefone,
        email

    FROM alunos

    WHERE id = ?

    """, (id,))

    aluno = cursor.fetchone()

    banco.close()

    return render_template(
        "editar.html",
        aluno=aluno
    )


# ===========================
# INICIAR O FLASK
# ===========================

# ===========================
# EXCLUIR ALUNO
# ===========================

@app.route("/excluir/<int:id>")
def excluir(id):

    banco = conectar()
    cursor = banco.cursor()


    # pega o nome da foto antes de excluir
    cursor.execute(
        "SELECT foto FROM alunos WHERE id = ?",
        (id,)
    )

    resultado = cursor.fetchone()


    if resultado:

        foto = resultado[0]


        # remove a foto da pasta
        caminho_foto = os.path.join(
            app.config["UPLOAD_FOLDER"],
            foto
        )


        if os.path.exists(caminho_foto):

            os.remove(caminho_foto)



        # remove aluno do banco
        cursor.execute(
            "DELETE FROM alunos WHERE id = ?",
            (id,)
        )


        banco.commit()


    banco.close()

    gerar_rostos.gerar_rostos()


    return redirect(url_for("listar_alunos"))

# ===========================
# CHAMADA
# ===========================

# ===========================
# CHAMADA
# ===========================

@app.route("/chamada")
def chamada():

    turma = session.get("turma")

    banco = conectar()
    cursor = banco.cursor()


    cursor.execute("""
    
    SELECT
        alunos.id,
        alunos.nome,
        alunos.foto

    FROM alunos

    INNER JOIN turmas

    ON alunos.turma_id = turmas.id

    WHERE turmas.nome = ?

    ORDER BY alunos.nome

    """,
    (turma,))


    alunos = cursor.fetchall()


    banco.close()


    return render_template(
        "chamada.html",
        alunos=alunos,
        turma=turma
    )

# ===========================
# SALVAR CHAMADA
# ===========================

@app.route("/salvar_chamada", methods=["POST"])
def salvar_chamada():

    from datetime import datetime


    alunos_presentes = request.form.getlist("alunos")

    aula = request.form.get("aula")


    data_atual = datetime.now().strftime("%d/%m/%Y")

    hora_atual = datetime.now().strftime("%H:%M")


    banco = conectar()

    cursor = banco.cursor()


    # Buscar todos os alunos da turma atual

    turma = session.get("turma")


    cursor.execute("""

    SELECT 
        alunos.id

    FROM alunos

    INNER JOIN turmas

    ON alunos.turma_id = turmas.id

    WHERE turmas.nome = ?

    """,
    (turma,))


    alunos_turma = cursor.fetchall()



    for aluno in alunos_turma:


        aluno_id = aluno[0]


        if str(aluno_id) in alunos_presentes:

            status = "Presente"

        else:

            status = "Falta"


    # Buscar todos os alunos da turma atual

    turma = session.get("turma")


    cursor.execute("""

    SELECT 
        alunos.id

    FROM alunos

    INNER JOIN turmas

    ON alunos.turma_id = turmas.id

    WHERE turmas.nome = ?

    """,
    (turma,))


    alunos_turma = cursor.fetchall()



    for aluno in alunos_turma:


        aluno_id = aluno[0]


        if str(aluno_id) in alunos_presentes:

            status = "Presente"

        else:

            status = "Falta"



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
            data_atual,
            hora_atual,
            aula,
            status
        ))



    banco.commit()

    banco.close()


    return redirect(url_for("inicio"))

# ===========================
# RELATÓRIO DE PRESENÇA
# ===========================

@app.route("/relatorio")
def relatorio():

    turma = session.get("turma")


    banco = conectar()
    cursor = banco.cursor()


    cursor.execute("""
    
    SELECT

        alunos.nome,

        SUM(
            CASE 
                WHEN presencas.status = 'Presente'
                THEN 1
                ELSE 0
            END
        ) AS presentes,


        SUM(
            CASE 
                WHEN presencas.status = 'Falta'
                THEN 1
                ELSE 0
            END
        ) AS faltas


    FROM alunos


    LEFT JOIN presencas

    ON alunos.id = presencas.aluno_id


    INNER JOIN turmas

    ON alunos.turma_id = turmas.id


    WHERE turmas.nome = ?


    GROUP BY alunos.id


    ORDER BY alunos.nome


    """,
    (turma,))


    alunos = cursor.fetchall()


    banco.close()


    return render_template(
        "relatorio.html",
        alunos=alunos,
        turma=turma
    )

@app.route("/exportar_frequencia_pdf")
def exportar_frequencia_pdf():

    turma = session.get("turma")

    banco = conectar()
    cursor = banco.cursor()


    cursor.execute("""
    
    SELECT

        alunos.nome,

        SUM(
            CASE 
                WHEN presencas.status = 'Presente'
                THEN 1
                ELSE 0
            END
        ) AS presentes,


        SUM(
            CASE 
                WHEN presencas.status = 'Falta'
                THEN 1
                ELSE 0
            END
        ) AS faltas


    FROM alunos


    LEFT JOIN presencas

    ON alunos.id = presencas.aluno_id


    INNER JOIN turmas

    ON alunos.turma_id = turmas.id


    WHERE turmas.nome = ?


    GROUP BY alunos.id


    ORDER BY alunos.nome


    """,
    (turma,))


    alunos = cursor.fetchall()


    banco.close()



    arquivo = io.BytesIO()


    pdf = canvas.Canvas(
        arquivo,
        pagesize=A4
    )


    pdf.setTitle(
        "Relatório de Frequência"
    )


    pdf.drawString(
        50,
        800,
        "Relatório de Frequência Escolar"
    )


    pdf.drawString(
        50,
        780,
        f"Turma: {turma}"
    )



    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors



    dados = [

        [
            "Aluno",
            "Presenças",
            "Faltas",
            "Frequência"
        ]

    ]



    for aluno in alunos:


        presentes = aluno[1] or 0

        faltas = aluno[2] or 0


        total = presentes + faltas


        if total > 0:

            frequencia = round(
                (presentes / total) * 100,
                1
            )

        else:

            frequencia = 0



        dados.append(

            [

                aluno[0],

                presentes,

                faltas,

                f"{frequencia}%"

            ]

        )



    tabela = Table(

        dados,

        colWidths=[250,80,80,80]

    )



    tabela.setStyle(

        TableStyle(

            [

                (
                    'BACKGROUND',
                    (0,0),
                    (-1,0),
                    colors.green
                ),


                (
                    'TEXTCOLOR',
                    (0,0),
                    (-1,0),
                    colors.white
                ),


                (
                    'GRID',
                    (0,0),
                    (-1,-1),
                    0.5,
                    colors.black
                ),


                (
                    'ALIGN',
                    (1,1),
                    (-1,-1),
                    'CENTER'
                )

            ]

        )

    )



    tabela.wrapOn(
        pdf,
        50,
        700
    )


    tabela.drawOn(
        pdf,
        50,
        600
    )



    pdf.save()



    arquivo.seek(0)



    return send_file(

        arquivo,

        as_attachment=True,

        download_name="relatorio_frequencia.pdf",

        mimetype="application/pdf"

    )
# ===========================
# HISTÓRICO DE CHAMADAS
# ===========================

@app.route("/historico")
def historico():

    turma = session.get("turma")


    banco = conectar()

    cursor = banco.cursor()


    cursor.execute("""
    
    SELECT

        alunos.nome,
        presencas.data,
        presencas.hora,
        presencas.aula,
        presencas.status


    FROM presencas


    INNER JOIN alunos

    ON presencas.aluno_id = alunos.id


    INNER JOIN turmas

    ON alunos.turma_id = turmas.id


    WHERE turmas.nome = ?


    ORDER BY presencas.id DESC


    """,
    (turma,))


    chamadas = cursor.fetchall()


    banco.close()


    return render_template(
        "historico.html",
        chamadas=chamadas,
        turma=turma
    )

@app.route("/exportar_pdf")
def exportar_pdf():

    turma = session.get("turma")

    banco = conectar()
    cursor = banco.cursor()


    cursor.execute("""
    
    SELECT

        alunos.nome,
        presencas.data,
        presencas.hora,
        presencas.aula,
        presencas.status


    FROM presencas


    INNER JOIN alunos

    ON presencas.aluno_id = alunos.id


    INNER JOIN turmas

    ON alunos.turma_id = turmas.id


    WHERE turmas.nome = ?


    ORDER BY presencas.id DESC


    """,
    (turma,))


    chamadas = cursor.fetchall()


    banco.close()



    arquivo = io.BytesIO()



    pdf = canvas.Canvas(
        arquivo,
        pagesize=A4
    )



    pdf.setTitle(
        "Histórico de Chamadas"
    )


    pdf.drawString(
    50,
    820,
    "Histórico de Chamadas Escolar"
)


    pdf.drawString(
    50,
    790,
    f"Turma: {turma}"
)


    y = 730



    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors



    dados = [

        [
            "Aluno",
            "Data",
            "Hora",
            "Aula",
            "Status"
        ]

    ]



    for chamada in chamadas:


        dados.append(

            [

                chamada[0],
                chamada[1],
                chamada[2],
                chamada[3],
                chamada[4]

            ]

        )



    tabela = Table(

        dados,

        colWidths=[
            180,
            80,
            60,
            50,
            80
        ]

    )



    tabela.setStyle(

        TableStyle(

            [

                (
                    'BACKGROUND',
                    (0,0),
                    (-1,0),
                    colors.green
                ),


                (
                    'TEXTCOLOR',
                    (0,0),
                    (-1,0),
                    colors.white
                ),


                (
                    'GRID',
                    (0,0),
                    (-1,-1),
                    0.5,
                    colors.black
                ),


                (
                    'ALIGN',
                    (1,1),
                    (-1,-1),
                    'CENTER'
                )

            ]

        )

    )



    tabela.wrapOn(
        pdf,
        50,
        700
    )


    tabela.drawOn(
    pdf,
    50,
    560
)



    pdf.save()



    arquivo.seek(0)



    return send_file(

        arquivo,

        as_attachment=True,

        download_name="historico_chamadas.pdf",

        mimetype="application/pdf"

    )
# ===========================
# ESCOLHER AULA - RECONHECIMENTO FACIAL
# ===========================

@app.route("/reconhecimento")
def reconhecimento():

    turma = session.get("turma")

    return render_template(
        "reconhecimento.html",
        turma=turma
    )

# ===========================
# INICIAR RECONHECIMENTO
# ===========================

from datetime import datetime


@app.route("/iniciar_reconhecimento", methods=["POST"])
def iniciar_reconhecimento():

    aula = request.form["aula"]

    turma = session.get("turma")

    data = datetime.now().strftime("%d/%m/%Y")


    session["aula"] = aula
    session["data"] = data


    camera.iniciar_camera(aula, turma)


    return redirect(url_for("inicio"))
# ===========================
# ABRIR CÂMERA
# ===========================

@app.route("/camera")
def abrir_camera():

    aula = session.get("aula")

    return render_template(
        "camera.html",
        aula=aula
    )

if __name__ == "__main__":

    app.run(debug=True)