import os
import random
import numpy as np
import json
import pickle
import nltk
import spacy
import openai
#nltk.download('punkt')
#nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer 
from keras.models import load_model
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email import encoders
from docxtpl import DocxTemplate
from docx import Document
lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbot_model.h5')



def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]

    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)

    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1

    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []

    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})

    return return_list

def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']

    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break

    return result

def request_user_data():
    full_name = input("Por favor, ingresa tu nombre completo: ")
    while True:
        id_number = input("Por favor, ingresa tu número de cédula: ")
        if len(id_number) == 10:
            break
        print("El número de cédula es invalido.")
    while True:
        age = int(input("Por favor, ingresa tu edad: "))
        if 18 <= age <= 130:
            break
        print("La edad debe estar entre 18 y 130 años.")
    total_income = float(input("Por favor, ingresa tu total de ingresos: "))
    address = input("Por favor, ingresa tu dirección: ")
    nationality = input("Por favor, ingresa tu nacionalidad: ")
    cadastral_code = input("Por favor, ingresa el código catastral: ")
    birthdate = input("Por favor, ingresa tu fecha de nacimiento (DD/MM/AAAA): ")
    phone_number = input("Por favor, ingresa tu número de teléfono: ")
    email = input("Por favor, ingresa tu dirección de correo electrónico: ")


    while True:
        marital_status = input("Por favor, ingresa tu estado civil (casado, soltero, viudo, divorciado): ").lower()
        if marital_status in ['casado', 'soltero', 'viudo', 'divorciado']:
            break
        print("Por favor, ingresa una opción válida.")

    spouse_data = {}
    if marital_status == 'casado':
        spouse_full_name = input("Por favor, ingresa el nombre completo de tu cónyuge: ")
        spouse_id_number = input("Por favor, ingresa el número de cédula de tu cónyuge: ")
        spouse_birthdate = input("Por favor, ingresa la fecha de nacimiento de tu cónyuge (DD/MM/AAAA): ")
        spouse_nationality = input("Por favor, ingresa la nacionalidad de tu cónyuge: ")
        spouse_data = {
            'spouse_full_name': spouse_full_name,
            'spouse_id_number': spouse_id_number,
            'spouse_birthdate': spouse_birthdate,
            'spouse_nationality': spouse_nationality
        }

    while True:
        property_acquisition = input("Por favor, indica cómo adquiriste el bien (compraventa, donación, herencia): ").lower()
        if property_acquisition in ['compraventa', 'donación', 'herencia']:
            break
        print("Por favor, ingresa una opción válida.")

    return full_name, id_number, age, total_income, address, nationality, cadastral_code, birthdate, phone_number, marital_status, spouse_data, property_acquisition, email

def check_requirements(age, total_income):
    return age >= 65 and total_income < 450 * 3

def save_user_data(data, filename='user_data.json'):
    existing_data = []

    if os.path.exists(filename):
        try:
            with open(filename, 'r') as file:
                existing_data = json.load(file)
        except json.JSONDecodeError:
            print(f"Advertencia: El archivo {filename} contiene datos no válidos y se sobrescribirá.")

    existing_data.append(data)

    with open(filename, 'w') as file:
        json.dump(existing_data, file, indent=4)
        
def fill_form(user_data, template_path='formato.docx', output_path='peticion.docx'):
    doc = Document(template_path)

    for paragraph in doc.paragraphs:
        for key, value in user_data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    paragraph.text = paragraph.text.replace(f'{{{{{sub_key}}}}}', str(sub_value))
            else:
                paragraph.text = paragraph.text.replace(f'{{{{{key}}}}}', str(value))

    doc.save(output_path)

def send_email(email_to, subject, body, attachments=None):
    email_from = 'itprojectsec@gmail.com'
    password = 'nAXx5}FrxgyM39.u'

    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = COMMASPACE.join(email_to)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    for attachment_path in attachments or []:
        with open(attachment_path, 'rb') as f:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(f.read())
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
        msg.attach(attachment)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_from, password)
    text = msg.as_string()
    server.sendmail(email_from, email_to, text)
    server.quit()

def chatbot_interaction():
    print("Bienvenido soy Chaos, estoy listo para ayudarte!")

    user_data = request_user_data()
    if check_requirements(user_data[2], user_data[3]):
        while True:
            proceed = input("Cumples con los requisitos. ¿Deseas continuar con el trámite? (Sí/No): ").lower()
            if proceed in ['sí', 'si', 'no']:
                break
            print("Por favor, responde con 'Sí' o 'No'.")

        if proceed == 'no':
            print("Entiendo. Si necesitas ayuda en otro momento, no dudes en preguntar.")
            return

        fingerprint_code = input("Por favor, ingresa el código de huella dactilar que se encuentra en tu cédula: ")

        user_info = {
            'full_name': user_data[0],
            'id_number': user_data[1],
            'age': user_data[2],
            'total_income': user_data[3],
            'address': user_data[4],
            'nationality': user_data[5],
            'cadastral_code': user_data[6],
            'birthdate': user_data[7],
            'phone_number': user_data[8],
            'marital_status': user_data[9],
            'spouse_data': user_data[10],
            'property_acquisition': user_data[11],
            'fingerprint_code': fingerprint_code,
            'email': user_data[12]
        }
        save_user_data(user_info)


        print("Puedes comenzar a hacer preguntas. Si deseas terminar, escribe 'salir'.")
        while True:
            message = input("")
            if message.lower() == 'salir':
                print("¡Hasta luego!")
                break
            ints = predict_class(message)
            res = get_response(ints, intents)
            print(res)
    else:
        print("Lo siento, no cumples con los requisitos para acceder a esta información.")
    
    user_data_file = 'user_data.json'
    if os.path.exists(user_data_file):
        with open(user_data_file, 'r') as file:
            user_data_list = json.load(file)
            if user_data_list:
                user_data = user_data_list[-1]
                fill_form(user_data)
                send_email([user_data['email']], 'Formulario completado', 'Aquí está el formulario completado.', 'peticion.docx')
            else:
                print('No hay datos de usuario para completar el formulario.')
    else:
        print('No se encontró el archivo user_data.json.')

if __name__ == "__main__":
    chatbot_interaction()
