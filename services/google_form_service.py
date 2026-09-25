"""Business logic service for fetching, parsing, and autofilling Google Forms."""

import json
import logging
import re
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple

import httpx

from models.schemas import (
    FormQuestion,
    GenerateLinkRequest,
    GenerateLinkResponse,
    MatchedField,
    StudentProfile,
)

logger = logging.getLogger("google_form_service")

# Common keyword mapping for matching question titles to StudentProfile attributes
FIELD_KEYWORD_MAP: Dict[str, List[str]] = {
    # CRC: Personal & Contact
    "enrollment_no": [
        "enrollment no", "enrollment number", "enrolment no", "enrolment number", "enrollment",
        "roll no", "roll number", "university roll number", "registration no", "registration number",
        "student id", "student roll no", "matriculation no", "univ id"
    ],
    "full_name": [
        "full name", "your name", "student name", "candidate name", "applicant name",
        "name of the student", "complete name", "legal name", "name (full)", "name"
    ],
    "dob": [
        "date of birth", "dob", "birth date", "birthday", "d.o.b", "d.o.b."
    ],
    "gender": [
        "gender", "sex"
    ],
    "home_location": [
        "home location", "hometown", "native location", "native place", "current location",
        "current city", "domicile", "home town", "city of residence"
    ],
    "permanent_address": [
        "permanent address", "residential address", "home address", "address for communication",
        "postal address", "street address", "current address", "address"
    ],
    "contact_no": [
        "contact no", "contact number", "mobile no", "mobile number", "phone number",
        "primary contact", "whatsapp number", "phone", "mobile", "cell"
    ],
    "alt_contact_no": [
        "alt contact no", "alt contact", "alternate contact no", "alternate contact",
        "alternate mobile", "secondary contact", "alternate number", "guardian contact",
        "parent contact", "emergency contact", "alternate phone"
    ],
    "personal_email": [
        "personal email", "personal email id", "personal e-mail", "personal mail",
        "alternate email", "gmail id", "email id", "email address", "email", "e-mail"
    ],
    "institutional_email": [
        "institutional email", "institutional email id", "college email", "university email",
        "official email", "school email", "institute email", "edu email", "college email id",
        "official college email"
    ],
    "driving_license_yes_no": [
        "driving license", "driving licence", "do you have a driving license",
        "do you have a driving licence", "driving license (yes/no)", "driving licence (yes/no)",
        "dl status", "two wheeler license", "four wheeler license", "valid driving license"
    ],

    # CRC: Academics
    "school_name": [
        "school name", "name of school", "college name", "school/department",
        "school / institute", "department name", "faculty name", "school"
    ],
    "category_ug_pg": [
        "category (ug/pg)", "category ug/pg", "ug/pg", "ug or pg", "program level",
        "course level", "category", "degree level", "qualification level"
    ],
    "course": [
        "course", "degree", "program", "program name", "course name", "degree program"
    ],
    "ug_specialization": [
        "ug specialization", "ug branch", "ug stream", "undergraduate branch",
        "undergraduate specialization", "b.tech branch", "btech branch", "specialization",
        "branch", "stream", "major", "discipline", "field of study"
    ],
    "ug_cgpa": [
        "ug cgpa", "b.tech cgpa", "btech cgpa", "graduation cgpa", "bachelor cgpa",
        "ug gpa", "cgpa (ug)", "current cgpa", "overall cgpa", "cgpa", "gpa", "aggregate cgpa"
    ],
    "ug_passing_year": [
        "ug passing year", "year of graduation (ug)", "graduation passing year",
        "b.tech passing year", "btech passing year", "passing year (ug)", "ug batch",
        "year of passing (ug)", "graduation year", "year of graduation", "expected graduation", "batch"
    ],
    "pg_specialization": [
        "pg specialization", "pg branch", "pg stream", "postgraduate specialization",
        "masters specialization", "m.tech branch", "mtech branch", "specialization (pg)"
    ],
    "pg_cgpa": [
        "pg cgpa", "postgraduate cgpa", "masters cgpa", "m.tech cgpa", "mtech cgpa",
        "cgpa (pg)", "pg gpa"
    ],
    "pg_passing_year": [
        "pg passing year", "postgraduate passing year", "masters passing year",
        "m.tech passing year", "mtech passing year", "year of graduation (pg)", "passing year (pg)"
    ],
    "tenth_percentage": [
        "10th percentage", "tenth percentage", "10th %", "class 10 percentage",
        "class x percentage", "10th marks", "ssc percentage", "matric percentage",
        "10th cgpa/percentage", "10th aggregate", "x percentage", "class 10 aggregate"
    ],
    "tenth_board": [
        "10th board", "tenth board", "10th education board", "tenth education board",
        "class 10 board", "class x board", "class 10th board", "10th class board",
        "ssc board", "matric board", "10th school board", "x board", "board (10th)", "10th standard board"
    ],
    "tenth_passing_year": [
        "10th passing year", "tenth passing year", "class 10 passing year", "class 10th passing year",
        "class x passing year", "year of passing 10th", "10th year of passing", "x passing year", "passing year (10th)"
    ],
    "twelfth_percentage": [
        "12th percentage", "twelfth percentage", "12th %", "class 12 percentage", "class 12th percentage",
        "class xii percentage", "12th marks", "hsc percentage", "intermediate percentage",
        "12th/diploma percentage", "12th aggregate", "xii percentage", "class 12 aggregate"
    ],
    "twelfth_board": [
        "12th board", "twelfth board", "12th education board", "twelfth education board",
        "class 12 board", "class xii board", "class 12th board", "12th class board",
        "hsc board", "intermediate board", "12th/diploma board", "xii board", "board (12th)", "12th standard board"
    ],
    "twelfth_passing_year": [
        "12th passing year", "twelfth passing year", "class 12 passing year", "class 12th passing year",
        "class xii passing year", "year of passing 12th", "12th year of passing", "xii passing year", "passing year (12th)"
    ],

    # CRC: Professional
    "internship_organization": [
        "internship organization", "internship company", "company name (internship)",
        "internship done at", "summer internship company", "internship employer",
        "internship firm", "organization name (internship)", "internship details (company)"
    ],
    "internship_topic": [
        "internship topic", "internship project", "project title", "internship domain",
        "project domain", "internship description", "internship project title", "title of internship"
    ],
    "extra_certifications": [
        "extra certifications", "certifications", "courses & certifications",
        "technical certifications", "certificates", "online courses completed",
        "additional certifications", "skill certifications", "licenses & certifications"
    ],
    "applying_for_role": [
        "applying for role", "role applied for", "job profile", "position applied for",
        "preferred role", "designation", "domain applying for", "profile interested in",
        "target role", "role preference", "applied position"
    ],

    # Legacy / Generic aliases
    "email": ["email", "e-mail", "email address", "e-mail address", "contact email"],
    "phone": ["phone", "mobile", "phone number", "contact number", "cell", "telephone"],
    "student_id": ["student id", "roll no", "roll number", "registration no", "registration number", "id number"],
    "university": ["university", "college", "school", "institution", "institute name", "campus"],
    "major": ["major", "branch", "stream", "field of study", "department", "discipline", "specialization"],
    "degree": ["degree", "program", "course (degree)", "qualification"],
    "graduation_year": ["graduation year", "year of graduation", "passing year", "batch", "class of", "expected graduation"],
    "current_year_of_study": ["year of study", "current year", "academic year", "current semester", "academic standing", "class standing", "standing", "level of study", "year"],
    "gpa": ["gpa", "cgpa", "grade point", "cumulative gpa", "overall score"],
    "date_of_birth": ["date of birth", "dob", "birth date", "birthday"],
    "address": ["address", "residential address", "street address", "permanent address", "current address"],

    # Online / Social Presence
    "linkedin_url": ["linkedin", "linkedin url", "linkedin profile", "linkedin link"],
    "github_url": ["github", "github url", "github profile", "github link"],
    "portfolio_url": ["portfolio", "personal website", "portfolio url", "website url", "personal site"],
    "resume_url": ["resume", "cv", "resume link", "resume url", "cv link", "curriculum vitae"],
    "tech_stack": ["tech stack", "skills", "technical skills", "technologies", "programming languages", "frameworks", "tools", "stack"],
    "bio": ["bio", "about you", "tell us about yourself", "brief introduction", "statement of purpose", "introduction", "cover letter"],
}


