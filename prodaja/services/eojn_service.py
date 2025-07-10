import requests
from bs4 import BeautifulSoup
import pdfplumber
from django.conf import settings
from ..models import TenderPreparation, TenderDocument

class EOJNService:
    def __init__(self):
        self.base_url = settings.EOJN_BASE_URL
        self.api_key = settings.EOJN_API_KEY

    def fetch_tender_data(self, tender_url):
        """Dohvaća podatke o tenderu s EOJN-a"""
        response = requests.get(tender_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        return {
            'broj': soup.find('div', class_='tender-number').text,
            'naziv': soup.select('h1.tender-title')[0].text,
            'objavljeno': soup.find('time')['datetime'],
            'rok': soup.find('div', class_='deadline').text,
            'dokumenti': self._fetch_documents(soup)
        }

    def _fetch_documents(self, soup):
        """Dohvaća i analizira dokumente"""
        documents = []
        for doc in soup.select('a.document-link'):
            file_url = doc['href']
            file_response = requests.get(file_url)
            
            if file_url.endswith('.pdf'):
                documents.append(self._analyze_pdf(file_response.content))
            
        return documents

    def _analyze_pdf(self, content):
        """Analizira PDF dokument koristeći pdfplumber"""
        with pdfplumber.open(content) as pdf:
            text = '\n'.join([page.extract_text() for page in pdf.pages])
            return self._extract_document_data(text)

    def _extract_document_data(self, text):
        """Ekstrahira relevantne podatke iz teksta dokumenta"""
        return {
            'vrsta': self._detect_document_type(text),
            'garancije': self._extract_guarantees(text),
            'kriteriji': self._extract_criteria(text),
            'text': text
        }

    def _detect_document_type(self, text):
        """Određuje vrstu dokumenta na temelju sadržaja"""
        if 'tehničke specifikacije' in text.lower():
            return 'technical'
        elif 'troškovnik' in text.lower():
            return 'financial'
        return 'other'

    def _extract_guarantees(self, text):
        """Ekstrahira podatke o garancijama"""
        guarantees = []
        # Add guarantee extraction logic
        return guarantees

    def _extract_criteria(self, text):
        """Ekstrahira kriterije evaluacije"""
        criteria = []
        # Add criteria extraction logic
        return criteria
