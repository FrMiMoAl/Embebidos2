
import tensorflow as tf
import numpy as np

X_train = np.array([-2, -1, 0, 1, 2, 3], dtype=float)
Y_train = 3 * X_train + 2

model = tf.keras.Sequential([
    tf.keras.layers.Dense(8, activation='relu', input_shape=[1]),
    tf.keras.layers.Dense(4, activation='relu'),
    tf.keras.layers.Dense(1)
])
model.compile(optimizer='adam', loss='mse')
model.fit(X_train, Y_train, epochs=500, verbose=0)


print("X=5  → ", model.predict(np.array([5.0]))[0][0])
print("X=3.3→ ", model.predict(np.array([3.3]))[0][0])