"""Standalone test script to execute live Google Form scraping, entry_id extraction, and Gemini field mapping directly."""

import asyncio
import json
import os
import sys
from typing import Optional

from dotenv import load_dotenv

# Load environment variables (e.g. GEMINI_API_KEY)
load_dotenv()

from models.schemas import FormQuestion, StudentProfile
from services.gemini_mapper import GeminiFormMapper
from services.google_form_service import GoogleFormService

# ==============================================================================
# CONFIGURATION: Paste your Google Form URL below or pass it via CLI argument
# Example: python -m run_live_test https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform
# ==============================================================================
DEFAULT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScMockTestFormId_12345/viewform"

# Hardcoded Google Form URL (Replace with your live form URL)
TARGET_FORM_URL = os.getenv("GOOGLE_FORM_URL", DEFAULT_FORM_URL)

# Dummy student profile JSON payload
DUMMY_STUDENT_PROFILE = {
    "first_name": "Alexander",
    "last_name": "Wright",
    "full_name": "Alexander Wright",
    "email": "alex.wright@university.edu",
    "phone": "+1 (555) 234-5678",
    "student_id": "STU-2026-8891",
    "university": "Massachusetts Institute of Technology",
    "major": "Computer Science & Engineering",
    "degree": "Bachelor of Science",
    "graduation_year": "2026",
    "current_year_of_study": "Senior",
    "gpa": "3.95",
    "city": "Cambridge",
    "state": "MA",
    "zip_code": "02139",
    "country": "United States",
    "linkedin_url": "https://linkedin.com/in/alexander-wright",
    "github_url": "https://github.com/alexwright-dev",
    "portfolio_url": "https://alexwright.dev",
    "bio": "Passionate software engineer specializing in backend systems and AI automation.",
    "custom_fields": {
        "tshirt_size": "Large",
        "dietary_preferences": "None",
        "emergency_contact": "+1 (555) 987-6543"
    }
}


# Sample fallback HTML simulating a live Google Form if offline or using placeholder URL
SAMPLE_MOCK_FORM_HTML = """
<html>
  <head><title>Spring 2026 Student Innovation Fellowship Application - Google Forms</title></head>
  <body>
    <script>
      var FB_PUBLIC_LOAD_DATA_ = [
        null,
        [
          "Spring 2026 Student Innovation Fellowship Application",
          [
            [1001, "Applicant Full Name", "Please enter your full legal name", 0, [[184729104, null, 1]]],
            [1002, "University Email Address", null, 0, [[739104821, null, 1]]],
            [1003, "Contact Phone Number", null, 0, [[392019482, null, 0]]],
            [1004, "Student ID Number", null, 0, [[948102941, null, 1]]],
            [1005, "University / Institution Name", null, 0, [[629104820, null, 1]]],
            [1006, "Major / Field of Study", null, 0, [[481029471, null, 1]]],
            [1007, "Expected Year of Graduation", null, 0, [[510294819, null, 0]]],
            [1008, "Current Academic Standing", null, 2, [[829104719, [["Freshman"], ["Sophomore"], ["Junior"], ["Senior"], ["Graduate"]], 1]]],
            [1009, "Cumulative GPA", null, 0, [[194820194, null, 0]]],
            [1010, "LinkedIn Profile URL", null, 0, [[491820471, null, 0]]],
            [1011, "GitHub Profile Link", null, 0, [[710294810, null, 0]]],
            [1012, "T-Shirt Size", null, 3, [[301948201, [["Small"], ["Medium"], ["Large"], ["XL"]], 0]]]
          ],
          null, null, null, null, null, null, "Spring 2026 Student Innovation Fellowship Application"
        ]
      ];
    </script>
  </body>
</html>
"""


async def run_live_test(form_url: str):
    """
    Directly tests core Google Form scraping, entry_id extraction,
    and Gemini mapping functions.
    """
    print("=" * 80)
    print("🎯 GOOGLE FORMS AUTOMATION - LIVE TEST HARNESS")
    print("=" * 80)
    print(f"📌 Target Form URL: {form_url}\n")

    # 1. Initialize services
    form_service = GoogleFormService()
    gemini_mapper = GeminiFormMapper()
    student_profile = StudentProfile(**DUMMY_STUDENT_PROFILE)

    print("👤 Loaded Student Profile:")
    print(json.dumps(DUMMY_STUDENT_PROFILE, indent=2))
    print("\n" + "-" * 80)

    # 2. Scrape the URL
    print("\n🌐 Step 1: Scraping Google Form HTML...")
    final_url = form_url
    html_content = ""
    is_live_fetch = False

    try:
        final_url, html_content = await form_service.fetch_form_html(form_url)
        is_live_fetch = True
        print(f"✅ Successfully fetched live form from: {final_url} ({len(html_content):,} bytes)")
    except Exception as exc:
        print(f"⚠️  Live fetch note: {exc}")
        print("ℹ️  Using form schema parser with test data to verify extraction & mapping pipeline...")
        html_content = SAMPLE_MOCK_FORM_HTML
        final_url = form_url

    # 3. Extract entry_ids and questions
    print("\n📋 Step 2: Extracting Entry IDs and Form Questions from HTML...")
    form_title, questions = form_service.parse_form_questions(html_content)

    print(f"🏷️  Form Title: {form_title or 'Untitled Form'}")
    print(f"🔢 Total Questions Found: {len(questions)}\n")

    print("--- Raw Extracted Questions ---")
    for idx, q in enumerate(questions, start=1):
        req_flag = " (Required)" if q.required else ""
        opts_str = f" | Options: {q.options}" if q.options else ""
        print(f" [{idx:02d}] entry.{q.entry_id:<12} | Title: \"{q.title}\"{req_flag}{opts_str}")

    if not questions:
        print("❌ No form fields were extracted. Please check the form URL.")
        return

    # 4. Pass to Gemini Mapper
    print("\n" + "-" * 80)
    print("🧠 Step 3: Passing Extracted Questions to Gemini Mapper...")
    matched_fields, unmatched_questions = await gemini_mapper.map_fields(
        questions=questions,
        student=student_profile,
    )

    print(f"✅ Successfully matched {len(matched_fields)} of {len(questions)} questions.\n")
    print("--- Matched Fields Mapping ---")
    for m in matched_fields:
        print(f" • entry.{m.entry_id:<12} -> [{m.profile_field:<22}] = \"{m.value}\" (Question: \"{m.question_title}\")")

    if unmatched_questions:
        print("\n--- Unmatched Questions ---")
        for u in unmatched_questions:
            print(f" ⚠️  \"{u}\"")

    # 5. Build and print final pre-filled URL
    print("\n" + "-" * 80)
    print("🔗 Step 4: Constructing Final Pre-filled Google Form URL...")
    prefilled_url, submit_url = form_service.build_prefilled_url(final_url, matched_fields)

    print("\n================================================================================")
    print("🚀 FINAL PRE-FILLED URL:")
    print("================================================================================")
    print(prefilled_url)
    print("\n📮 Direct Submission Endpoint (/formResponse):")
    print(submit_url)
    print("================================================================================\n")


def main():
    """CLI entrypoint."""
    # Allow passing form URL as command-line argument: python -m run_live_test <URL>
    target_url = sys.argv[1] if len(sys.argv) > 1 else TARGET_FORM_URL
    asyncio.run(run_live_test(target_url))


if __name__ == "__main__":
    main()
