import os

def borrar_todo(directorio='.'):
    # Recorre todos los archivos y directorios dentro del directorio especificado
    for archivo in os.listdir(directorio):
        ruta = directorio + '/' + archivo  # Concatenar la ruta directamente
        if os.stat(ruta)[0] == 0x4000:  # Verifica si es un directorio (0x4000 es un código para directorios en MicroPython)
            borrar_todo(ruta)  # Llamada recursiva para subdirectorios
            os.rmdir(ruta)     # Elimina el subdirectorio vacío
        else:
            os.remove(ruta)    # Elimina el archivo

# Llamar a la función para borrar todo en el directorio actual (el sistema de archivos raíz)
borrar_todo()
