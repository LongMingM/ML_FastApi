from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Optional, Literal

import json
def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)
    return data

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)

app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="The ID of the patient", example="P001")]
    name: Annotated[str, Field(..., description="The name of the patient", example="John Doe")]
    city: Annotated[str, Field(..., description="The city of the patient", example="New York")]
    age: Annotated[int, Field(..., gt=0, lt=120, description="The age of the patient", example=30)]
    gender: Annotated[str, Field(..., description="The gender of the patient", example="Male")]
    height: Annotated[float, Field(..., gt=0, description="The height of the patient in cm", example=180)]
    weight: Annotated[float, Field(..., gt=0, description="The weight of the patient in kg", example=75)]
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height / 100) ** 2, 2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 24.9:
            return "Healthy"
        elif 25 <= self.bmi < 29.9:
            return "Overweight"
        else:
            return "Obese"
        
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0, lt=120)]
    gender: Annotated[Optional[Literal['Male', 'Female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]

@app.get("/")
def hello():
    return {'message': "Patient Management System Api"}

@app.get("/about")
def about():
    return {'message': "A Fully functional Api to manage your patients records"}

@app.get("/view")
def view():
    data = load_data()
    return {'patients': data}

@app.get("/view/{patient_id}")
def view_patient(patient_id: str = Path(..., description="The ID of the patient to view",example_id="P001")):
    data = load_data()
    if patient_id in data:
        return {'patient': data[patient_id]}
    else:
        return HTTPException(status_code=404, detail="Patient not found")
    

@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description="Sort on the height, weight or bmi"),
                  order: str = Query(..., description="Sort order: asc or desc")):
    
    valid_fields = ['height', 'weight', 'bmi']
    if sort_by not in valid_fields:
        return HTTPException(status_code=400, detail=f"Invalid sort field selected from {valid_fields}")
    
    if order not in ['asc', 'desc']:
        return HTTPException(status_code=400, detail="Invalid sort order selected. Please select asc or desc")
    
    data = load_data()
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=(order == 'desc'))
    return sorted_data

@app.post('/create')
def create_patient(patient: Patient):
    # Load existing data
    data = load_data()

    # Check if patient with the same ID already exists
    if patient.id in data:
        return HTTPException(status_code=400, detail="Patient with this ID already exists")
    
    # Add the new patient to the data
    data[patient.id] = patient.model_dump(exclude=['id'])
    
    with open('patients.json', 'w') as f:
        json.dump(data, f, indent=4)

    # save into json file
    save_data(data)

    return JSONResponse(status_code=201, content={"message": "Patient created successfully"})


@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):
    """Update a patient"""
    data = load_data()
    # Check if the patient exists
    if patient_id not in data:
        return JSONResponse(status_code=404, content={"message": "Patient not found"})

    # Update the patient
    existring_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existring_patient_info[key] = value

    # trans the updated patient info back to the data
    existring_patient_info['id'] = patient_id
    patient_pydantic_obj = Patient(**existring_patient_info)
    existring_patient_info = patient_pydantic_obj.model_dump(exclude=['id'])
    data[patient_id] = existring_patient_info

    # save into json file
    save_data(data)

    return JSONResponse(status_code=200, content={"message": "Patient updated successfully"})


@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    data = load_data()
    if patient_id not in data:
        return JSONResponse(status_code=404, content={"message": "Patient not found"})
    del data[patient_id]
    save_data(data)
    return JSONResponse(status_code=200, content={"message": "Patient deleted successfully"})
