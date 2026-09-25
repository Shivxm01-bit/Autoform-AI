"""Unit and integration tests for Google Form Automation API."""

import time
import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from models.schemas import FormQuestion, StudentProfile
from services.auth_service import auth_service
from services.google_form_service import GoogleFormService

# Test JWT secret and mock token generator
TEST_JWT_SECRET = "super-secret-test-jwt-key-1234567890"


def generate_test_jwt(user_id: str = "test-user-uuid-123", email: str = "test@example.com", expired: bool = False) -> str:
    """Helper to generate signed test JWT tokens."""
    exp = int(time.time()) - 3600 if expired else int(time.time()) + 3600
    payload = {
        "sub": user_id,
        "email": email,
        "role": "authenticated",
        "aud": "authenticated",
        "exp": exp,
    }
    return jwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")


@pytest.fixture(autouse=True)
def setup_test_auth(monkeypatch):
    """Ensure auth service uses the test secret for all tests."""
    monkeypatch.setenv("SUPABASE_JWT_SECRET", TEST_JWT_SECRET)
    auth_service.jwt_secret = TEST_JWT_SECRET


@pytest.mark.asyncio
async def test_health_check():
    """Test health check and root endpoints without authentication."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json() == {"status": "healthy"}

        res_root = await client.get("/")
        assert res_root.status_code == 200
        assert res_root.json()["service"] == "Google Forms Automation API"


def test_field_matching_logic():
    """Test the smart field matching algorithm against mock questions."""
    service = GoogleFormService()
    questions = [
        FormQuestion(entry_id="1001", title="Full Name (Legal)"),
        FormQuestion(entry_id="1002", title="Your College Email Address"),
        FormQuestion(entry_id="1003", title="Major / Field of Study"),
        FormQuestion(entry_id="1004", title="Expected Graduation Year"),
        FormQuestion(entry_id="1005", title="Student ID Number"),
        FormQuestion(entry_id="1006", title="LinkedIn Profile URL"),
        FormQuestion(
            entry_id="1007",
            title="Current Academic Standing",
            options=["Freshman", "Sophomore", "Junior", "Senior"]
        ),
    ]

    student = StudentProfile(
        full_name="Alex Mercer",
        personal_email="alex.m@stanford.edu",
        ug_specialization="Computer Science",
        ug_passing_year="2026",
        enrollment_no="STU-48291",
        linkedin_url="https://linkedin.com/in/alexmercer",
        current_year_of_study="Senior",
    )

    matched, unmatched = service.match_fields(questions, student, auto_match=True)

    assert len(matched) == 7
    assert len(unmatched) == 0

    matched_dict = {m.entry_id: (m.profile_field, m.value) for m in matched}
    assert matched_dict["1001"][1] == "Alex Mercer"
    assert matched_dict["1002"][1] == "alex.m@stanford.edu"
    assert matched_dict["1003"][1] == "Computer Science"
    assert matched_dict["1004"][1] == "2026"
    assert matched_dict["1005"][1] == "STU-48291"
    assert matched_dict["1006"][1] == "https://linkedin.com/in/alexmercer"
    assert matched_dict["1007"][1] == "Senior"


def test_crc_field_matching():
    """Test comprehensive Corporate Resource Center (CRC) field matching."""
    service = GoogleFormService()
    questions = [
        FormQuestion(entry_id="2001", title="Enrollment Number"),
        FormQuestion(entry_id="2002", title="Candidate Full Name"),
        FormQuestion(entry_id="2003", title="Date of Birth (DOB)"),
        FormQuestion(entry_id="2004", title="Gender", options=["Male", "Female", "Other"]),
        FormQuestion(entry_id="2005", title="Permanent Address"),
        FormQuestion(entry_id="2006", title="Primary Contact No"),
        FormQuestion(entry_id="2007", title="Alternate Contact Number"),
        FormQuestion(entry_id="2008", title="Personal Email ID"),
        FormQuestion(entry_id="2009", title="Institutional / College Email"),
        FormQuestion(entry_id="2010", title="Do you have a Driving License?", options=["Yes", "No"]),
        FormQuestion(entry_id="2011", title="School / Department Name"),
        FormQuestion(entry_id="2012", title="Category (UG/PG)", options=["UG", "PG"]),
        FormQuestion(entry_id="2013", title="Course / Program"),
        FormQuestion(entry_id="2014", title="UG Specialization / Branch"),
        FormQuestion(entry_id="2015", title="Current UG CGPA"),
        FormQuestion(entry_id="2016", title="UG Passing Year"),
        FormQuestion(entry_id="2017", title="Class 10th Percentage"),
        FormQuestion(entry_id="2018", title="10th School Board"),
        FormQuestion(entry_id="2019", title="Class 12th Percentage"),
        FormQuestion(entry_id="2020", title="12th Education Board"),
        FormQuestion(entry_id="2021", title="Internship Organization"),
        FormQuestion(entry_id="2022", title="Internship Project Topic"),
        FormQuestion(entry_id="2023", title="Extra Technical Certifications"),
        FormQuestion(entry_id="2024", title="Target Role Applying For", options=["Software Development Engineer (SDE)", "Data Analyst"]),
    ]

    crc_student = StudentProfile(
        enrollment_no="2021BCSE042",
        full_name="Priya Sharma",
        dob="2003-05-18",
        gender="Female",
        permanent_address="45 Park Avenue, Bangalore, Karnataka",
        contact_no="+91 9876543210",
        alt_contact_no="+91 9876543211",
        personal_email="priya.sharma@gmail.com",
        institutional_email="priya.s@university.edu.in",
        driving_license_yes_no="Yes",
        school_name="School of Computer Science & Engineering",
        category_ug_pg="UG",
        course="B.Tech",
        ug_specialization="Computer Science & Engineering",
        ug_cgpa="8.92",
        ug_passing_year="2026",
        tenth_percentage="94.2%",
        tenth_board="CBSE",
        twelfth_percentage="91.8%",
        twelfth_board="CBSE",
        internship_organization="Microsoft",
        internship_topic="Azure Cloud Telemetry and Performance Benchmarking",
        extra_certifications="AWS Certified Cloud Practitioner, Meta Front-End Developer",
        applying_for_role="Software Development Engineer (SDE)",
    )

    matched, unmatched = service.match_fields(questions, crc_student, auto_match=True)

    assert len(matched) == 24
    assert len(unmatched) == 0

    matched_dict = {m.entry_id: m.value for m in matched}
    assert matched_dict["2001"] == "2021BCSE042"
    assert matched_dict["2002"] == "Priya Sharma"
    assert matched_dict["2003"] == "2003-05-18"
    assert matched_dict["2004"] == "Female"
    assert matched_dict["2010"] == "Yes"
    assert matched_dict["2014"] == "Computer Science & Engineering"
    assert matched_dict["2015"] == "8.92"
    assert matched_dict["2021"] == "Microsoft"
    assert matched_dict["2024"] == "Software Development Engineer (SDE)"


def test_build_prefilled_url():
    """Test prefilled URL query param construction."""
    service = GoogleFormService()
    base_url = "https://docs.google.com/forms/d/e/1FAIpQLSdMockId/viewform"
    questions = [
        FormQuestion(entry_id="12345", title="Full Name"),
        FormQuestion(entry_id="67890", title="Email Address"),
    ]
    student = StudentProfile(full_name="Jane Doe", email="jane@example.com")
    matched, _ = service.match_fields(questions, student)
    prefilled_url, submit_url = service.build_prefilled_url(base_url, matched)

    assert "usp=pp_url" in prefilled_url
    assert "entry.12345=Jane+Doe" in prefilled_url or "entry.12345=Jane%20Doe" in prefilled_url
    assert "entry.67890=jane%40example.com" in prefilled_url
    assert submit_url == "https://docs.google.com/forms/d/e/1FAIpQLSdMockId/formResponse"


@pytest.mark.asyncio
async def test_generate_link_endpoint_missing_auth():
    """Test that POST /api/generate-link rejects unauthenticated requests with 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "form_url": "https://docs.google.com/forms/d/e/1FAIpQLScMockId12345/viewform",
            "student": {
                "full_name": "Test User",
                "email": "test@example.com"
            }
        }
        res = await client.post("/api/generate-link", json=payload)
        assert res.status_code == 401
        assert "Authentication required" in res.json()["detail"]


