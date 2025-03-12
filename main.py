from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Настройки базы данных
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///schedules.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Создаем объект базы данных
db = SQLAlchemy(app)

from datetime import datetime, timedelta

# Определяем модель для хранения данных о расписании лекарств
class Schedule(db.Model):
    schedule_id = db.Column(db.Integer, primary_key=True)
    medicine_name = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)
    therapy_duration = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Создаем таблицы в базе данных
with app.app_context():
    db.create_all()

@app.route("/schedules", methods=["GET"])
def getData():
    user_id = request.args.get("user_id") # Получаем значение "user_id"из query-параметра
    schedule_id = request.args.get("schedule_id") # Получаем значение "schedule_id" из query-параметра

    if user_id and schedule_id:
        schedule = Schedule.query.filter_by(schedule_id = schedule_id, user_id = user_id).first()
        if not schedule:
            return jsonify({"error": "schedule not found"}), 404
        
        intake_times = [] # Будет храниться время принятия лекарства в течении 8:00 - 22:00 текущего дн
        # Логика вычисления времени приема лекарств [17:45, 19:45, 21:45]
            # Будет зависеть от:
                # 1) Переодичности frequency
                # 2) Приемы не раньше 8:00 и не позже 22:00
                # 3) Первый прием зависит от даты и времени назначения лекарства
                    # createdAt=12.03.25, 17:43, тогда intake_times = [17:45, 19:45, 21:45]
        # 1. Присваиваем нужные данные
        currentFrequency = schedule.frequency # Переодичности frequency в часах # 2
        dateReference = roundDate(schedule.created_at) # Присвоение времени создания записи (стартовое время приема)
        # Округление нужного времени "14:59" -> "15:00"
        
        return jsonify({
            "scheduleID": schedule.schedule_id, # id текущего расписания
            "userID": schedule.user_id, # id текущего пациента
            "medicineName": schedule.medicine_name, # Лекарство
            "frequency": schedule.frequency, # Периодичность приема
            "createdAt":schedule.created_at, # Дата назначения
            "intakeTimes": intake_times,
            "testTime": dateReference
            # "therapyDuration": schedule.therapy_duration,
        })

    elif user_id: # Если переданы только user_id - вернем все расписания по данному пользователю
        schedules = Schedule.query.filter_by(user_id = user_id).all()
    else: # Если user_id не передан, то возвращаем все данные
        schedules = Schedule.query.all()

    result = [
        {
            "schedule_id": schedule.schedule_id,
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
        "id": new_schedule.schedule_id
    }), 201

def roundDate(dt):
    minutes = (dt.minute // 15 + 1) * 15
    if minutes == 60:
        dt += timedelta(hours=1)
        minutes = 0
    currentDate = dt.replace(minute = minutes, second = 0,  microsecond = 0)
    return currentDate.strftime("%H:%M")

if __name__ == "__main__":
    app.run(debug=True)
