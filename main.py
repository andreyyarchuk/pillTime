from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Настройки базы данных
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///schedules.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Создаем объект базы данных
db = SQLAlchemy(app)

# Определяем модель для хранения данных о расписании лекарств
class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medicine_name = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)
    therapy_duration = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

# Создаем таблицы в базе данных
with app.app_context():
    db.create_all()

@app.route("/schedules", methods=["GET"])
def getData():
    schedules = Schedule.query.all()
    result = [
        {
            "id": schedule.id,
            "medicineName": schedule.medicine_name,
            "frequency": schedule.frequency,
            "therapyDuration": schedule.therapy_duration,
            "userID": schedule.user_id,
        }
        for schedule in schedules
    ]
    return jsonify(result)

@app.route("/schedules", methods=["POST"])
def createData():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    new_schedule = Schedule(
        medicine_name=data.get("medicineName", "Unknown"),
        frequency=data.get("frequency", "Unknown"),
        therapy_duration=data.get("therapyDuration", "Unknown"),
        user_id=data.get("userID", 0),
    )

    db.session.add(new_schedule)
    db.session.commit() #фиксация измениний в базе данных

    return jsonify({
        "message": "Запись добавлена успешно",
        "id": new_schedule.id
    }), 201

if __name__ == "__main__":
    app.run(debug=True)
