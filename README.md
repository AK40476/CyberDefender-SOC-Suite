## CyberDefender SOC Suite

**A Software-Based Security Operations Center Platform for Threat Detection, Alert Prioritization, and Incident Investigation**

CyberDefender SOC Suite is a Python-based web application designed to simulate core Security Operations Center (SOC) workflows. It provides a centralized interface for security log ingestion, suspicious activity detection, alert risk scoring, alert correlation, attack-chain identification, threat prioritization, and incident investigation.

The platform helps demonstrate how security events can be transformed into actionable alerts and investigated through structured workflows involving indicators of compromise (IOCs), evidence, analyst notes, investigation timelines, and audit logs.

## Project Status

**Status: Completed — Core Features Implemented and Validated**

This project was developed as an academic cybersecurity project to demonstrate practical SOC concepts using a modular web application.

## Key Features

* **Security Log Ingestion:** Accepts security log events through the application's log-ingestion interface.
* **Brute-Force Detection:** Detects repeated failed login attempts from a source IP within a configured time window.
* **Credential-Stuffing Detection:** Identifies suspicious authentication activity involving multiple usernames from the same source IP.
* **IOC-Based Detection:** Matches source IP addresses against stored indicators of compromise.
* **Automated Alert Generation:** Creates security alerts when supported detection rules are triggered.
* **Risk Scoring:** Assigns numerical risk scores to alerts.
* **Alert Prioritization:** Classifies alerts into Critical, High, Medium, or Low priority levels.
* **Alert Correlation:** Identifies related alerts based on source IP and a configured correlation window.
* **Attack-Chain Detection:** Classifies related security activity into supported attack-chain categories.
* **SOC Triage Queue:** Organizes active alerts to support investigation prioritization.
* **Incident Management:** Creates, assigns, and tracks security incidents.
* **Incident Workflow Enforcement:** Restricts incident status changes to supported transitions.
* **IOC Management:** Stores, searches, filters, and associates indicators of compromise with incidents.
* **Evidence Management:** Maintains evidence records and their associated incident information.
* **Analyst Notes:** Supports recording investigation observations.
* **Investigation Timeline:** Records incident investigation activities and status changes.
* **Audit Logging:** Maintains records of important application and investigation actions.
* **SOC Analytics:** Summarizes alert activity, severity, status, and detection-rule information.
* **Authentication and Role-Based Access Control:** Protects application functionality using user authentication and role-based authorization.

## SOC Workflow

The platform follows this general security operations workflow:

Security Log Ingestion
          |
          v
    Detection Engine
          |
          v
    Alert Generation
          |
          v
      Risk Scoring
          |
          v
   Alert Correlation
          |
          v
   Attack-Chain Analysis
          |
          v
  Alert Prioritization
          |
          v
      Triage Queue
          |
          v
 Incident Investigation
          |
          v
 IOCs, Evidence, Notes,
 Timeline and Audit Logs
          |
          v
      SOC Analytics

## Detection Capabilities

### 1. Brute-Force Login Detection

Detects repeated failed login attempts originating from the same source IP within the configured detection window.

**Detection rule:** `BRUTE_FORCE_LOGIN`

The implemented detection threshold is five failed login events within five minutes.

### 2. Credential-Stuffing Detection

Identifies authentication activity involving multiple distinct usernames from the same source IP within the configured time window.

**Detection rule:** `CREDENTIAL_STUFFING`

The implemented threshold is three or more distinct usernames within five minutes.

### 3. Suspicious IP and IOC Detection

Checks source IP activity against stored IP-based indicators of compromise. Matches can generate alerts with severity determined by the configured detection logic and IOC information.

**Detection rule:** `IOC_MATCH`

These capabilities demonstrate rule-based detection. They do not represent a replacement for a production SIEM or a complete enterprise threat-detection platform.

## Risk Scoring and Alert Prioritization

CyberDefender assigns numerical risk scores to alerts and uses risk scores, alert severity, and correlation information to help prioritize investigation.

The prioritization service supports four levels:

* **Critical**
* **High**
* **Medium**
* **Low**

The triage queue focuses on active alerts, including alerts in New and Investigating states.

## Alert Correlation and Attack Chains

The correlation engine identifies related alerts associated with the same source IP within a configured **10-minute correlation window**. It evaluates detection-rule combinations to classify correlated activity.

Supported attack-chain classifications include:

* `BRUTE_FORCE_IOC_CHAIN`
* `CREDENTIAL_ATTACK_CHAIN`
* `CREDENTIAL_IOC_CHAIN`
* `MULTI_STAGE_ATTACK`
* `CORRELATED_ACTIVITY`

Correlation helps analysts investigate related events as a potential sequence of suspicious activity rather than treating every alert as an isolated event.

