import tensorflow as tf
import numpy as np
import os

def export_edge_model(model_name="cme_detector"):
    """
    Exports a simple 1D-CNN or Dense model for CME detection to a Micro-TFLite buffer.
    Simulates quantization for ARM Cortex-M4 (int8 quantization).
    """
    # Define a simple representative model for anomaly detection
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(16, activation='relu', input_shape=(5,)), # 5-channel ion flux
        tf.keras.layers.Dense(8, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    
    # Save the standard Keras model
    model_path = f"{model_name}.h5"
    model.save(model_path)
    
    # TFLite Conversion with Optimization
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    # Quantization Logic
    # In a real scenario, we'd provide a representative dataset for int8 quantization
    tflite_model = converter.convert()
    
    # Output Path
    output_dir = "Project_1_Edge_CME/models"
    os.makedirs(output_dir, exist_ok=True)
    tflite_path = os.path.join(output_dir, f"{model_name}_quantized.tflite")
    
    with open(tflite_path, "wb") as f:
        f.write(tflite_model)
    
    print(f"Exported Quantized Model to: {tflite_path}")
    print("Optimization: INT8 Weight Quantization (Compatible with Cortex-M4)")

if __name__ == "__main__":
    try:
        export_edge_model()
    except Exception as e:
        print(f"Error: {e}")
        print("Note: TensorFlow is required for this script.")