class GoogleFormService:
    """Service to interact with, parse, and generate pre-filled links for Google Forms."""

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def fetch_form_html(self, form_url: str) -> Tuple[str, str]:
        """Fetch the Google Form HTML and return final redirected URL and HTML content."""
        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers=self.headers
        ) as client:
            try:
                response = await client.get(form_url)
                response.raise_for_status()
                return str(response.url), response.text
            except httpx.HTTPError as exc:
                logger.error(f"Error fetching Google Form at {form_url}: {exc}")
                raise ValueError(f"Failed to fetch Google Form: {str(exc)}") from exc

    def parse_form_questions(self, html_content: str) -> Tuple[Optional[str], List[FormQuestion]]:
        """
        Extract form title and list of question fields with their entry IDs from the Google Form HTML.
        Google Forms stores metadata inside FB_PUBLIC_LOAD_DATA_ Javascript variable.
        """
        form_title = None
        questions: List[FormQuestion] = []

        # 1. Primary Strategy: Extract FB_PUBLIC_LOAD_DATA_
        # var FB_PUBLIC_LOAD_DATA_ = [...];
        match = re.search(r"FB_PUBLIC_LOAD_DATA_\s*=\s*(\[.+?\]);\s*</script>", html_content, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                # Title is at data[1][8] or data[1][0]
                if len(data) > 1 and data[1]:
                    if len(data[1]) > 8 and data[1][8]:
                        form_title = str(data[1][8])
                    elif len(data[1]) > 0 and data[1][0]:
                        form_title = str(data[1][0])

                    # Form items are at data[1][1]
                    raw_items = data[1][1] if len(data[1]) > 1 and isinstance(data[1][1], list) else []
                    for item in raw_items:
                        if not isinstance(item, list) or len(item) < 2:
                            continue

                        item_id = item[0] if len(item) > 0 else None
                        title = item[1] if len(item) > 1 and item[1] else ""
                        description = item[2] if len(item) > 2 else None
                        q_type = item[3] if len(item) > 3 else None

                        # Entry details are nested in item[4]
                        if len(item) > 4 and isinstance(item[4], list) and len(item[4]) > 0:
                            for entry_data in item[4]:
                                if isinstance(entry_data, list) and len(entry_data) > 0:
                                    entry_id = str(entry_data[0])
                                    options: List[str] = []
                                    if len(entry_data) > 1 and isinstance(entry_data[1], list):
                                        for opt in entry_data[1]:
                                            if isinstance(opt, list) and len(opt) > 0 and opt[0]:
                                                options.append(str(opt[0]))

                                    required = bool(entry_data[2]) if len(entry_data) > 2 else False

                                    questions.append(
                                        FormQuestion(
                                            item_id=item_id,
                                            entry_id=entry_id,
                                            title=str(title).strip(),
                                            description=str(description) if description else None,
                                            question_type=q_type,
                                            options=options,
                                            required=required,
                                        )
                                    )
            except Exception as e:
                logger.warning(f"Failed parsing FB_PUBLIC_LOAD_DATA_: {e}")

        # 2. Fallback Strategy: Scan for HTML input entry.XXXX or data-params
        if not questions:
            # Look for inputs like name="entry.123456789"
            entries = re.findall(r'name=["\']entry\.(\d+)["\']', html_content)
            for entry_id in set(entries):
                questions.append(
                    FormQuestion(
                        entry_id=entry_id,
                        title=f"Question {entry_id}",
                    )
                )

        # Fallback for form title
        if not form_title:
            title_match = re.search(r"<title>(.*?)</title>", html_content, re.IGNORECASE)
            if title_match:
                form_title = title_match.group(1).replace("- Google Forms", "").strip()

        return form_title, questions

    def match_fields(
        self,
        questions: List[FormQuestion],
        student: StudentProfile,
        custom_mapping: Optional[Dict[str, str]] = None,
        auto_match: bool = True,
    ) -> Tuple[List[MatchedField], List[str]]:
        """
        Match student profile fields with form question entry IDs.
        Supports:
        - Exact custom mapping (e.g. entry.12345 -> 'email' or 'Full Name' -> 'full_name')
        - Semantic/keyword matching on normalized question titles
        - Option matching for multiple-choice/dropdown fields
        """
        flattened_student = student.to_flattened_dict()
        matched: List[MatchedField] = []
        unmatched: List[str] = []
        used_entries = set()

        # Step 1: Apply custom mapping if provided
        if custom_mapping:
            for question in questions:
                # Check if entry_id or full entry.ID is in custom_mapping
                map_target = None
                if question.entry_id in custom_mapping:
                    map_target = custom_mapping[question.entry_id]
                elif f"entry.{question.entry_id}" in custom_mapping:
                    map_target = custom_mapping[f"entry.{question.entry_id}"]
                elif question.title in custom_mapping:
                    map_target = custom_mapping[question.title]

                if map_target and map_target in flattened_student:
                    val = flattened_student[map_target]
                    matched.append(
                        MatchedField(
                            entry_id=question.entry_id,
                            question_title=question.title,
                            profile_field=map_target,
                            value=val,
                        )
                    )
                    used_entries.add(question.entry_id)

        # Step 2: Auto-matching logic
        if auto_match:
            for question in questions:
                if question.entry_id in used_entries:
                    continue

                clean_title = self._normalize_text(question.title)
                matched_field_name: Optional[str] = None
                matched_value: Optional[str] = None

                # Direct match with custom fields first
                if student.custom_fields:
                    for cf_key, cf_val in student.custom_fields.items():
                        clean_cf_key = self._normalize_text(cf_key)
                        if clean_cf_key in clean_title or clean_title in clean_cf_key:
                            matched_field_name = cf_key
                            matched_value = str(cf_val)
                            break

                # Keyword-based matching across standard student profile fields
                if not matched_field_name:
                    best_match = None
                    best_score = 0

                    for profile_key, keywords in FIELD_KEYWORD_MAP.items():
                        if profile_key not in flattened_student:
                            continue

                        # Check each keyword
                        for kw in keywords:
                            # Prioritize exact/word-boundary match
                            pattern = r"\b" + re.escape(kw) + r"\b"
                            if re.search(pattern, clean_title):
                                score = len(kw) + 10
                                if score > best_score:
                                    best_score = score
                                    best_match = profile_key
                            elif kw in clean_title:
                                score = len(kw)
                                if score > best_score:
                                    best_score = score
                                    best_match = profile_key

                    if best_match:
                        matched_field_name = best_match
                        raw_val = flattened_student[best_match]

                        # Check if this question has limited options (multiple choice / dropdown)
                        if question.options:
                            matched_value = self._find_best_option(raw_val, question.options)
                        else:
                            matched_value = raw_val

                # Heuristic 3: If still no match and question has options, check if any student field matches an option
                if not matched_field_name and question.options:
                    for profile_key, profile_val in flattened_student.items():
                        if not profile_val:
                            continue
                        clean_prof_val = profile_val.strip().lower()
                        for opt in question.options:
                            if opt.strip().lower() == clean_prof_val:
                                matched_field_name = profile_key
                                matched_value = opt
                                break
                        if matched_field_name:
                            break

                if matched_field_name and matched_value:
                    matched.append(
                        MatchedField(
                            entry_id=question.entry_id,
                            question_title=question.title,
                            profile_field=matched_field_name,
                            value=matched_value,
                        )
                    )
                    used_entries.add(question.entry_id)
                else:
                    unmatched.append(question.title or f"Entry {question.entry_id}")
        else:
            # If auto-match is off, record all remaining as unmatched
            for question in questions:
                if question.entry_id not in used_entries:
                    unmatched.append(question.title or f"Entry {question.entry_id}")

        return matched, unmatched

    def build_prefilled_url(self, base_form_url: str, matched_fields: List[MatchedField]) -> Tuple[str, str]:
        """
        Build the Google Forms prefilled link (viewform with usp=pp_url)
        and the direct formResponse URL.
        """
        # Normalize URL to viewform
        clean_url = base_form_url.split("?")[0]
        if clean_url.endswith("/formResponse"):
            clean_url = clean_url.replace("/formResponse", "/viewform")
        elif not clean_url.endswith("/viewform") and not clean_url.endswith("/"):
            clean_url = clean_url + "/viewform"
        elif clean_url.endswith("/"):
            clean_url = clean_url + "viewform"

        # Build query parameters
        params: Dict[str, str] = {"usp": "pp_url"}
        for match in matched_fields:
            param_name = f"entry.{match.entry_id}"
            params[param_name] = match.value

        query_string = urllib.parse.urlencode(params, doseq=True)
        prefilled_url = f"{clean_url}?{query_string}"

        submit_url = clean_url.replace("/viewform", "/formResponse")

        return prefilled_url, submit_url

    async def generate_prefilled_link(self, request: GenerateLinkRequest) -> GenerateLinkResponse:
        """Complete workflow: Fetch -> Parse -> Match -> Generate Link."""
        # 1. Fetch
        final_url, html_content = await self.fetch_form_html(request.form_url)

        # 2. Parse
        form_title, questions = self.parse_form_questions(html_content)

        if not questions:
            logger.warning(f"No questions/entries found for URL: {request.form_url}")

        # 3. Match
        matched_fields, unmatched = self.match_fields(
            questions=questions,
            student=request.student,
            custom_mapping=request.custom_mapping,
            auto_match=request.auto_match,
        )

        # 4. Build URLs
        prefilled_url, submit_url = self.build_prefilled_url(final_url, matched_fields)

        return GenerateLinkResponse(
            form_title=form_title,
            original_url=request.form_url,
            prefilled_url=prefilled_url,
            submit_url=submit_url,
            matched_fields=matched_fields,
            unmatched_questions=unmatched,
            total_questions_found=len(questions),
            total_matched=len(matched_fields),
        )

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text for relaxed case-insensitive matching."""
        if not text:
            return ""
        # Lowercase, replace punctuation with spaces
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _find_best_option(value: str, options: List[str]) -> str:
        """Find the matching option in multiple-choice questions."""
        clean_val = value.strip().lower()
        for opt in options:
            if opt.strip().lower() == clean_val:
                return opt
        # Substring / partial match
        for opt in options:
            if clean_val in opt.strip().lower() or opt.strip().lower() in clean_val:
                return opt
        # Fallback to the original value
        return value
