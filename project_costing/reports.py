from django.template.loader import render_to_string
from weasyprint import HTML

from .models import LabourEntry


def generate_worker_payout_report(project):
    labour_entries = LabourEntry.objects.filter(project=project)
    context = {
        "project": project,
        "labour_entries": labour_entries,
    }
    html_string = render_to_string("project_costing/worker_payout_report.html", context)
    html = HTML(string=html_string)
    pdf_file = f"{project.name}_worker_payout_report.pdf"
    html.write_pdf(target=pdf_file)
    return pdf_file
