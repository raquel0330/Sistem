import pickle

with open("modelos/rostos.pkl", "rb") as arquivo:
    rostos = pickle.load(arquivo)

print("Quantidade de rostos:", len(rostos))

for rosto in rostos:
    print("------------------------")
    print("ID:", rosto["id"])
    print("Nome:", rosto["nome"])