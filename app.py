from flask import Flask, render_template, request, jsonify
from sistema_experto import SistemaExpertoFutbol

app = Flask(__name__)
sistema = SistemaExpertoFutbol()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analizar", methods=["POST"])
def analizar():
    datos = request.get_json(force=True)

    if not datos:
        return jsonify({"error": "No se recibieron datos"}), 400

    try:
        resultado = sistema.analizar_jugador(
            altura_cm = int(datos.get("altura_cm", 178)),
            peso_kg = int(datos.get("peso_kg", 72)),
            velocidad_ms = float(datos.get("velocidad_ms", 8.0)),
            salto_long_cm = int(datos.get("salto_long_cm", 210)),
            salto_alt_cm = int(datos.get("salto_alt_cm", 48)),
            reaccion_ms = int(datos.get("reaccion_ms",185)),
            potencia_tiro = int(datos.get("potencia_tiro", 70)),
        )

        if resultado is None:
            return jsonify({"error": "El motor no produjo resultado"}), 500

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("=" * 55)
    print("  Sistema Experto · Cantera · Servidor Flask")
    print("  Abre tu navegador en: http://127.0.0.1:5000")
    print("=" * 55)
    app.run(debug=True)