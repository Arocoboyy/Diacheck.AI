from flask import Flask, render_template, request, send_from_directory
import os
from ultralytics import YOLO
from werkzeug.utils import secure_filename
from PIL import Image
import pillow_heif

app = Flask(__name__)

# ===============================
# Konfigurasi Upload
# ===============================
UPLOAD_FOLDER = "images_upload"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'heic'}  # tambahkan heic
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ===============================
# Load Dua Model
# ===============================
models = YOLO("best100.pt")

# ===============================
# Fungsi bantu: cek ekstensi
# ===============================
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ===============================
# Halaman Utama
# ===============================
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# ===============================
# Tampilkan Gambar Upload
# ===============================
@app.route("/images_upload/<filename>")
def display_image(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ===============================
# Prediksi
# ===============================
@app.route("/", methods=["POST"])
def predict():
    if 'imagefile' not in request.files:
        return render_template("index.html", error="❌ No file uploaded!")

    imagefile = request.files["imagefile"]
    if imagefile.filename == "":
        return render_template("index.html", error="❌ Empty filename!")

    if not allowed_file(imagefile.filename):
        return render_template("index.html", error="❌ Unsupported file format! Use .png, .jpg, .jpeg, .webp, or .heic")

    # Pilih model dari dropdown (default anedet)
    
    # Simpan file asli
    filename = secure_filename(imagefile.filename)
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    imagefile.save(image_path)

    # Jika HEIC → convert ke JPG
    if filename.lower().endswith(".heic"):
        try:
            heif_file = pillow_heif.read_heif(image_path)
            img = Image.frombytes(
                heif_file.mode, heif_file.size, heif_file.data, "raw"
            ).convert("RGB")

            new_filename = filename.rsplit(".", 1)[0] + ".jpg"
            new_image_path = os.path.join(app.config["UPLOAD_FOLDER"], new_filename)
            img.save(new_image_path, "JPEG")

            os.remove(image_path)  # hapus HEIC asli
            filename = new_filename
            image_path = new_image_path
        except Exception as e:
            return render_template("index.html", error=f"❌ Failed to convert HEIC: {e}")

    try:
        # Prediksi
        results = models(image_path)

        if results and results[0].boxes is not None and len(results[0].boxes) > 0:
            pred_class = results[0].names[int(results[0].boxes.cls[0])]
            percent = f"{float(results[0].boxes.conf[0]) * 100:.2f}"

            return render_template(
                "index.html",
                prediction=pred_class,
                percent=percent,
                image_file=filename,
            )
        else:
            return render_template("index.html", error=" No object detected.", image_file=filename)

    except Exception as e:
        return render_template("index.html", error=f"❌ Error during prediction: {e}")

# ===============================
# Run App
# ===============================
if __name__ == "__main__":
    app.run(port=5005, debug=False)
