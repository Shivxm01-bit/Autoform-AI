"""Pydantic data models and schemas for Google Form Automation API."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class StudentProfile(BaseModel):
    """
    Data model representing a Corporate Resource Center (CRC) student profile.
    Contains Personal & Contact, Academic Record, and Professional Experience fields.
    """

    # =========================================================================
    # 1. Personal & Contact Information
    # =========================================================================
    enrollment_no: Optional[str] = Field(None, description="University Enrollment / Roll Number", examples=["2021BCSE042"])
    full_name: Optional[str] = Field(None, description="Full Name of the candidate", examples=["Alex Mercer"])
    dob: Optional[str] = Field(None, description="Date of Birth (YYYY-MM-DD or DD/MM/YYYY)", examples=["2003-04-12"])
    gender: Optional[str] = Field(None, description="Gender (Male, Female, Other, Prefer not to say)", examples=["Male"])
    home_location: Optional[str] = Field(None, description="Home Location / City / State", examples=["Noida, Uttar Pradesh"])
    permanent_address: Optional[str] = Field(None, description="Permanent Residential Address", examples=["Flat 402, Lotus Boulevard, Sector 100, Noida, UP - 201304"])
    contact_no: Optional[str] = Field(None, description="Primary Contact Number / Mobile", examples=["+91 9876543210"])
    alt_contact_no: Optional[str] = Field(None, description="Alternate / Secondary Contact Number", examples=["+91 9876543211"])
    personal_email: Optional[str] = Field(None, description="Personal Email Address", examples=["alex.mercer.dev@gmail.com"])
    institutional_email: Optional[str] = Field(None, description="Institutional / College Email Address", examples=["alex.mercer@university.edu.in"])
    driving_license_yes_no: Optional[str] = Field(None, description="Driving License Availability (Yes/No)", examples=["Yes"])

    # =========================================================================
    # 2. Academic Record
    # =========================================================================
    school_name: Optional[str] = Field(None, description="School / Department Name", examples=["School of Computer Science & Engineering"])
    category_ug_pg: Optional[str] = Field(None, description="Category / Level of Study (UG/PG)", examples=["UG"])
    course: Optional[str] = Field(None, description="Course / Degree Program", examples=["B.Tech"])
    ug_specialization: Optional[str] = Field(None, description="Undergraduate Branch / Specialization", examples=["Computer Science & Engineering"])
    ug_cgpa: Optional[str] = Field(None, description="Undergraduate Cumulative GPA / CGPA", examples=["8.85"])
    ug_passing_year: Optional[str] = Field(None, description="Undergraduate Passing Year", examples=["2026"])
    pg_specialization: Optional[str] = Field(None, description="Postgraduate Specialization (if applicable)", examples=["AI & Machine Learning"])
    pg_cgpa: Optional[str] = Field(None, description="Postgraduate CGPA (if applicable)", examples=["9.10"])
    pg_passing_year: Optional[str] = Field(None, description="Postgraduate Passing Year (if applicable)", examples=["2028"])
    tenth_percentage: Optional[str] = Field(None, description="Class 10th / Secondary Percentage or CGPA", examples=["92.4%"])
    tenth_board: Optional[str] = Field(None, description="Class 10th Education Board (e.g. CBSE, ICSE, State Board)", examples=["CBSE"])
    tenth_passing_year: Optional[str] = Field(None, description="Class 10th Passing Year", examples=["2020"])
    twelfth_percentage: Optional[str] = Field(None, description="Class 12th / Intermediate / Diploma Percentage", examples=["89.6%"])
    twelfth_board: Optional[str] = Field(None, description="Class 12th Education Board (e.g. CBSE, ISC, State Board)", examples=["CBSE"])
    twelfth_passing_year: Optional[str] = Field(None, description="Class 12th Passing Year", examples=["2022"])

    # =========================================================================
    # 3. Professional Experience & Role Preferences
    # =========================================================================
    internship_organization: Optional[str] = Field(None, description="Internship Organization / Company Name", examples=["Amazon Web Services (AWS)"])
    internship_topic: Optional[str] = Field(None, description="Internship Project Topic / Domain", examples=["Cloud Infrastructure & Microservices Architecture"])
    extra_certifications: Optional[str] = Field(None, description="Additional Courses & Technical Certifications", examples=["AWS Certified Solutions Architect, Oracle Java Associate, Coursera Deep Learning"])
    applying_for_role: Optional[str] = Field(None, description="Applying for Target Role / Position", examples=["Software Development Engineer (SDE)"])

    # =========================================================================
    # 4. Optional / Legacy & Social Fields
    # =========================================================================
    email: Optional[str] = Field(None, description="Generic Email fallback", examples=["alex.mercer@gmail.com"])
    phone: Optional[str] = Field(None, description="Generic Phone fallback", examples=["+1-555-0199"])
    student_id: Optional[str] = Field(None, description="Generic Student ID fallback", examples=["2021BCSE042"])
    date_of_birth: Optional[str] = Field(None, description="Generic DOB fallback", examples=["2003-04-12"])
    university: Optional[str] = Field(None, description="Generic University fallback", examples=["Stanford University"])
    major: Optional[str] = Field(None, description="Generic Major fallback", examples=["Computer Science"])
    degree: Optional[str] = Field(None, description="Generic Degree fallback", examples=["B.Tech"])
    graduation_year: Optional[str] = Field(None, description="Generic Grad Year fallback", examples=["2026"])
    gpa: Optional[str] = Field(None, description="Generic GPA fallback", examples=["8.85"])
    address: Optional[str] = Field(None, description="Generic Address fallback", examples=["Noida, UP"])
    city: Optional[str] = Field(None, description="City", examples=["Noida"])
    state: Optional[str] = Field(None, description="State", examples=["UP"])
    zip_code: Optional[str] = Field(None, description="Zip / Pin code", examples=["201304"])
    country: Optional[str] = Field(None, description="Country", examples=["India"])
    linkedin_url: Optional[str] = Field(None, description="LinkedIn Profile URL", examples=["https://linkedin.com/in/alexmercer"])
    github_url: Optional[str] = Field(None, description="GitHub Profile URL", examples=["https://github.com/alexmercer"])
    portfolio_url: Optional[str] = Field(None, description="Portfolio URL", examples=["https://alexmercer.dev"])
    resume_url: Optional[str] = Field(None, description="Resume URL", examples=["https://alexmercer.dev/resume.pdf"])
    tech_stack: Optional[str] = Field(None, description="Tech Stack & Skills", examples=["React, Python, FastAPI, TypeScript, PostgreSQL"])
    bio: Optional[str] = Field(None, description="Short Bio", examples=["Passionate software engineer."])

    # Dynamic / Custom fields
    custom_fields: Dict[str, Any] = Field(
        default_factory=dict,
        description="Any custom key-value pairs for dynamic form matching"
    )

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    def to_flattened_dict(self) -> Dict[str, str]:
        """Flatten profile attributes and custom fields into a comprehensive key-value dictionary."""
        flat: Dict[str, str] = {}

        # Add all model fields
        for key, value in self.model_dump(exclude={"custom_fields"}).items():
            if value is not None and str(value).strip() != "":
                flat[key] = str(value).strip()

        # Bidirectional Fallback bridges for seamless matching
        # Email
        if "personal_email" in flat and "email" not in flat:
            flat["email"] = flat["personal_email"]
        if "email" in flat and "personal_email" not in flat:
            flat["personal_email"] = flat["email"]

        # Phone / Contact
        if "contact_no" in flat and "phone" not in flat:
            flat["phone"] = flat["contact_no"]
        if "phone" in flat and "contact_no" not in flat:
            flat["contact_no"] = flat["phone"]

        # Enrollment / Student ID
        if "enrollment_no" in flat and "student_id" not in flat:
            flat["student_id"] = flat["enrollment_no"]
        if "student_id" in flat and "enrollment_no" not in flat:
            flat["enrollment_no"] = flat["student_id"]

        # DOB / Date of birth
        if "dob" in flat and "date_of_birth" not in flat:
            flat["date_of_birth"] = flat["dob"]
        if "date_of_birth" in flat and "dob" not in flat:
            flat["dob"] = flat["date_of_birth"]

        # CGPA / GPA
        if "ug_cgpa" in flat and "gpa" not in flat:
            flat["gpa"] = flat["ug_cgpa"]
        if "gpa" in flat and "ug_cgpa" not in flat:
            flat["ug_cgpa"] = flat["gpa"]

        # Specialization / Major
        if "ug_specialization" in flat and "major" not in flat:
            flat["major"] = flat["ug_specialization"]
        if "major" in flat and "ug_specialization" not in flat:
            flat["ug_specialization"] = flat["major"]

        # Passing Year / Graduation Year
        if "ug_passing_year" in flat and "graduation_year" not in flat:
            flat["graduation_year"] = flat["ug_passing_year"]
        if "graduation_year" in flat and "ug_passing_year" not in flat:
            flat["ug_passing_year"] = flat["graduation_year"]

        # Address
        if "permanent_address" in flat and "address" not in flat:
            flat["address"] = flat["permanent_address"]
        if "address" in flat and "permanent_address" not in flat:
            flat["permanent_address"] = flat["address"]

        # School / University
        if "school_name" in flat and "university" not in flat:
            flat["university"] = flat["school_name"]
        if "university" in flat and "school_name" not in flat:
            flat["school_name"] = flat["university"]

        # Add custom fields
        if self.custom_fields:
            for k, v in self.custom_fields.items():
                if v is not None and str(v).strip() != "":
                    flat[str(k)] = str(v).strip()

        return flat


class FormQuestion(BaseModel):
    """Represents an extracted question/field from a Google Form."""
    item_id: Optional[int] = None
    entry_id: str = Field(..., description="The Google Form entry parameter (e.g. '12345678')")
    title: str = Field(..., description="The question title / prompt")
    description: Optional[str] = None
    question_type: Optional[int] = Field(None, description="Google form question type ID")
    options: Optional[List[str]] = Field(default_factory=list, description="Available options if multiple choice or dropdown")
    required: bool = False


class MatchedField(BaseModel):
    """Represents a successfully mapped form question to a student profile field."""
    entry_id: str
    question_title: str
    profile_field: str
    value: str


class GenerateLinkRequest(BaseModel):
    """Request payload for POST /api/generate-link."""

    form_url: str = Field(
        ...,
        description="Public Google Form URL (e.g. https://docs.google.com/forms/d/e/.../viewform)",
        examples=["https://docs.google.com/forms/d/e/1FAIpQLScExampleFormId12345/viewform"]
    )
    student: StudentProfile = Field(
        ...,
        description="Corporate Resource Center (CRC) student profile information"
    )
    custom_mapping: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional manual map of exact entry_id or question keywords to student profile field names",
        examples=[{"entry.12345678": "personal_email", "Enrollment No": "enrollment_no"}]
    )
    auto_match: bool = Field(
        default=True,
        description="Whether to use intelligent semantic/keyword matching for question titles"
    )

    @field_validator("form_url")
    @classmethod
    def validate_google_form_url(cls, v: str) -> str:
        clean = v.strip()
        if "docs.google.com/forms" not in clean and "forms.gle" not in clean:
            raise ValueError("URL must be a valid Google Forms URL (docs.google.com/forms or forms.gle)")
        return clean


class GenerateLinkResponse(BaseModel):
    """Response payload for POST /api/generate-link."""

    form_title: Optional[str] = Field(None, description="Title of the Google Form extracted from metadata")
    original_url: str = Field(..., description="The input Google Form URL")
    prefilled_url: str = Field(..., description="The generated pre-filled Google Form URL")
    submit_url: Optional[str] = Field(None, description="The direct /formResponse endpoint for programmatic POST submission")
    matched_fields: List[MatchedField] = Field(
        default_factory=list,
        description="List of form entries matched and populated"
    )
    unmatched_questions: List[str] = Field(
        default_factory=list,
        description="List of questions found in the form that could not be matched"
    )
    total_questions_found: int = 0
    total_matched: int = 0
