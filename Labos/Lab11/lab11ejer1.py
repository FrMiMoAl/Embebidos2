import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.preprocessing import StandardScaler
import pickle

df = pd.read_excel("Jugadores.xlsx")

# Separar 
X = df[['Posicion Num', 'Edad', 'Partidos Jugados', 'Goles', 
        'Asistencias', 'Penales Acertados', 'Tarjetas Amarillas', 
        'Tarjetas Rojas', 'Goles Esperados']].values
y = df['Label'].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = Sequential([
    Dense(32, activation='relu', input_shape=(9,)),
    Dense(16, activation='relu'),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

model.fit(X_scaled, y, epochs=50, batch_size=16, verbose=1)

model.save('modelo_jugadores.h5')
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

print("\n✓ Modelo y scaler guardados")