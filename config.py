import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")


class Config:
    # --- Core Flask ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "fidpos_secret_key")

    # --- Database (stored in instance/) ---
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(INSTANCE_DIR, 'fidpos.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Flask Uploads / Media ---
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

    # --- Misc ---
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")


class DevelopmentConfig(Config):
    DEBUG = True


# Helper for allowed file uploads
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


# Ensure instance & upload folders exist
os.makedirs(INSTANCE_DIR, exist_ok=True)
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
