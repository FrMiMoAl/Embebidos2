#!/bin/bash

# Puerto de la Pico (ajústalo si es necesario)
PIPICO=/dev/ttyACM0

# Lista de archivos a subir (solo los que quieres)
FILES=("Steering.py" "Motors.py" "UARTHandler.py" "USonic.py" "main.py")

# Verificar que el puerto exista
if [ ! -e "$PIPICO" ]; then
    echo "Error: no se encontró el dispositivo en $PIPICO"
    exit 1
fi

echo "Subiendo archivos a la Pico en $PIPICO ..."

# Subir cada archivo del listado
for f in "${FILES[@]}"; do
    if [ ! -f "$f" ]; then
        echo "Advertencia: archivo $f no encontrado, se salta."
        continue
    fi

    echo "Subiendo $f ..."
    if ! sudo mpremote connect $PIPICO fs cp "$f" : ; then
        echo "Error: no se pudo subir $f"
        exit 1
    fi
done

# Reiniciar la Pico para ejecutar main.py
echo "Reiniciando la Pico..."
if ! sudo mpremote connect $PIPICO reset ; then
    echo "Error: no se pudo reiniciar la Pico"
    exit 1
fi

echo "¡Archivos subidos y Pico reiniciada correctamente!"
