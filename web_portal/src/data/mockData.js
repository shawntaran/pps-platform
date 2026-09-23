export const USERS = {
  student: {
    id: "stu_014",
    name: "Aarav Mehta",
    email: "aarav@example.edu",
    role: "student",
    batch: "PPS4027 A",
    rollNo: "PPS-2024-4027",
    avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
    cohort: "Cohort AY 2024–25 · Week 4",
    track: "Data & Analytics Track"
  },
  trainer: {
    id: "trn_007",
    name: "Dr. Kavya Shah",
    email: "kavya@example.edu",
    role: "trainer",
    batch: "PPS4027 A",
    title: "Lead Faculty & Evaluator",
    avatar: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
    cohort: "Batch 2025 · Cohort B",
    track: "Vocational Evaluator Desk"
  },
  admin: {
    id: "adm_001",
    name: "Prof. K. V. Ramanathan",
    email: "admin@example.edu",
    role: "admin",
    batch: "All batches",
    title: "Program Administrator & Dean",
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
    cohort: "Institution Registry",
    track: "Academic Governance"
  }
};

export const INITIAL_REPORT = {
  submission_id: "sub_2026_014",
  student_name: "Aarav Mehta",
  student_id: "stu_014",
  filename: "Aarav_Mehta_Resume_v2.4.pdf",
  target_role: "Thoughtworks · Graduate Data Analyst",
  status: "Complete",
  analysed_on: "19 Sep 2026, 11:20 AM",
  ats_score: 76,
  grade: "B+ (Distinction Track)",
  parseability: {
    score: 88,
    summary: "Single-column layout parsed cleanly. Text layer extractable with zero unicode errors.",
    details: [
      "Standard UTF-8 character encoding verified",
      "Heading hierarchy (H1 -> H2 -> H3) recognized by parsers",
      "No non-standard text boxes or embedded tables detected"
    ]
  },
  keyword_match: {
    score: 72,
    summary: "Solid alignment with Graduate Data Analyst competencies; add 3 missing core terms.",
    details: [
      "Strong density on Python, SQL, and Power BI",
      "Missing critical keywords: Data Modelling, Statistics, ETL Pipelines",
      "Add quantifiable action verbs to experience bullet points"
    ]
  },
  section_structure: {
    score: 68,
    summary: "Most expected sections found; clarify Certifications and Leadership headings.",
    details: [
      "Education, Skills, Experience, and Projects clearly isolated",
      "Missing dedicated 'Certifications' section header",
      "Contact information should remain in body header, not in footer margin"
    ]
  },
  detected_sections: [
    "Contact Information",
    "Professional Summary",
    "Education",
    "Technical Skills",
    "Projects & Practicums",
    "Internship Experience",
  ],
  skills: [
    "Python",
    "SQL",
    "Power BI",
    "Excel",
    "Communication",
    "Data Cleaning",
    "Git",
    "Pandas"
  ],
  matched_skills: [
    "Python",
    "SQL",
    "Power BI",
    "Excel",
    "Data Cleaning"
  ],
  missing_skills: [
    "Data Modelling",
    "Inferential Statistics",
    "ETL Pipelines",
    "Cloud Basics (AWS/GCP)"
  ],
  formatting_issues: [
    "Two distinct font sizes detected in body description bullets",
    "Contact icons used without accompanying plain-text labels"
  ],
  recommendations: [
    "Use a pure single-column ATS-safe format without multi-column margins",
    "Add a dedicated 'Certifications & Accreditations' section heading",
    "Mention at least one end-to-end ETL pipeline project with metrics in summary",
    "Quantify project achievements with percentages or turnaround improvements"
  ],
  trainer_feedback: "Good structural foundation, Aarav. Enhance the analytics metrics in your project descriptions and add the missing data modelling competencies before CA1 locks."
};

export const INITIAL_SUBMISSIONS = [
  {
    id: "sub_2026_014",
    student: "Aarav Mehta",
    student_id: "stu_014",
    rollNo: "PPS-2024-4027",
    filename: "Aarav_Mehta_Resume_v2.4.pdf",
    target_role: "Thoughtworks · Graduate Data Analyst",
    assessment: "CA1",
    submitted_date: "19 Sep 2026, 11:20 AM",
    status: "Complete",
    ats_score: 76,
    review_status: "Needs review",
    trainer_notes: "Draft ready for final sign-off.",
    batch: "PPS4027 A"
  },
  {
    id: "sub_2026_015",
    student: "Nisha Rao",
    student_id: "stu_015",
    rollNo: "PPS-2024-4028",
    filename: "Nisha_Rao_CV_Tech.pdf",
    target_role: "TCS · Associate Software Engineer",
    assessment: "CA1",
    submitted_date: "19 Sep 2026, 10:15 AM",
    status: "Processing",
    ats_score: 82,
    review_status: "Waiting",
    trainer_notes: "Awaiting automated parsing worker.",
    batch: "PPS4027 A"
  },
  {
    id: "sub_2026_016",
    student: "Sana Ali",
    student_id: "stu_016",
    rollNo: "PPS-2024-4029",
    filename: "Sana_Ali_Product_Resume.pdf",
    target_role: "Deloitte · Business Tech Analyst",
    assessment: "CA1",
    submitted_date: "18 Sep 2026, 04:45 PM",
    status: "Submitted",
    ats_score: 69,
    review_status: "Waiting",
    trainer_notes: "Initial submission received.",
    batch: "PPS4027 A"
  },
  {
    id: "sub_2026_017",
    student: "Devansh Roy",
    student_id: "stu_017",
    rollNo: "PPS-2024-4030",
    filename: "Devansh_Roy_Frontend_2026.pdf",
    target_role: "Thoughtworks · UI/UX Engineer",
    assessment: "CA1",
    submitted_date: "18 Sep 2026, 02:10 PM",
    status: "Complete",
    ats_score: 88,
    review_status: "Graded",
    trainer_notes: "Excellent typography and ATS layout.",
    batch: "PPS4027 A"
  },
  {
    id: "sub_2026_018",
    student: "Pooja Verma",
    student_id: "stu_018",
    rollNo: "PPS-2024-4031",
    filename: "Pooja_Verma_Analyst.pdf",
    target_role: "KPMG · Risk Analyst",
    assessment: "CA1",
    submitted_date: "17 Sep 2026, 06:30 PM",
    status: "Complete",
    ats_score: 91,
    review_status: "Graded",
    trainer_notes: "Benchmark standard resume.",
    batch: "PPS4027 A"
  }
];

