# Job Scraper Project

Automated tool for scraping contract job opportunities from LinkedIn, Monster, and Dice platforms.

# Web Scraper Project

An automated job scraping tool that extracts contract job opportunities from LinkedIn, Monster, and Dice platforms. The system analyzes job postings across different technology verticals and provides state-wise analysis of contractual roles.

## 🚀 Features

- **Multi-Platform Scraping**: Extracts job data from LinkedIn, Monster, and Dice
- **Automated Scheduling**: 
  - Monday: 72-hour window (captures weekend postings)
  - Tuesday-Friday: 24-hour window (daily captures)
- **Vertical Classification**: Categorizes jobs into ERP, Infrastructure & BT, DevOps & BI, and QA/QE
- **Contract Job Filtering**: Focuses specifically on contract/freelance opportunities
- **State-wise Analysis**: Maps job opportunities across US states
- **Excel Output**: Generates comprehensive reports with multiple analysis sheets
- **Anti-Bot Protection**: Implements measures to handle platform restrictions

## 📋 Prerequisites

- Python 3.8 or higher
- Chrome browser (for Selenium WebDriver)
- Virtual environment (recommended)

## 🛠️ Installation

1. **Clone the repository**
git clone https://github.com/Aadarsh-07/web-scraper-project.git


2. **Create virtual environment**
python -m venv venv

Windows
venv\Scripts\activate

Mac/Linux
source venv/bin/activate



3. **Install dependencies**
pip install -r requirements.txt


4. **Configure settings**
- Update `config/settings.yaml` with your preferences
- Modify `config/roles_mapping.json` to customize search terms

## 🚀 Usage

### Manual Scraping
Scrape all platforms
python src/main.py --mode manual --platform all

Scrape specific platform
python src/main.py --mode manual --platform linkedin
python src/main.py --mode manual --platform monster
python src/main.py --mode manual --platform dice



### Scheduled Scraping
python src/main.py --mode scheduled


## 📊 Output Format

The scraper generates Excel files with the following structure:

### Main Data Sheet
- **Role**: Job title
- **Vertical/Industry**: ERP, Infrastructure & BT, DevOps & BI, QA/QE
- **State**: US state location
- **Platform**: LinkedIn, Monster, or Dice
- **Job Posting Date**: When the job was posted
- **Contract Duration**: Length of contract (if specified)

### Analysis Sheets
- **Vertical Analysis**: Job distribution by technology vertical
- **State Analysis**: Geographic distribution of opportunities
- **Platform Analysis**: Comparison across job platforms

## ⚙️ Configuration

### Search Terms by Vertical

**ERP**: SAP, Oracle ERP, SAP ABAP, SAP HANA, Oracle Financials, PeopleSoft, JD Edwards

**Infrastructure & BT**: Network Engineer, System Administrator, AWS, Azure, VMware, Kubernetes, Docker

**DevOps & BI**: DevOps Engineer, CI/CD, Jenkins, Tableau, Power BI, Data Warehouse, ETL

**QA/QE**: Quality Assurance, Test Automation, Selenium, API Testing, Performance Testing

### Scheduling Configuration
- **Monday 9:00 AM**: 72-hour window scraping
- **Tuesday-Friday 9:00 AM**: 24-hour window scraping
