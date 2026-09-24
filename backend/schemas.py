from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# AI output schema — this is what Gemini is forced to return via
# response_schema. Mirrors the structure suggested in the assignment brief.
# ---------------------------------------------------------------------------


class PatientInformation(BaseModel):
    name: Optional[str] = None
    age: Optional[str] = None
    sex: Optional[str] = None
    other_identifiers: Optional[str] = None


class VitalSigns(BaseModel):
    blood_pressure: Optional[str] = None
    heart_rate: Optional[str] = None
    temperature: Optional[str] = None
    respiratory_rate: Optional[str] = None
    oxygen_saturation: Optional[str] = None
    other: Optional[str] = None


class ClinicalReport(BaseModel):
    report_summary: str
    patient_information: PatientInformation = Field(default_factory=PatientInformation)
    symptoms: list[str] = Field(default_factory=list)
    diagnoses: list[str] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)
    vitals: VitalSigns = Field(default_factory=VitalSigns)
    allergies: list[str] = Field(default_factory=list)
    clinical_observations: list[str] = Field(default_factory=list)
    clinical_concerns: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    potential_inconsistencies: list[str] = Field(default_factory=list)
    requires_review: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# API schemas — what the backend returns to the frontend.
# ---------------------------------------------------------------------------


class ReportListItem(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    created_at: datetime
    input_type: str
    status: str
    report_summary: Optional[str] = None


class ReportDetail(ReportListItem):
    full_report: Optional[dict] = None
    error_message: Optional[str] = None
