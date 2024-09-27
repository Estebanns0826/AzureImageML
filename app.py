from flask import Flask, jsonify, render_template, request
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')  # Archivo HTML para el frontend

@app.route('/enviar_imagen', methods=['POST'])
def recibir_clasificacion():
    file = request.files.get('image')
    azure_endpoint = request.form.get('endpoint')
    subscription_key = request.form.get('key')
    
    if not file or not azure_endpoint or not subscription_key:
        return jsonify({'error': 'Faltan datos necesarios'}), 400
    
    try:
        response = classify_image_with_azure(file.read(), azure_endpoint, subscription_key)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def classify_image_with_azure(image_file, azure_endpoint, subscription_key):
    headers = {
        'Content-Type': 'application/octet-stream',
        'Prediction-Key': subscription_key
    }

    response = requests.post(azure_endpoint, headers=headers, data=image_file)

    if response.status_code == 200:
        # Filtrar predicciones con probabilidad mayor al 50%
        data = response.json()
        filtered_predictions = [
            pred for pred in data.get('predictions', [])
            if pred['probability'] >= 0.5
        ]
        # Devolver solo las predicciones filtradas
        return {'predictions': filtered_predictions}
    else:
        return {'error': 'Error al clasificar la imagen'}, response.status_code

if __name__ == '__main__':
    app.run(debug=True)
