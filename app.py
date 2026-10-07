"""MVP local para criação de templates de bicicleta.

Execute com: python app.py
"""

from __future__ import annotations

import json
import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LAYOUTS_FILE = DATA_DIR / "layouts.json"
PROJECTS_FILE = DATA_DIR / "projects.json"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "troque-esta-chave-em-producao")
# Apenas para este MVP local. Em produção, use usuários/senhas seguros.
DEV_PASSWORD = os.environ.get("DEV_PASSWORD", "admin123")


# Pontos no canvas de 760 × 500 px, as dimensões finais devem ser conferidas no quadro físico.
BASE_LAYOUTS = [
    {"id": "top-tube", "name": "Top Tube", "description": "Retângulo central 2 × 20 cm com pontas triangulares de 2 cm", "widthCm": 2, "heightCm": 24, "defaultQuantity": 2, "polygon": [[304, 178], [318, 173], [493, 102], [507, 106], [497, 111], [321, 177]]},
    {"id": "protector-conduit", "name": "High-rise Tube, Top View", "description": "Parte superior do cano", "widthCm": 3, "heightCm": 40, "defaultQuantity": 2, "previewAngle": "top", "anglePolygons": {"top": [[311, 213], [301, 218], [311, 222], [500, 196], [512, 187], [499, 184]]}, "polygon": [[301, 164], [306, 173], [419, 141], [415, 133]]},
    {"id": "front-tube", "name": "Front tube", "description": "Tubo frontal", "widthCm": 6, "heightCm": 9, "defaultQuantity": 2, "previewAngle": "front", "anglePolygons": {"front": [[378, 103], [399, 103], [401, 154], [375, 155]]}, "polygon": [[378, 103], [399, 103], [401, 154], [375, 155]]},
    {"id": "front-fork", "name": "Front fork", "description": "Garfo - vista frontal", "widthCm": 2, "heightCm": 15, "defaultQuantity": 1, "previewAngle": "front", "anglePolygons": {"front": [[348, 267], [341, 276], [340, 395], [349, 405], [356, 396], [357, 276]]}, "polygon": [[348, 267], [341, 276], [340, 395], [349, 405], [356, 396], [357, 276]]},
    {"id": "rear-tube", "name": "Rear tube", "description": "Tubo traseiro", "widthCm": 6, "heightCm": 9, "defaultQuantity": 1, "previewAngle": "rear", "anglePolygons": {"rear": [[388, 81], [383, 86], [383, 177], [388, 181], [393, 176], [393, 85]]}, "polygon": [[388, 81], [383, 86], [383, 177], [388, 181], [393, 176], [393, 85]]},
    {"id": "roda", "name": "Roda", "description": "Faixa lateral do aro", "widthCm": 2, "heightCm": 25, "defaultQuantity": 8, "polygon": [[112, 206], [100, 218], [89, 228], [78, 239], [69, 252], [60, 266], [55, 280], [52, 292], [49, 307], [49, 328], [53, 349], [55, 373], [51, 362], [48, 356], [46, 348], [44, 341], [43, 336], [42, 328], [42, 319], [42, 307], [44, 301], [46, 286], [52, 271], [57, 259], [66, 246], [74, 235], [83, 225], [91, 218]]},
    {"id": "headset", "name": "Headset", "description": "Caixa de direção", "widthCm": 6, "heightCm": 9, "defaultQuantity": 2, "polygon": [[526, 131], [509, 90], [501, 94], [513, 137]]},
    {"id": "fork", "name": "Fork", "description": "Garfo dianteiro", "widthCm": 3, "heightCm": 18, "defaultQuantity": 2, "polygon": [[545, 209], [556, 203], [593, 317], [586, 321]]},
    {"id": "fork-menor", "name": "Fork menor", "description": "Parte superior do garfo", "widthCm": 4, "heightCm": 9, "defaultQuantity": 2, "polygon": [[532, 164], [540, 162], [551, 196], [542, 199]]},
    {"id": "down-tube", "name": "Down Tube", "description": "Tubo inferior", "widthCm": 6, "heightCm": 55, "defaultQuantity": 2, "polygon": [[500, 118], [487, 125], [470, 137], [459, 153], [357, 310], [364, 318], [477, 152], [490, 140], [501, 133]]},
    {"id": "pedivela", "name": "Pedivela", "description": "Região do pedivela", "widthCm": 2, "heightCm": 8, "defaultQuantity": 2, "polygon": [[352, 345], [390, 345], [386, 349], [347, 349]]},
    {"id": "chain-stay", "name": "Chain Stay", "description": "Escora inferior traseira", "widthCm": 2, "heightCm": 25, "defaultQuantity": 2, "polygon": [[197, 329], [201, 333], [304, 346], [305, 337]]},
    {"id": "seatstay", "name": "Seatstay", "description": "Escora superior traseira", "widthCm": 2, "heightCm": 35, "defaultQuantity": 2, "polygon": [[172, 294], [180, 290], [309, 185], [312, 180], [306, 182], [177, 287]]},
]

