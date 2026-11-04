# -*- coding: utf-8 -*-
"""Convierte el modelo Keras (.keras) a ONNX para usarlo con OpenCV.

Ejecutar UNA sola vez con el Python 3.12 del entorno .venv:
    .venv\\Scripts\\python.exe convertir_a_onnx.py
"""

import os

import tensorflow as tf
import tf2onnx

RUTA_KERAS = "modelo_trashnet_grupo6.keras"
RUTA_ONNX = "modelo_trashnet_grupo6.onnx"


def main():
    if not os.path.exists(RUTA_KERAS):
        raise FileNotFoundError(f"No se encontro {RUTA_KERAS}")

    print(f"Cargando {RUTA_KERAS}...")
    modelo = tf.keras.models.load_model(RUTA_KERAS, compile=False)

    nombre_entrada = modelo.inputs[0].name
    print(f"Entrada: {nombre_entrada}  forma: {modelo.inputs[0].shape}")
    print(f"Salida:  {modelo.outputs[0].name}  forma: {modelo.outputs[0].shape}")

    print("Convirtiendo a ONNX (esto puede tardar un poco)...")
    try:
        tf2onnx.convert.from_keras(
            modelo,
            opset=13,
            inputs_as_nchw=[nombre_entrada],
            output_path=RUTA_ONNX,
        )
    except Exception as error:
        print(f"Conversion directa fallo ({error}). Probando con tf.function...")
        firma = [tf.TensorSpec([None, 224, 224, 3], tf.float32, name="input")]

        @tf.function(input_signature=firma)
        def inferencia(x):
            return modelo(x, training=False)

        tf2onnx.convert.from_function(
            inferencia,
            input_signature=firma,
            opset=13,
            inputs_as_nchw=["input"],
            output_path=RUTA_ONNX,
        )

    print(f"Listo: {RUTA_ONNX}")


if __name__ == "__main__":
    main()
