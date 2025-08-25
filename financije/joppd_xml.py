"""Minimal JOPPD XML exporter for payroll runs."""

from __future__ import annotations

from xml.etree.ElementTree import Element, SubElement, tostring

from .payroll import PayrollRun


def export_joppd(run: PayrollRun) -> str:
    """Return a basic JOPPD XML representation of the given run."""
    root = Element("JOPPD")
    for item in run.items:
        emp = SubElement(root, "Employee")
        SubElement(emp, "Name").text = item.employee
        SubElement(emp, "Gross").text = str(item.gross)
        SubElement(emp, "Net").text = str(item.net)
        SubElement(emp, "Tax").text = str(item.tax)
        SubElement(emp, "PensionI").text = str(item.pension_i)
        SubElement(emp, "PensionII").text = str(item.pension_ii)
        if item.profit_share:
            SubElement(emp, "ProfitShare").text = str(item.profit_share)
    return tostring(root, encoding="unicode")
