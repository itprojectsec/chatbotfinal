from flask import Flask, request, jsonify
import json
import os
from chat import request_user_data, check_requirements, save_user_data, chatbot_interaction
# Importa las funciones adicionales si es necesario

app = Flask(__name__)

@app.route("/process_data", methods=["POST"])
def process_data():
    data = request.get_json()

    # Llama a la función request_user_data y pasa los datos recibidos
    user_data = request_user_data(data)

    # Llama a la función check_requirements y pasa los valores de edad e ingresos totales
    requirements_met = check_requirements(user_data[2], user_data[3])

    if requirements_met:
        message = "Cumples con los requisitos."

        # Guardar los datos del usuario
        save_user_data(user_data)

        # Llamar a la función chatbot_interaction para interactuar con el chatbot
        # Tendrás que ajustar la función chatbot_interaction en tu archivo Python
        # para aceptar un diccionario de datos en lugar de solicitar la entrada del usuario
        chatbot_response = chatbot_interaction(user_data)
        message += f" Chatbot dice: {chatbot_response}"
    else:
        message = "Lo siento, no cumples con los requisitos para acceder a esta información."

    # Retorna los resultados o mensajes necesarios en formato JSON
    return jsonify({"message": message})

if __name__ == "__main__":
    app.run(debug=True)