DEFAULT_LAYOUTS = {
    "mountain": {"name": "Bicicleta aro 26–29", "layouts": deepcopy(BASE_LAYOUTS)},
}


def ensure_data_files() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if not LAYOUTS_FILE.exists():
        write_json(LAYOUTS_FILE, DEFAULT_LAYOUTS)
    if not PROJECTS_FILE.exists():
        write_json(PROJECTS_FILE, [])


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data) -> None:
    """Escreve primeiro em arquivo temporário para reduzir risco de corrupção."""
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    temporary.replace(path)


@app.before_request
def initialise_storage():
    ensure_data_files()


@app.get("/")
def index():
    return render_template("index.html")


@app.route("/dev", methods=["GET", "POST"])
def developer_corner():
    if request.method == "POST" and request.form.get("action") == "login":
        if request.form.get("password") == DEV_PASSWORD:
            session["developer_authenticated"] = True
            return redirect(url_for("developer_corner"))
        return render_template("dev_login.html", error="Senha inválida."), 401

    if not session.get("developer_authenticated"):
        return render_template("dev_login.html")
    return render_template("dev.html")


@app.post("/dev/logout")
def developer_logout():
    session.pop("developer_authenticated", None)
    return redirect(url_for("developer_corner"))


@app.get("/api/layouts")
def get_layouts():
    return jsonify(read_json(LAYOUTS_FILE))


@app.put("/api/layouts")
def save_layouts():
    if not session.get("developer_authenticated"):
        return jsonify({"error": "Autenticação necessária."}), 401

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Dados inválidos."}), 400

    try:
        validate_layouts(payload)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    write_json(LAYOUTS_FILE, payload)
    return jsonify({"ok": True, "message": "Layouts salvos com sucesso."})


@app.post("/api/projects")
def save_project():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not payload.get("model") or not payload.get("layout"):
        return jsonify({"error": "Projeto incompleto."}), 400

    projects = read_json(PROJECTS_FILE)
    project = {
        "id": str(uuid4()),
        "createdAt": datetime.now(timezone.utc).isoformat(),
        # Salva somente as transformações e metadados; a imagem continua no navegador.
        "model": payload["model"],
        "layout": payload["layout"],
        "imageName": payload.get("imageName", ""),
        "transform": payload.get("transform", {}),
        "assets": payload.get("assets", []),
        "assignments": payload.get("assignments", {}),
    }
    projects.append(project)
    write_json(PROJECTS_FILE, projects)
    return jsonify({"ok": True, "project": project})


def validate_layouts(layouts: dict) -> None:
    for model_key, model in layouts.items():
        if not isinstance(model_key, str) or not isinstance(model, dict):
            raise ValueError("Estrutura de modelo inválida.")
        if not isinstance(model.get("name"), str) or not isinstance(model.get("layouts"), list):
            raise ValueError(f"O modelo '{model_key}' precisa de nome e layouts.")
        if not model["name"].strip():
            raise ValueError("O nome do modelo não pode ficar vazio.")
        for layout in model["layouts"]:
            if not isinstance(layout, dict) or not isinstance(layout.get("id"), str):
                raise ValueError("Cada layout precisa ter um identificador.")
            if not isinstance(layout.get("name"), str) or not layout["name"].strip():
                raise ValueError("O nome do layout não pode ficar vazio.")
            if float(layout.get("widthCm", 0)) <= 0 or float(layout.get("heightCm", 0)) <= 0:
                raise ValueError("As medidas em centímetros devem ser maiores que zero.")
            if int(layout.get("defaultQuantity", 1)) < 0:
                raise ValueError("A quantidade padrão não pode ser negativa.")
            polygon = layout.get("polygon")
            if not isinstance(polygon, list) or len(polygon) < 3:
                raise ValueError("Todo layout deve conter ao menos três pontos no polígono.")
            for point in polygon:
                if not isinstance(point, list) or len(point) != 2:
                    raise ValueError("Cada ponto do polígono deve ser [X, Y].")
                float(point[0])
                float(point[1])


if __name__ == "__main__":
    ensure_data_files()
    app.run(debug=True, host="127.0.0.1", port=5000)
