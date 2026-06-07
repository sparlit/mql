# Project: Autonomous AutoTrader (AAT) V5.0.0
# Description: Model Quantization Script (FinBERT -> ONNX INT8)

import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from optimum.onnxruntime import ORTModelForSequenceClassification, ORTQuantizer
from optimum.onnxruntime.configuration import AutoQuantizationConfig

def quantize_finbert():
    model_id = "ProsusAI/finbert"
    save_dir = "src/shared/models/finbert_onnx"
    os.makedirs(save_dir, exist_ok=True)

    print(f"Loading and exporting {model_id} to ONNX...")
    # Load and export the model to ONNX
    model = ORTModelForSequenceClassification.from_pretrained(model_id, export=True)
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    # Save the ONNX model and tokenizer
    model.save_pretrained(save_dir)
    tokenizer.save_pretrained(save_dir)

    print("Starting INT8 Quantization...")
    # Initialize the quantizer
    quantizer = ORTQuantizer.from_pretrained(model)

    # Define quantization configuration (INT8 for CPU)
    dqconfig = AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=False)

    # Apply quantization
    quantizer.quantize(
        save_dir=save_dir,
        quantization_config=dqconfig,
    )
    print(f"Quantization complete. Model saved in {save_dir}")

if __name__ == "__main__":
    try:
        quantize_finbert()
    except Exception as e:
        print(f"Quantization failed: {e}")
        # Fallback: In a real low-spec environment, we would pre-bundle this or download the artifact
