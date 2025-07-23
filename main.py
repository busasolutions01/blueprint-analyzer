
from fastapi import FastAPI, UploadFile
import cv2, pytesseract, numpy as np
from pdf2image import convert_from_bytes
import pandas as pd

app = FastAPI()

@app.post("/upload")
async def process_pdf(file: UploadFile):
    content = await file.read()
    images = convert_from_bytes(content)
    data = []

    for i, image in enumerate(images):
        img_np = np.array(image)
        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

        text = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for idx, word in enumerate(text['text']):
            if word.upper() in ["SIDEWALK", "CURB", "CONC."]:
                x, y, w, h = text['left'][idx], text['top'][idx], text['width'][idx], text['height'][idx]
                area_px = w * h
                area_ft = area_px * scale_factor()
                data.append({"label": word, "area_ft2": area_ft})

    df = pd.DataFrame(data)
    df.to_excel("output.xlsx", index=False)
    return {"status": "success", "areas_detected": len(df)}

def scale_factor():
    return 0.25