## Incident Investigation

The platform supports converting eligible alerts into structured incidents while preserving the relationship between an alert and its originating incident.

Incident investigation capabilities include:

* Incident creation and assignment
* Linked originating alerts
* Controlled incident status transitions
* Investigation timeline entries
* Analyst notes
* Associated indicators of compromise
* Evidence records
* Audit logging

Supported incident states include Open, Investigating, Contained, Resolved, and False Positive. Valid transitions are enforced by the incident workflow logic.

## Indicator of Compromise (IOC) Management

The IOC module supports managing indicators associated with security investigations.

Supported indicator types include:

* IP addresses
* Domains
* URLs
* MD5 hashes
* SHA-1 hashes
* SHA-256 hashes
* Email addresses

The application provides IOC listing, search and filtering functionality, detail views, and incident associations.

## Evidence Management

The evidence module allows analysts to maintain evidence records associated with incidents.

Evidence records support fields such as:

* Evidence title
* Evidence type
* Hash information
* Collection information
* Associated incident

The module maintains evidence metadata; it should not be interpreted as a complete forensic acquisition or chain-of-custody platform.

## Audit Logging and Investigation Timeline

Audit logs provide traceability for important actions performed in the application. Investigation timeline entries help preserve the sequence of activities associated with incidents.

Together, these capabilities demonstrate accountability and structured investigation recordkeeping.

## Authentication and Access Control

The application uses Flask-Login for authentication and role-based access-control logic to protect supported routes and functionality.

The project includes analyst and administrative access.

## Technology Stack

| Technology       | Purpose                                    |
| ---------------- | ------------------------------------------ |
| Python 3.11      | Application logic and detection services   |
| Flask            | Web application framework                  |
| Flask-SQLAlchemy | Database integration and ORM               |
| Flask-Login      | User authentication and session management |
| SQLite           | Relational database                        |
| HTML5            | Web page structure                         |
| CSS3             | Interface styling                          |
| JavaScript       | Client-side functionality                  |
| Jinja2           | Server-side HTML templating                |
| Git              | Version control                            |

## Project Structure

CyberDefender-SOC-Suite/
├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── templates/
│   └── utils/
├── tests/
├── create_admin.py
├── create_analyst.py
├── run.py
├── requirements.txt
├── README.md
└── .gitignore

## Installation and Setup

### Prerequisites

* Python 3.11 or a compatible Python version
* pip
* PowerShell on Windows, or an equivalent terminal
* Git (optional, if using a cloned repository)

### 1. Open the project directory

```powershell
cd CyberDefender-SOC-Suite
```

### 2. Create a virtual environment

```powershell
python -m venv venv
```

### 3. Activate the virtual environment

On Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Initialize the database

Run the application entry point once to create the required database tables:

```powershell
python run.py
```

Wait for the Flask server to start, then stop it using `Ctrl+C`.

### 6. Create application users

Create an administrator account:

```powershell
python create_admin.py
```

Create an analyst account:

```powershell
python create_analyst.py
```

Follow the prompts to enter and confirm each account password. Passwords are entered securely and are not stored in the source code.

## Running the Application

From the project root, with the virtual environment activated, run:

```powershell
python run.py
```

Open the local address in a browser:

http://127.0.0.1:5000

Sign in using a locally configured account.

**Security note:** Use a trusted local environment for demonstrations. Do not expose the Flask development server directly to the public internet.

## Validation

The project includes automated unit and integration tests covering risk scoring, alert prioritization, detection workflows, API endpoints, and incident lifecycle operations.

The test suite was executed successfully, with all 33 tests passing.

## Limitations

CyberDefender SOC Suite is an academic demonstration platform. Its capabilities are limited to the implemented detection rules, configured data sources, and application workflows.

The current project should not be represented as a production SIEM, a fully automated response platform, or a continuously monitoring endpoint security agent. Real-time operating-system event collection, external threat-intelligence integrations, and automated containment are potential future extensions rather than assumed current capabilities.

## Future Enhancements

Potential extensions include:

* Windows Event Log collection
* Linux authentication-log collection
* Network traffic monitoring and analysis
* External threat-intelligence integrations
* Email and desktop notifications
* Additional detection rules
* Expanded automated test coverage for additional workflows
* SIEM integration
* Automated unit and integration tests
* Containerized deployment

## Project Objective

The objective of CyberDefender SOC Suite is to demonstrate practical cybersecurity concepts and SOC analyst workflows, including security event ingestion, rule-based detection, alert prioritization, event correlation, incident investigation, IOC management, evidence tracking, and security auditing.

## Authors

Developed by a student as an academic cybersecurity project.

## License

This project is intended for academic and educational purposes. No separate open-source license is specified in this repository.
