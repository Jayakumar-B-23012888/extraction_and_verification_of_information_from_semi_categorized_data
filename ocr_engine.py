import easyocr
import torch
from preprocess import preprocess_for_ocr

# Automatically use GPU if available, otherwise fall back to CPU
use_gpu = torch.cuda.is_available()
reader = easyocr.Reader(['en'], gpu=use_gpu)

def extract_text(image_path):
    processed = preprocess_for_ocr(image_path)
    result = reader.readtext(processed, detail=0)
    return "\n".join(result)

