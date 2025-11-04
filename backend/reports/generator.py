from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os
from database.connection import db
from database.models import Complaint, User, PoliceOfficer, CaseAssignment, CaseUpdate
from admin.advanced_analytics import advanced_analytics

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for reports"""
        # Custom title style
        self.title_style = ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Center
            textColor=colors.HexColor('#2c3e50')
        )
        
        # Custom heading style
        self.heading_style = ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#34495e')
        )
        
        # Custom body style
        self.body_style = ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            spaceAfter=6
        )
        
        # Custom small style
        self.small_style = ParagraphStyle(
            name='CustomSmall',
            parent=self.styles['BodyText'],
            fontSize=8,
            spaceAfter=4
        )
    
    def generate_case_report(self, case_id, output_path=None):
        """Generate case PDF report - FIXED VERSION"""
        try:
            print(f"🔍 Starting case report generation for: {case_id}")
            
            case = Complaint.query.filter_by(case_id=case_id).first()
            if not case:
                raise ValueError(f"Case {case_id} not found")
            
            if not output_path:
                reports_dir = 'reports'
                os.makedirs(reports_dir, exist_ok=True)
                output_path = os.path.join(reports_dir, f"case_report_{case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            
            doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=50, bottomMargin=50)
            story = []
            
            # Build the report content step by step with error handling
            try:
                # Header
                story.extend(self._create_header(case_id))
                story.append(Spacer(1, 20))
                
                # Case Overview
                story.append(Paragraph("Case Overview", self.heading_style))
                overview_data = self._get_case_overview_data(case)
                story.append(self._create_table(overview_data, colors.HexColor('#f8f9fa')))
                story.append(Spacer(1, 20))
                
                # Victim Information
                story.append(Paragraph("Victim Information", self.heading_style))
                victim_data = self._get_victim_data(case)
                story.append(self._create_table(victim_data, colors.HexColor('#e8f5e8')))
                story.append(Spacer(1, 20))
                
                # Incident Details
                story.append(Paragraph("Incident Details", self.heading_style))
                description = case.description or "No description provided"
                # Ensure description is a string and handle encoding
                if isinstance(description, bytes):
                    description = description.decode('utf-8', errors='ignore')
                story.append(Paragraph(description, self.body_style))
                story.append(Spacer(1, 10))
                
                location_data = self._get_location_data(case)
                story.append(self._create_table(location_data, colors.HexColor('#e3f2fd')))
                story.append(Spacer(1, 20))
                
                # Additional Information
                story.append(Paragraph("Additional Information", self.heading_style))
                additional_data = self._get_additional_data(case)
                story.append(self._create_table(additional_data, colors.HexColor('#fff3cd')))
                story.append(Spacer(1, 20))
                
                # Case Updates/Timeline
                updates = CaseUpdate.query.filter_by(complaint_id=case.id).order_by(CaseUpdate.created_at).all()
                if updates:
                    story.append(Paragraph("Case Timeline", self.heading_style))
                    update_data = self._get_update_data(updates)
                    story.append(self._create_timeline_table(update_data))
                    story.append(Spacer(1, 20))
                
                # Assignment Information
                assignments = CaseAssignment.query.filter_by(complaint_id=case.id).all()
                if assignments:
                    story.append(Paragraph("Assigned Personnel", self.heading_style))
                    assignment_data = self._get_assignment_data(assignments)
                    story.append(self._create_table(assignment_data, colors.HexColor('#f4f6f9')))
                    story.append(Spacer(1, 20))
                
                # Footer
                story.extend(self._create_footer())
                
            except Exception as content_error:
                print(f"❌ Error building report content: {content_error}")
                # Add error message to report
                story.append(Paragraph("Error generating report content", self.heading_style))
                story.append(Paragraph(str(content_error), self.body_style))
            
            # Generate the PDF
            print("📄 Building PDF document...")
            doc.build(story)
            
            if os.path.exists(output_path):
                print(f"✅ Report generated successfully: {output_path}")
                return output_path
            else:
                raise Exception("PDF file was not created")
                
        except Exception as e:
            print(f"❌ Error in generate_case_report: {e}")
            raise

    def generate_analytics_report(self, report_type='monthly', output_path=None):
        """Generate analytics PDF report - SIMPLIFIED VERSION"""
        try:
            if not output_path:
                reports_dir = 'reports'
                os.makedirs(reports_dir, exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = os.path.join(reports_dir, f"analytics_report_{report_type}_{timestamp}.pdf")
            
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Title
            title = Paragraph(f"iReport Analytics - {report_type.title()} Report", self.title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Simple content instead of complex analytics
            story.append(Paragraph("System Analytics Summary", self.heading_style))
            
            # Basic system info
            from database.models import Complaint, User, PoliceOfficer
            
            total_cases = Complaint.query.count()
            total_users = User.query.count()
            total_officers = PoliceOfficer.query.filter_by(is_active=True).count()
            
            summary_data = [
                ['Metric', 'Count'],
                ['Total Cases', str(total_cases)],
                ['Total Users', str(total_users)],
                ['Active Officers', str(total_officers)],
                ['Report Type', report_type],
                ['Generated On', datetime.now().strftime('%Y-%m-%d %H:%M')]
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(summary_table)
            
            # Footer
            story.append(Spacer(1, 30))
            footer = self._create_footer()
            story.extend(footer)
            
            doc.build(story)
            return output_path
            
        except Exception as e:
            print(f"Error generating analytics report: {e}")
            raise

    # Keep all your existing helper methods (_create_header, _get_case_overview_data, etc.)
    def _create_header(self, case_id):
        """Create report header"""
        header_elements = []
        
        # Title
        title = Paragraph(f"CASE REPORT - {case_id}", self.title_style)
        header_elements.append(title)
        
        # Subtitle
        subtitle = Paragraph("iReport System - Official Case Documentation", self.body_style)
        header_elements.append(subtitle)
        
        return header_elements
    
    def _get_case_overview_data(self, case):
        """Get case overview data for table"""
        return [
            ['Case ID:', case.case_id],
            ['Title:', case.title or 'N/A'],
            ['Status:', case.status.title() if case.status else 'N/A'],
            ['Priority:', case.priority.title() if case.priority else 'N/A'],
            ['Crime Type:', case.crime_type.title() if case.crime_type else 'N/A'],
            ['Incident Date:', case.incident_date.strftime('%Y-%m-%d %H:%M') if case.incident_date else 'N/A'],
            ['Report Date:', case.created_at.strftime('%Y-%m-%d %H:%M') if case.created_at else 'N/A'],
            ['Last Updated:', case.updated_at.strftime('%Y-%m-%d %H:%M') if case.updated_at else 'N/A']
        ]
    
    def _get_victim_data(self, case):
        """Get victim information data"""
        return [
            ['Name:', case.victim_name or 'N/A'],
            ['Age:', str(case.victim_age) if case.victim_age else 'N/A'],
            ['Gender:', case.victim_gender or 'N/A'],
            ['Contact:', case.victim_contact or 'N/A'],
            ['Injury Involved:', 'Yes' if case.is_injury_involved else 'No'],
            ['Missing Person:', 'Yes' if case.is_missing_person else 'No']
        ]
    
    def _get_location_data(self, case):
        """Get location data"""
        return [
            ['State:', case.state or 'N/A'],
            ['District:', case.district or 'N/A'],
            ['Location:', case.location or 'N/A'],
            ['Coordinates:', f"{case.latitude}, {case.longitude}" if case.latitude and case.longitude else 'N/A']
        ]
    
    def _get_additional_data(self, case):
        """Get additional case information"""
        return [
            ['Property Damage:', 'Yes' if case.is_property_damage else 'No'],
            ['Estimated Loss:', f"₹{case.estimated_loss:,.2f}" if case.estimated_loss else 'N/A'],
            ['Police Complaint Filed:', 'Yes' if case.police_complaint_filed else 'No'],
            ['Police Station:', case.police_station or 'N/A'],
            ['FIR Number:', case.police_complaint_number or 'N/A'],
            ['Anonymous Report:', 'Yes' if case.is_anonymous else 'No']
        ]
    
    def _get_update_data(self, updates):
        """Get case update data for timeline"""
        update_data = [['Date & Time', 'Updated By', 'Update Type', 'Description']]
        
        for update in updates:
            user = User.query.get(update.updated_by)
            description = update.description or update.title or 'No description'
            # Truncate long descriptions
            if len(description) > 100:
                description = description[:100] + '...'
                
            update_data.append([
                update.created_at.strftime('%Y-%m-%d %H:%M') if update.created_at else 'N/A',
                user.full_name if user else 'System',
                update.update_type.replace('_', ' ').title() if update.update_type else 'Update',
                description
            ])
        
        return update_data
    
    def _get_assignment_data(self, assignments):
        """Get assignment information"""
        assignment_data = [['Assignee', 'Type', 'Assignment Date', 'Status']]
        
        for assignment in assignments:
            assignee_name = "Unknown"
            assignee_type = assignment.assignment_type or 'Unknown'
            
            if assignment.police_officer_id and assignment.police_officer:
                officer = assignment.police_officer
                assignee_name = f"{officer.user.full_name if officer.user else 'Unknown'} ({officer.badge_number})"
            elif assignment.volunteer_id and assignment.volunteer:
                volunteer = assignment.volunteer
                assignee_name = volunteer.user.full_name if volunteer.user else 'Unknown'
            
            assignment_data.append([
                assignee_name,
                assignee_type.title(),
                assignment.assigned_date.strftime('%Y-%m-%d') if assignment.assigned_date else 'N/A',
                assignment.status.title() if assignment.status else 'Active'
            ])
        
        return assignment_data
    
    def _create_table(self, data, header_color=colors.HexColor('#f8f9fa')):
        """Create a styled table"""
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), header_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        return table
    
    def _create_timeline_table(self, data):
        """Create timeline table with headers"""
        table = Table(data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 2.4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        return table
    
    def _create_footer(self):
        """Create report footer"""
        footer_elements = []
        
        footer_elements.append(Spacer(1, 20))
        footer_elements.append(Paragraph("_" * 80, self.body_style))
        footer_elements.append(Spacer(1, 10))
        
        generated_info = [
            f"Report generated on: {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}",
            "iReport System - Automated Report Generation",
            "This is an official system-generated document"
        ]
        
        for info in generated_info:
            footer_elements.append(Paragraph(info, self.small_style))
        
        return footer_elements

# Global report generator instance
report_generator = ReportGenerator()