export const ASSIGNMENTS = [
  {
    assessment: "CA1",
    title: "Resume Review & ATS Verification",
    due: "24 Sep 2026",
    status: "Complete",
    score: "76 / 100",
    weight: "30%",
    description: "Single-column ATS format, section structure, and target JD keyword alignment."
  },
  {
    assessment: "CA2",
    title: "Group Discussion & Problem Solving",
    due: "16 Oct 2026",
    status: "Not open",
    score: "-",
    weight: "30%",
    description: "Evaluation on business case structuring, team argumentation, and leadership."
  },
  {
    assessment: "CA3",
    title: "Technical Mock Viva & HR Interview",
    due: "30 Oct 2026",
    status: "Not open",
    score: "-",
    weight: "40%",
    description: "1-on-1 viva with external industry evaluators on projects and core competencies."
  }
];

export const CONTENT_LIBRARY = [
  {
    week: "Week 1",
    module: "Resume Building",
    title: "ATS-Ready Resume Basics & Single-Column Standard",
    type: "Reading + Worksheet",
    duration: "45 min",
    released: true,
  },
  {
    week: "Week 2",
    module: "Resume Building",
    title: "Tailoring Resume to Job Descriptions & Keyword Matching",
    type: "Video + Practice",
    duration: "1 hr 15 min",
    released: true,
  },
  {
    week: "Week 3",
    module: "Resume Building",
    title: "Writing Impact-Focused Projects & STAR Framework",
    type: "Reading Guide",
    duration: "30 min",
    released: true,
  },
  {
    week: "Week 4",
    module: "Group Discussion",
    title: "Structuring Business Arguments & Constructive Rebuttal",
    type: "Masterclass Video",
    duration: "50 min",
    released: false,
  }
];

export const CALENDAR_EVENTS = [
  {
    date: "22 Sep",
    day: "Tue",
    time: "10:00 AM",
    event: "Tuesday Content Drop · Module 1 Advanced",
    location: "Content Library",
    type: "curriculum"
  },
  {
    date: "23 Sep",
    day: "Wed",
    time: "04:00 PM",
    event: "Live Q&A with Placement Faculty",
    location: "MS Teams Room 4",
    type: "live"
  },
  {
    date: "24 Sep",
    day: "Thu",
    time: "11:59 PM",
    event: "CA1 Resume Review Hard Deadline",
    location: "Submission Desk",
    type: "deadline"
  },
  {
    date: "25 Sep",
    day: "Fri",
    time: "02:00 PM",
    event: "Weekly MCQ 4 Assessment",
    location: "MS Forms Portal",
    type: "quiz"
  }
];

export const AUDIT_EVENTS = [
  {
    time: "19 Sep, 11:20",
    event: "ATS diagnostic report generated & viewed",
    actor: "Aarav Mehta (stu_014)",
    result: "Allowed",
    ip: "10.40.75.226",
    category: "Assessment"
  },
  {
    time: "19 Sep, 11:18",
    event: "Resume analysis pipeline worker executed",
    actor: "System Engine v4.2",
    result: "Success",
    ip: "Internal Cluster",
    category: "Ingestion"
  },
  {
    time: "19 Sep, 10:55",
    event: "Privacy consent agreement digitally recorded",
    actor: "Aarav Mehta (stu_014)",
    result: "Success",
    ip: "10.40.75.226",
    category: "Compliance"
  },
  {
    time: "19 Sep, 09:12",
    event: "Trainer bulk review status updated (Cohort B)",
    actor: "Dr. Kavya Shah (trn_007)",
    result: "Success",
    ip: "10.40.88.114",
    category: "Grading"
  },
  {
    time: "18 Sep, 16:40",
    event: "CA1 deadline policy synchronized",
    actor: "Prof. K. V. Ramanathan (adm_001)",
    result: "Success",
    ip: "10.40.12.001",
    category: "Policy"
  }
];

export const SYSTEM_CONFIG = {
  max_upload_mb: 5,
  retention_days: 180,
  ats_weights: {
    parseability: 40,
    keyword_match: 40,
    section_structure: 20
  },
  last_updated: "2026-09-19",
  engine_version: "v4.2.8-production",
  ferpa_compliant: true,
  iso_certified: true
};
