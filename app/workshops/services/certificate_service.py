"""
Certificate Generation Service for Workshops
Handles generating PDF certificates for workshop completions
"""
import os
from io import BytesIO
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import jdatetime
import logging

logger = logging.getLogger(__name__)

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import Paragraph, Spacer, Image
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("reportlab is not installed. Certificate generation will use basic PDF generation.")


class CertificateService:
    """Service class for generating workshop certificates"""
    
    def __init__(self):
        self.available = REPORTLAB_AVAILABLE
        if REPORTLAB_AVAILABLE:
            self.page_width, self.page_height = A4
        else:
            # Default A4 size in points (when reportlab is not available)
            self.page_width = 595.27
            self.page_height = 841.89
    
    def generate_certificate_pdf(self, certificate):
        """
        Generate a PDF certificate for a workshop completion
        
        Args:
            certificate: WorkshopCertificate instance
            
        Returns:
            BytesIO: PDF file content
        """
        if not self.available:
            logger.error("reportlab is not available. Cannot generate certificate PDF.")
            return None
        
        try:
            registration = certificate.registration
            user = registration.user
            workshop = registration.workshop
            
            # Create a BytesIO buffer for the PDF
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            # Set up colors
            border_color = colors.HexColor('#1a237e')  # Dark blue
            text_color = colors.HexColor('#212121')  # Dark gray
            accent_color = colors.HexColor('#1976d2')  # Blue
            
            # Draw decorative border
            border_width = 20
            c.setStrokeColor(border_color)
            c.setLineWidth(border_width)
            c.rect(border_width, border_width, 
                   width - 2*border_width, height - 2*border_width)
            
            # Draw inner decorative border
            inner_border = 40
            c.setLineWidth(2)
            c.rect(inner_border, inner_border, 
                   width - 2*inner_border, height - 2*inner_border)
            
            # Title
            c.setFillColor(accent_color)
            c.setFont("Helvetica-Bold", 36)
            title_y = height - 120
            title = "گواهینامه"
            title_width = c.stringWidth(title, "Helvetica-Bold", 36)
            c.drawString((width - title_width) / 2, title_y, title)
            
            # Subtitle
            c.setFillColor(text_color)
            c.setFont("Helvetica", 18)
            subtitle = "Certificate of Completion"
            subtitle_width = c.stringWidth(subtitle, "Helvetica", 18)
            c.drawString((width - subtitle_width) / 2, title_y - 35, subtitle)
            
            # Main content
            content_y = height - 250
            c.setFont("Helvetica", 16)
            
            # This is to certify that
            text1 = "این گواهینامه به این منظور صادر می‌شود که"
            text1_width = c.stringWidth(text1, "Helvetica", 16)
            c.drawString((width - text1_width) / 2, content_y, text1)
            
            # User name
            c.setFont("Helvetica-Bold", 24)
            user_name = user.full_name
            user_name_width = c.stringWidth(user_name, "Helvetica-Bold", 24)
            c.drawString((width - user_name_width) / 2, content_y - 50, user_name)
            
            # Workshop completion text
            c.setFont("Helvetica", 16)
            text2 = "دوره آموزشی زیر را با موفقیت به پایان رسانده است:"
            text2_width = c.stringWidth(text2, "Helvetica", 16)
            c.drawString((width - text2_width) / 2, content_y - 100, text2)
            
            # Workshop title
            c.setFont("Helvetica-Bold", 20)
            workshop_title = workshop.title
            workshop_title_width = c.stringWidth(workshop_title, "Helvetica-Bold", 20)
            c.drawString((width - workshop_title_width) / 2, content_y - 140, workshop_title)
            
            # Workshop details
            c.setFont("Helvetica", 14)
            details_y = content_y - 200
            
            # Total hours
            hours_text = f"مدت زمان دوره: {workshop.total_hours} ساعت"
            hours_width = c.stringWidth(hours_text, "Helvetica", 14)
            c.drawString((width - hours_width) / 2, details_y, hours_text)
            
            # Issue date
            if certificate.issued_at:
                issue_date = jdatetime.datetime.fromgregorian(datetime=certificate.issued_at)
                date_text = f"تاریخ صدور: {issue_date.strftime('%Y/%m/%d')}"
            else:
                now = timezone.now()
                issue_date = jdatetime.datetime.fromgregorian(datetime=now)
                date_text = f"تاریخ صدور: {issue_date.strftime('%Y/%m/%d')}"
            
            date_width = c.stringWidth(date_text, "Helvetica", 14)
            c.drawString((width - date_width) / 2, details_y - 30, date_text)
            
            # Certificate number
            cert_num_text = f"شماره گواهینامه: {certificate.certificate_number}"
            cert_num_width = c.stringWidth(cert_num_text, "Helvetica", 12)
            c.drawString((width - cert_num_width) / 2, details_y - 60, cert_num_text)
            
            # Instructor signature area
            signature_y = 150
            c.setFont("Helvetica", 14)
            instructor_name = workshop.instructor.full_name
            instructor_text = f"مدرس: {instructor_name}"
            instructor_width = c.stringWidth(instructor_text, "Helvetica", 14)
            c.drawString((width - instructor_width) / 2, signature_y, instructor_text)
            
            # Verification code (small text at bottom)
            c.setFont("Helvetica", 10)
            verification_text = f"کد تأیید: {certificate.verification_code}"
            verification_width = c.stringWidth(verification_text, "Helvetica", 10)
            c.drawString((width - verification_width) / 2, 50, verification_text)
            
            # Save the PDF
            c.save()
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating certificate PDF: {str(e)}")
            return None
    
    def generate_and_save_certificate(self, certificate):
        """
        Generate PDF certificate and save it to the certificate file field
        
        Args:
            certificate: WorkshopCertificate instance
            
        Returns:
            bool: Success status
        """
        try:
            pdf_buffer = self.generate_certificate_pdf(certificate)
            if not pdf_buffer:
                return False
            
            # Generate filename
            filename = f"certificate_{certificate.certificate_number}.pdf"
            filepath = f"workshops/certificates/{filename}"
            
            # Save to storage
            certificate.certificate_file.save(
                filename,
                ContentFile(pdf_buffer.read()),
                save=False
            )
            
            # Update certificate status
            certificate.status = 'issued'
            if not certificate.issued_at:
                certificate.issued_at = timezone.now()
            certificate.save()
            
            logger.info(f"Certificate {certificate.certificate_number} generated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving certificate PDF: {str(e)}")
            return False
    
    def can_issue_certificate(self, registration):
        """
        Check if a certificate can be issued for a registration
        
        Args:
            registration: WorkshopRegistration instance
            
        Returns:
            tuple: (can_issue: bool, reason: str)
        """
        # Check if registration is completed
        if registration.status != 'completed':
            return False, "Registration is not completed"
        
        # Check if progress is sufficient (e.g., at least 80%)
        if registration.progress_percentage < 80:
            return False, f"Progress is insufficient ({registration.progress_percentage}%). Minimum 80% required."
        
        # Check if workshop is completed
        if registration.workshop.status != 'completed':
            return False, "Workshop is not completed"
        
        # Check if certificate already exists
        if hasattr(registration, 'certificate'):
            if registration.certificate.status == 'issued':
                return False, "Certificate already issued"
        
        return True, "Certificate can be issued"


# Singleton instance
certificate_service = CertificateService()

