# Arctos Tableau Dashboard

**1. 📌 Project Overview**

This Tableau dashboard provides a user-friendly, visual interface to explore and understand the system-level statistics from the Arctos collection management system. It’s designed to help researchers, data contributors, and institutions interactively explore taxonomic and geographic data, annotations, and record contributions.

**2. 🗂️ Dashboard Tabs & Functions**

#### Tab Name: Readme

Purpose: Includes project description, researcher credits, glossary, and creation date


#### Tab Name: Summary

Purpose:

- Top bar chart: System statistics (collections, agents, taxa, annotations, etc.)
- Bottom left: Record counts by Guid Prefix
- Bottom right: Contribution by institution (pie chart)

Filters: Institution name, Collection type


#### Tab Name: Spatial Analysis

Purpose: Interactive map of record locations

Dot size = record count, Dot color = time period

Hover reveals detailed location metadata & record-type bubbles

Filter by country available


**3. 🔐 Access & Data Source**

Data Source: Arctos Public Database- https://arctos.database.museum/record_summary.cfm

<img width="398" alt="image" src="https://github.com/user-attachments/assets/dd605193-6b60-41db-a56a-8240d43f60f3" />

 
Dashboard Location: Tableau Public (Shivani Tayade’s account)

Proposed Final Location: Arctos or MVZ-affiliated Tableau account

Current Update Method: Manual data upload to Tableau Workbook

**4. ⚙️ Maintenance & Updates**

#### Task: Data Refresh

Frequency: As needed

Method: Manually replace data in Tableau workbook

#### Task: Metadata Review

Frequency: Quarterly

Method: Verify taxonomy, GUIDs, annotations

#### Task: Dashboard Publication

Frequency: On updates

Method: Republish to Tableau Public

#### Task: Dashboard Migration

Frequency: Once

Method: Transfer to MVZ/Arctos Tableau Account (if approved)

**5. 📥 How to Export Dashboard (PPT / PDF)**
Click the Download button in the top-right of the Tableau Public dashboard.

Choose from:

- Image (.PNG)
- PDF
- PowerPoint (.PPTX) – if available
- Data (CSV/Excel)

  
If PPT is not available:

- Download as PDF
- Convert PDF to PPT using Adobe Acrobat or online tools

  
**6. 📧 Key Contacts**

Name: Shivani Tayade

Role: Current Owner

Contact: svtayade@ucdavis.edu

Name: Michelle Koo

Role: Data Source Admin

Contact: mkoo@berkeley.edu

**7. 🧠 Notes & Recommendations**

- Consider automating data ingestion in the future using Tableau Prep or Python → Tableau API.
- Maintain consistency in taxonomic levels and time ranges for dot color categorization.
- Clarify legends for dot size and color to aid non-technical users.
- Document changes to filters or layout in a changelog tab if multiple editors are involved.

  
**8. 🔄 Dashboard Update Process (Manual Upload – Current Method)**

The dashboard currently requires manual updates whenever new data is available from Arctos. Below is a step-by-step process:

1. Download Latest Data from Arctos
- Visit https://arctos.database.museum/home.cfm
- Export necessary modules as CSV
  
2. Clean and Format the Data
- Use Excel or Google Sheets
- Ensure consistency in headers and structure
  
3. Open Tableau Workbook (.twbx)
- Replace data source using Data > Replace Data Source
  
4. Verify Visualizations
- Ensure charts, filters, and legends are working
  
5. Update Metadata (if needed)
- Add new institutions, update glossary, credits, or date in Readme tab
  
6. Publish Updated Dashboard
- Save to Tableau Public (or proposed institutional account)
  
7. Confirm Publication
- Test filters, interactivity, and download options
