
import io
import json

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def _as_text(value):
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def create_pdf_report(profile, plan):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []

    title = "Student Career Guidance Plan"
    content.append(Paragraph(title, styles["Title"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph("<b>Student profile</b>", styles["Heading2"]))
    for key, value in profile.items():
        content.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {_as_text(value)}", styles["BodyText"]))

    content.append(Spacer(1, 12))
    content.append(Paragraph("<b>Profile summary</b>", styles["Heading2"]))
    content.append(Paragraph(plan.get("profile_summary", ""), styles["BodyText"]))

    content.append(Spacer(1, 12))
    content.append(Paragraph("<b>Recommended career paths</b>", styles["Heading2"]))
    for role in plan.get("career_paths", []):
        content.append(Paragraph(f"<b>{role.get('role', 'Career role')}</b>", styles["Heading3"]))
        content.append(Paragraph(f"<b>Why it fits:</b> {role.get('why_it_fits', '')}", styles["BodyText"]))
        content.append(Paragraph("<b>Responsibilities:</b>", styles["BodyText"]))
        for item in role.get("responsibilities", []):
            content.append(Paragraph(f"- {item}", styles["BodyText"]))
        content.append(Paragraph(f"<b>Required skills:</b> {_as_text(role.get('required_skills', []))}", styles["BodyText"]))
        content.append(Paragraph(f"<b>Qualifications:</b> {role.get('qualification', '')}", styles["BodyText"]))
        certs = role.get("certifications", [])
        if certs:
            content.append(Paragraph(f"<b>Certifications:</b> {_as_text(certs)}", styles["BodyText"]))
        content.append(Spacer(1, 8))

    content.append(Spacer(1, 12))
    gaps = plan.get("skill_gap", {})
    content.append(Paragraph("<b>Skill-gap analysis</b>", styles["Heading2"]))
    content.append(Paragraph(f"<b>Existing skills:</b> {_as_text(gaps.get('existing_skills', []))}", styles["BodyText"]))
    content.append(Paragraph(f"<b>Skills to develop:</b> {_as_text(gaps.get('missing_skills', []))}", styles["BodyText"]))
    for item in gaps.get("actions", []):
        content.append(Paragraph(f"- {item}", styles["BodyText"]))

    content.append(Spacer(1, 12))
    content.append(Paragraph("<b>Learning roadmap</b>", styles["Heading2"]))
    for stage in plan.get("roadmap", []):
        content.append(Paragraph(f"<b>{stage.get('stage', '')}</b>", styles["Heading3"]))
        content.append(Paragraph(f"<b>Goal:</b> {stage.get('goal', '')}", styles["BodyText"]))
        content.append(Paragraph(f"<b>Topics:</b> {_as_text(stage.get('topics', []))}", styles["BodyText"]))
        for item in stage.get("activities", []):
            content.append(Paragraph(f"- {item}", styles["BodyText"]))
        content.append(Paragraph(f"<b>Project:</b> {stage.get('project', '')}", styles["BodyText"]))
        content.append(Spacer(1, 8))

    content.append(Spacer(1, 12))
    content.append(Paragraph("<b>Learning resources</b>", styles["Heading2"]))
    for resource in plan.get("learning_resources", []):
        content.append(Paragraph(f"- {resource.get('name', '')}: {resource.get('url', '')} — {resource.get('purpose', '')}", styles["BodyText"]))

    content.append(Spacer(1, 12))
    content.append(Paragraph("<b>Job-search resources</b>", styles["Heading2"]))
    for resource in plan.get("job_search_resources", []):
        content.append(Paragraph(f"- {resource.get('name', '')}: {resource.get('url', '')} — {resource.get('purpose', '')}", styles["BodyText"]))

    content.append(Spacer(1, 12))
    content.append(Paragraph("Career guidance is informational. Verify current course details, eligibility and job postings on official websites.", styles["Italic"]))

    doc.build(content)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data


def make_download(profile, plan, file_format="json"):
    if file_format == "pdf":
        return create_pdf_report(profile, plan)

    if file_format == "markdown":
        lines = ["# Student Career Guidance Plan", "", "## Student profile"]
        for key, value in profile.items():
            lines.append(f"- **{key.replace('_', ' ').title()}:** {', '.join(value) if isinstance(value, list) else value}")
        lines += ["", "## Profile summary", plan.get("profile_summary", "")]
        lines += ["", "## Recommended career paths"]
        for role in plan.get("career_paths", []):
            lines += [f"### {role.get('role', 'Career role')}", role.get("why_it_fits", ""), "",
                      "**Responsibilities**"]
            lines += [f"- {x}" for x in role.get("responsibilities", [])]
            lines += ["", "**Required skills**", ", ".join(role.get("required_skills", []))]
            lines += ["", "**Certifications**"]
            lines += [f"- {x}" for x in role.get("certifications", [])]
            lines.append("")
        gaps = plan.get("skill_gap", {})
        lines += ["## Skill-gap analysis", "", "**Existing skills**"]
        lines += [f"- {x}" for x in gaps.get("existing_skills", [])]
        lines += ["", "**Skills to develop**"]
        lines += [f"- {x}" for x in gaps.get("missing_skills", [])]
        lines += ["", "## Learning roadmap"]
        for stage in plan.get("roadmap", []):
            lines += [f"### {stage.get('stage', '')}", stage.get("goal", ""),
                      f"- **Topics:** {', '.join(stage.get('topics', []))}"]
            lines += [f"- {x}" for x in stage.get("activities", [])]
            lines += [f"- **Project:** {stage.get('project', '')}", ""]
        lines += ["## Learning resources"]
        for r in plan.get("learning_resources", []):
            lines.append(f"- [{r.get('name', '')}]({r.get('url', '')}) — {r.get('purpose', '')}")
        lines += ["", "## Job-search resources"]
        for r in plan.get("job_search_resources", []):
            lines.append(f"- [{r.get('name', '')}]({r.get('url', '')}) — {r.get('purpose', '')}")
        lines += ["", "> Career guidance is informational. Verify current course details, eligibility and job postings on official websites."]
        return "\n".join(lines)

    return json.dumps({"student_profile": profile, "career_plan": plan}, indent=2, ensure_ascii=False)
