from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# =========================
# DATABASE
# =========================
DATABASE_URL = "sqlite:///./patients.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# =========================
# TABLES
# =========================

class PatientDB(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    patient_id = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    department = Column(String)
    time = Column(String)


class DoctorDB(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True)
    doctor_name = Column(String)
    specialization = Column(String)
    department = Column(String)
    status = Column(String)
    schedule = Column(String)


class TokenDB(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    token_number = Column(String)
    patient_id = Column(String)
    patient_name = Column(String)
    department = Column(String)
    doctor_name = Column(String)
    status = Column(String)
    time = Column(String)


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String)


Base.metadata.create_all(bind=engine)

# =========================
# APP
# =========================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =========================
# MODELS
# =========================

class LoginData(BaseModel):
    username: str
    password: str
    role: str


class Patient(BaseModel):
    firstName: str
    lastName: str
    age: int
    gender: str
    department: str


class Doctor(BaseModel):
    name: str
    specialization: str
    department: str
    status: str
    schedule: str


# =========================
# LOGIN (FIXED)
# =========================
@app.post("/login")
def login(data: LoginData):

    # HARD-CODED USERS
    users = {
        "admin": {
            "password": "12345@",
            "role": "admin",
            "redirect": "admin.html"
        },
        "reception": {
            "password": "12345@",
            "role": "receptionist",
            "redirect": "register.html"
        },

        # DOCTORS (YOUR 4 DOCTORS)
        "shanzaymalik": {
            "password": "12345@",
            "role": "doctor",
            "redirect": "doctor.html"
        },
        "alikhan": {
            "password": "12345@",
            "role": "doctor",
            "redirect": "doctor.html"
        },
        "faristaheer": {
            "password": "12345@",
            "role": "doctor",
            "redirect": "doctor.html"
        },
        "imranhameed": {
            "password": "12345@",
            "role": "doctor",
            "redirect": "doctor.html"
        }
    }

    user = users.get(data.username.lower().replace(" ", ""))

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if data.password != user["password"] or data.role != user["role"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "success": True,
        "role": user["role"],
        "username": data.username,
        "redirect": user["redirect"]
    }

# =========================
# PATIENTS
# =========================
@app.post("/register-patient")
def register_patient(data: Patient):

    db = SessionLocal()

    patient_id = f"P-{int(datetime.now().timestamp())}"

    patient = PatientDB(
        patient_id=patient_id,
        first_name=data.firstName,
        last_name=data.lastName,
        age=data.age,
        gender=data.gender,
        department=data.department,
        time=datetime.now().strftime("%H:%M")
    )

    db.add(patient)
    db.commit()
    db.close()

    return {"success": True, "patientId": patient_id}


@app.get("/patients")
def get_patients():

    db = SessionLocal()
    patients = db.query(PatientDB).all()
    db.close()

    return [
        {
            "id": p.patient_id,

            # IMPORTANT
            "firstName": p.first_name,
            "lastName": p.last_name,

            "name": f"{p.first_name} {p.last_name}",

            "age": p.age,
            "gender": p.gender,
            "department": p.department,
            "time": p.time
        }
        for p in patients
    ]
# =========================
# DOCTORS
# =========================
@app.post("/add-doctor")
def add_doctor(data: Doctor):

    db = SessionLocal()

    doctor = DoctorDB(
        doctor_name=data.name,
        specialization=data.specialization,
        department=data.department,
        status=data.status,
        schedule=data.schedule
    )

    db.add(doctor)

    # AUTO CREATE LOGIN USER
    username = data.name.lower().replace(" ", "")

    existing_user = db.query(UserDB).filter_by(username=username).first()

    if not existing_user:
        new_user = UserDB(
            username=username,
            password="1234",
            role="doctor"
        )
        db.add(new_user)

    db.commit()
    db.close()

    return {
        "success": True,
        "login_username": username,
        "password": "1234"
    }


@app.get("/doctors")
def get_doctors():

    db = SessionLocal()
    doctors = db.query(DoctorDB).all()
    db.close()

    return [
        {
            "id": d.id,
            "name": d.doctor_name,
            "specialization": d.specialization,
            "department": d.department,
            "status": d.status,
            "schedule": d.schedule
        }
        for d in doctors
    ]


@app.delete("/delete-doctor/{doctor_id}")
def delete_doctor(doctor_id: int):

    db = SessionLocal()

    doc = db.query(DoctorDB).filter_by(id=doctor_id).first()

    if not doc:
        raise HTTPException(404, "Doctor not found")

    db.delete(doc)
    db.commit()
    db.close()

    return {"success": True}


# =========================
# TOKENS
# =========================
@app.post("/generate-token/{patient_id}")
def generate_token(patient_id: str):

    db = SessionLocal()

    patient = db.query(PatientDB).filter_by(patient_id=patient_id).first()

    if not patient:
        raise HTTPException(404, "Patient not found")

    count = db.query(TokenDB).count()
    token_number = f"T-{str(count + 1).zfill(3)}"

    token = TokenDB(
        token_number=token_number,
        patient_id=patient.patient_id,
        patient_name=f"{patient.first_name} {patient.last_name}",
        department=patient.department,
        doctor_name="",
        status="Waiting",
        time=datetime.now().strftime("%H:%M")
    )

    db.add(token)
    db.commit()
    db.close()

    return {"success": True, "token": token_number}


@app.get("/tokens")
def get_tokens():

    db = SessionLocal()
    tokens = db.query(TokenDB).all()
    db.close()

    return [
        {
            "token": t.token_number,
            "patient": t.patient_name,
            "department": t.department,
            "status": t.status,
            "time": t.time
        }
        for t in tokens
    ]
import os
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )   