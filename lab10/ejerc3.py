import tensorflow as tf

model_filename = 'modelo_entrenado.h5'

loaded_model = tf.keras.models.load_model(model_filename)

if 'tokenizer' not in locals():
    print("Error: El objeto 'tokenizer' no está disponible. Por favor, asegúrate de haber ejecutado la celda donde se inicializa el Tokenizer.")
else:
    user_message = input("Ingresa un mensaje para verificar si es spam o no: ")

    # Preprocesar el mensaje del usuario
    seqs_user = tokenizer.texts_to_sequences([user_message])
    X_user = tf.keras.preprocessing.sequence.pad_sequences(seqs_user, maxlen=50)

    # Realizar la predicción
    prediction = loaded_model.predict(X_user)[0][0]

    # Interpretar el resultado
    if prediction >= 0.5:
        print(f"\nEl mensaje es: SPAM (Probabilidad: {prediction:.2f})")
    else:
        print(f"\nEl mensaje es: HAM (Probabilidad: {prediction:.2f})")