# CivilSaaS - Sistema para Engenheiros Civis

## Overview

CivilSaaS is a comprehensive software-as-a-service platform designed specifically for civil engineers to manage construction projects. The system provides end-to-end project management capabilities covering all major pain points in civil engineering: deadlines, costs, bureaucracy, workforce, sustainability, safety, technology, and technical responsibility.

The platform offers modules for project management, budgeting, permits and licenses, safety incident tracking, supplier management, risk assessment, compliance documentation, field measurements (IoT integration), sustainability tracking, workforce training, and comprehensive reporting.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python) - Lightweight web framework chosen for rapid development and simplicity
- **Database**: SQLite3 with row factory for dictionary-like access - File-based database for easy deployment and maintenance without external dependencies
- **Authentication**: Session-based authentication using Flask sessions with password hashing via Werkzeug
- **File Structure**: Modular blueprint architecture separating concerns into distinct modules (auth, projects, budget, safety, etc.)

### Database Design
- **Schema Management**: Single schema.sql file with all table definitions for easy version control
- **Audit Trail**: Built-in audit logging system tracking all database changes with old/new values
- **Data Access**: Direct SQL queries using sqlite3 library without ORM for performance and control

### Frontend Architecture
- **Template Engine**: Jinja2 templates with inheritance-based layout system
- **Styling**: Bootstrap 5 for responsive design with custom CSS enhancements
- **JavaScript**: Vanilla JavaScript with utility functions for form validation, file uploads, and UI interactions
- **Icons**: Font Awesome for consistent iconography

### Modular Blueprint Structure
Each major feature is implemented as a Flask blueprint:
- **Auth**: User authentication and session management
- **Projects**: Core project management functionality
- **Budget**: Financial tracking and cost management
- **Safety**: Incident reporting and safety management
- **Suppliers**: Vendor and purchase order management
- **Permits**: License and permit tracking with document uploads
- **Risks**: Risk assessment with probability/impact matrices
- **Compliance**: Document management and regulatory compliance
- **Field**: IoT device measurements and field data collection
- **Sustainability**: Carbon emissions tracking and material usage
- **Training**: Workforce training and certification management
- **Reports**: Comprehensive reporting with export capabilities

### File Upload System
- **Storage**: Local file system with uploads/ directory
- **Validation**: File type and size restrictions for security
- **Organization**: Systematic file naming and organization by module

### Security Considerations
- **Input Validation**: Form validation on both client and server side
- **SQL Injection Prevention**: Parameterized queries throughout
- **File Upload Security**: Restricted file types and secure filename handling
- **Session Management**: Secure session configuration with environment-based secret keys

## External Dependencies

### Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design and UI components
- **Font Awesome**: Icon library for consistent visual elements
- **Chart.js**: Client-side charting library for data visualization (implied in templates)

### Python Dependencies
- **Flask**: Core web framework
- **Werkzeug**: WSGI utilities and security functions (password hashing, file uploads)
- **SQLite3**: Database engine (Python standard library)

### Infrastructure Requirements
- **File System**: Local storage for uploaded documents and files
- **Session Storage**: Server-side session management
- **Environment Variables**: Configuration management for sensitive data (SESSION_SECRET)

### Future Integration Points
The system is architected to support future integrations with:
- **IoT Devices**: Field measurement endpoints for sensor data
- **External APIs**: Government permit systems, environmental databases
- **Email Services**: Notification systems for alerts and reports
- **Cloud Storage**: Document storage migration capabilities
- **Mobile Applications**: RESTful API endpoints for mobile access