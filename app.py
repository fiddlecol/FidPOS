from flask import Flask
from models import db
from routes.main import bp as main_bp
from routes.categories import bp as categories_bp
from routes.items import bp as items_bp
from routes.sales import bp as sales_bp
from routes.reports import bp as reports_bp
from routes.settings import bp as settings_bp
import os
from dotenv import load_dotenv
from utils.printer import initialize_printer
from utils.backup import backup_database
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import atexit
import logging

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    with app.app_context():
        db.create_all()
        initialize_printer()

    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        func=backup_database,
        trigger=IntervalTrigger(hours=24),
        args=["backup.sql"],
        id='database_backup_job',
        name='Backup database every 24 hours',
        replace_existing=True
    )
    atexit.register(lambda: scheduler.shutdown())

    @app.context_processor
    def inject_year():
        return {'current_year': datetime.now().year}

    return app
