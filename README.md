```markdown
# 🛡️ Aura51 Security Compliance Advisor

**AI-Powered Risk Assessment and Compliance Management Platform**

Aura51 is an intelligent, explainable AI platform designed to streamline third-party security and compliance assessments.  
It automates questionnaire analysis, calculates risk scores, and provides transparent, actionable insights across major cybersecurity frameworks — all through an interactive dashboard and professional PDF reports.

---

## 🚀 Key Features

### 🔍 Automated Questionnaire Analysis
- Accepts CSV, Excel, and JSON formats  
- Detects multiple questionnaire types (SIG, CAIQ, NIST CSF, etc.)  
- Smart categorization of questions into security domains  

### ⚙️ AI-Powered Risk Scoring
- Multi-factor scoring based on vendor responses  
- Machine-learning–enhanced TPRA (Third-Party Risk Assessment) module  
- Domain-specific insights: Data Protection, Access Control, Vulnerability Management, etc.

### 🔐 Framework Compliance Mapping
- Evaluates alignment against 8 major frameworks:  
  `ISO 27001 • NIST CSF • PCI DSS • GDPR • HIPAA • CCPA • CIS Controls • HITRUST`

### 💬 Explainable AI Insights
- Generates **natural-language explanations** for each finding  
- Identifies gaps and provides prioritized recommendations  
- Maps issues to framework controls for remediation

### 📊 Interactive Risk Dashboard
- **Streamlit** interface with interactive charts (Plotly)  
- Risk Matrix, Domain Score Graphs, and Compliance Radar Charts  
- Exportable **PDF reports** with embedded visual analytics  

---

## 🧠 Technical Architecture

| Component | Description |
|------------|-------------|
| **`core/advisor/questionnaire_processor.py`** | Parses and normalizes questionnaire data |
| **`core/risk/risk_scoring_model.py`** | Calculates multi-domain risk scores |
| **`core/risk/explainable_risk_module.py`** | Generates SHAP-based risk explanations |
| **`core/tpra/tpra_module.py`** | Machine-learning module for deeper risk detection |
| **`app/pages/dashboard_page.py`** | Interactive dashboard built with Streamlit & Plotly |
| **`utils/pdf_generator.py`** | PDF reporting engine (ReportLab + Matplotlib) |

---

## 🧩 Data Flow

```

1. Upload questionnaire file (CSV/Excel/JSON)
2. Data parsed and normalized by Questionnaire Processor
3. Risk Scoring Model calculates domain risk values
4. Explainable AI module generates insights (SHAP, NLP)
5. Streamlit Dashboard visualizes metrics in real time
6. Optional PDF report generated for download

````

---

## 🧰 Tech Stack

**Languages:** Python  
**Frameworks & Libraries:** FastAPI, Streamlit, Pandas, NumPy, XGBoost, SHAP, Plotly, ReportLab  
**AI/ML:** TPRA Risk Model, Explainable AI (SHAP + NLP)  
**Visualization:** Plotly, Matplotlib  
**Deployment:** Streamlit Cloud / On-Premises  

---

## 🧪 Use Cases

- Vendor Security & Risk Assessments  
- Multi-framework Compliance Management  
- Third-Party Risk Monitoring (TPRM)  
- Security Due Diligence for M&A or Procurement  

---

## 🏆 Recognition

> 🎯 **Top 6 Finalist** — *SecurityPal × NAAMII AI Hackathon*  
> Developed as part of a 2-day challenge focused on building explainable AI systems for cybersecurity and compliance automation.

---

## 💡 Challenges & Learnings

Building Aura51 required integrating structured data processing, AI models, and explainable insights into one workflow.  
The most difficult challenge was handling inconsistent vendor questionnaire formats and mapping them across frameworks.  
Through this, I learned the value of **modular backend design**, **data normalization**, and **clear, human-readable AI explanations**.

---

## 📸 Screenshots

| Dashboard | Risk Matrix | PDF Report |
|------------|-------------|------------|
| ![Dashboard](docs/dashboard.png) | ![Matrix](docs/matrix.png) | ![Report](docs/pdfreport.png) |

---

## ⚙️ Installation

```bash
# Clone repository
git clone https://github.com/HasEEnaEEby/Aura51-Security-Compliance-Advisor

# Navigate to project
cd Aura51-Security-Compliance-Advisor

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app/main.py
````

---

## 🧾 Example Output

* **Overall Risk Score** (0-100%)
* **Framework Compliance Radar Chart**
* **Domain-wise Risk Breakdown**
* **AI-Generated Risk Explanations**
* **PDF Report with Actionable Recommendations**

---

## 👩‍💻 Author

**Hasina KC Khatri**
BSc (Hons) Computing — Coventry University (Softwarica College)
💼 Data & Backend Engineer | AI & Explainability Researcher
📧 [rkc697418@gmail.com](mailto:rkc697418@gmail.com)
🌐 [GitHub @HasEEnaEEby](https://github.com/HasEEnaEEby)

---

## 🛠️ License

This project is released for educational and research purposes.
© 2025 Hasina KC Khatri. All rights reserved.

```
