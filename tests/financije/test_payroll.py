from datetime import date
from decimal import Decimal

from lxml import etree

from financije.joppd_xml import export_joppd
from financije.payroll import PayrollItem, PayrollRun


def test_payroll_calculation_and_joppd_xml_validation():
    run = PayrollRun(
        date(2025, 1, 31),
        [
            PayrollItem("Ana", Decimal("1000")),
            PayrollItem("Bruno", Decimal("3000")),
            PayrollItem("Cecilija", Decimal("2000"), profit_share=Decimal("500")),
        ],
    )
    run.calculate()

    a, b, c = run.items
    assert a.net == Decimal("746.00")
    assert b.tax == Decimal("374.00")
    assert c.net == Decimal("1886.00")
    assert run.total_cost == Decimal("7490.00")

    xml = export_joppd(run)
    doc = etree.fromstring(xml.encode())

    xsd = """
    <xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
      <xsd:element name="JOPPD">
        <xsd:complexType>
          <xsd:sequence>
            <xsd:element name="Employee" minOccurs="1" maxOccurs="unbounded">
              <xsd:complexType>
                <xsd:sequence>
                  <xsd:element name="Name" type="xsd:string"/>
                  <xsd:element name="Gross" type="xsd:decimal"/>
                  <xsd:element name="Net" type="xsd:decimal"/>
                  <xsd:element name="Tax" type="xsd:decimal"/>
                  <xsd:element name="PensionI" type="xsd:decimal"/>
                  <xsd:element name="PensionII" type="xsd:decimal"/>
                  <xsd:element name="ProfitShare" type="xsd:decimal" minOccurs="0"/>
                </xsd:sequence>
              </xsd:complexType>
            </xsd:element>
          </xsd:sequence>
        </xsd:complexType>
      </xsd:element>
    </xsd:schema>
    """
    schema = etree.XMLSchema(etree.fromstring(xsd))
    schema.assertValid(doc)

    assert len(doc.findall("Employee")) == 3
