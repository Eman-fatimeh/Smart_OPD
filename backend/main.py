from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# PATIENT MODEL
# ---------------------------
class Patient(BaseModel):
    firstName: str
    lastName: str
    age: int
    dob: str | None = None
    blood: str | None = None
    gender: str

    phone: str
    email: str | None = None
    address: str | None = None
    emergencyName: str | None = None
    emergencyPhone: str | None = None

    department: str
    visitType: str
    complaint: str
    allergies: str | None = None


# fake database (temporary)
patients = []
patient_counter = 1025


@app.post("/register-patient")
def register_patient(data: Patient):
    global patient_counter

    patient_counter += 1
    patient_id = f"P-{patient_counter}"

    new_patient = {
        "id": patient_id,
        "data": data.model_dump(),
        "time": datetime.now().strftime("%H:%M")
    }

    patients.append(new_patient)

    return {
        "success": True,
        "message": "Patient registered successfully",
        "patientId": patient_id,
        "redirect": "register.html"
    }


@app.get("/patients")
def get_patients():
    return patients
    
class LoginData(BaseModel):
    username: str
    password: str
    role: str

users = {
    "admin": {
        "username": "admin",
        "password": "1234",
        "role": "admin"
    },

    "receptionist": {
        "username": "reception",
        "password": "1234",
        "role": "receptionist"
    }
}

@app.post("/login")
async def login(data: LoginData):

    for user in users.values():

        if (
            data.username == user["username"]
            and data.password == user["password"]
            and data.role == user["role"]
        ):

            redirect_page = "index.html"

            if user["role"] == "receptionist":
                redirect_page = "register.html"

            return {
                "success": True,
                "redirect": redirect_page
            }

    raise HTTPException(
        status_code=401,
        detail="Invalid credentials"
    )