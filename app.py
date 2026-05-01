from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Unsere "Datenbank" – eine einfache Liste im Arbeitsspeicher
aufgaben = [
    {"id": 1, "titel": "Mathe Hausaufgaben", "erledigt": False},
    {"id": 2, "titel": "Physik lernen", "erledigt": True},
]

def naechste_id():
    if len(aufgaben) == 0:
        return 1
    return max(a["id"] for a in aufgaben) + 1


@app.route("/aufgaben", methods=["GET"])
def get_aufgaben():
    return jsonify(aufgaben)


@app.route("/aufgaben", methods=["POST"])
def create_aufgabe():
    daten = request.get_json()
    if not daten or "titel" not in daten:
        return jsonify({"fehler": "Feld 'titel' fehlt"}), 400
    neue_aufgabe = {
        "id": naechste_id(),
        "titel": daten["titel"],
        "erledigt": False
    }
    aufgaben.append(neue_aufgabe)
    return jsonify(neue_aufgabe), 201


@app.route("/aufgaben/<int:aufgabe_id>", methods=["PUT"])
def update_aufgabe(aufgabe_id):
    daten = request.get_json()
    for aufgabe in aufgaben:
        if aufgabe["id"] == aufgabe_id:
            if "titel" in daten:
                aufgabe["titel"] = daten["titel"]
            if "erledigt" in daten:
                aufgabe["erledigt"] = daten["erledigt"]
            return jsonify(aufgabe)
    return jsonify({"fehler": "Aufgabe nicht gefunden"}), 404


@app.route("/aufgaben/<int:aufgabe_id>", methods=["DELETE"])
def delete_aufgabe(aufgabe_id):
    for i, aufgabe in enumerate(aufgaben):
        if aufgabe["id"] == aufgabe_id:
            aufgaben.pop(i)
            return jsonify({"nachricht": "Aufgabe gelöscht"})
    return jsonify({"fehler": "Aufgabe nicht gefunden"}), 404


if __name__ == "__main__":
    app.run(debug=True)