@pytest.mark.asyncio
async def test_generate_link_endpoint_invalid_token():
    """Test that POST /api/generate-link rejects invalid or expired tokens with 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "form_url": "https://docs.google.com/forms/d/e/1FAIpQLScMockId12345/viewform",
            "student": {
                "full_name": "Test User",
                "email": "test@example.com"
            }
        }
        # Invalid signature
        res = await client.post(
            "/api/generate-link",
            json=payload,
            headers={"Authorization": "Bearer invalid.jwt.token"}
        )
        assert res.status_code == 401

        # Expired token
        expired_token = generate_test_jwt(expired=True)
        res_expired = await client.post(
            "/api/generate-link",
            json=payload,
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert res_expired.status_code == 401
        assert "expired" in res_expired.json()["detail"].lower()


@pytest.mark.asyncio
async def test_generate_link_endpoint_validation_error():
    """Test that invalid form URLs return 422 Unprocessable Entity when authenticated."""
    token = generate_test_jwt()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "form_url": "https://example.com/not-a-google-form",
            "student": {
                "full_name": "Test User",
                "email": "test@example.com"
            }
        }
        res = await client.post(
            "/api/generate-link",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 422


@pytest.mark.asyncio
async def test_generate_link_endpoint_success(monkeypatch):
    """Test full POST /api/generate-link endpoint with mocked Google Form response and valid JWT."""
    mock_html = """
    <html>
      <head><title>Mock Club Registration - Google Forms</title></head>
      <body>
        <script>
          var FB_PUBLIC_LOAD_DATA_ = [
            null,
            [
              "Mock Club Registration",
              [
                [101, "Full Name", null, 0, [[11111, null, 1]]],
                [102, "Email Address", null, 0, [[22222, null, 1]]],
                [103, "Student ID", null, 0, [[33333, null, 0]]]
              ],
              null, null, null, null, null, null, "Mock Club Registration"
            ]
          ];
        </script>
      </body>
    </html>
    """

    async def mock_fetch(self, form_url: str):
        return form_url, mock_html

    monkeypatch.setattr(GoogleFormService, "fetch_form_html", mock_fetch)

    token = generate_test_jwt(user_id="usr-789", email="sarah@cyberdyne.org")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "form_url": "https://docs.google.com/forms/d/e/1FAIpQLScMockId12345/viewform",
            "student": {
                "full_name": "Sarah Connor",
                "email": "sarah@cyberdyne.org",
                "student_id": "SC-1984"
            }
        }
        res = await client.post(
            "/api/generate-link",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 200
        data = res.json()
        assert data["form_title"] == "Mock Club Registration"
        assert "entry.11111=Sarah+Connor" in data["prefilled_url"] or "entry.11111=Sarah%20Connor" in data["prefilled_url"]
        assert "entry.22222=sarah%40cyberdyne.org" in data["prefilled_url"]
        assert "entry.33333=SC-1984" in data["prefilled_url"]
        assert data["total_matched"] == 3
        assert data["total_questions_found"] == 3
