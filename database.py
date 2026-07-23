import sqlite3


conexao = sqlite3.connect("instance/banco.db")

cursor = conexao.cursor()


# ===========================
# Tabela de professores
# ===========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS professores(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    usuario TEXT UNIQUE,
    senha TEXT
)
""")


# ===========================
# Tabela de turmas
# ===========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS turmas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    professor_id INTEGER,
    FOREIGN KEY(professor_id) REFERENCES professores(id)
)
""")


# Criar turmas padrão

cursor.execute("""
INSERT OR IGNORE INTO turmas
(id, nome, professor_id)

VALUES
(1, '3º Ano B', 1)
""")


cursor.execute("""
INSERT OR IGNORE INTO turmas
(id, nome, professor_id)

VALUES
(2, '2º Ano A', 1)
""")


# ===========================
# Tabela de alunos
# ===========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS alunos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    turma_id INTEGER,
    foto TEXT,
    responsavel TEXT,
    telefone TEXT,
    email TEXT,
    FOREIGN KEY(turma_id) REFERENCES turmas(id)
)
""")


# ===========================
# Tabela de presenças
# ===========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS presencas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER,
    data TEXT,
    hora TEXT,
    aula TEXT,
    status TEXT,
    FOREIGN KEY(aluno_id) REFERENCES alunos(id)
)
""")


# ===========================
# Corrigir banco antigo
# adicionando aula se já existir
# ===========================

try:

    cursor.execute("""
    ALTER TABLE presencas
    ADD COLUMN aula TEXT
    """)

except:

    pass



# ===========================
# Criar professor administrador
# ===========================

cursor.execute("""

INSERT OR IGNORE INTO professores
(nome, usuario, senha)

VALUES

('Administrador',
 'admin',
 '123456')

""")


conexao.commit()

conexao.close()


print("Banco criado com sucesso!")