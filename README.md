
# Scoutify: Intelligent Lead Ranking System 💡

**Scoutify** is an AI-powered Streamlit application designed to revolutionize how businesses and individuals identify, rank, and engage with high-potential leads.

Whether you're a job seeker targeting ideal employers, an investor seeking promising startups, or a sales professional optimizing prospecting efforts — **Scoutify** leverages intelligent algorithms to deliver actionable insights.

The app allows users to define their specific goals and criteria, then intelligently filters, enriches, and ranks leads from comprehensive datasets, providing a streamlined and data-driven approach to opportunity discovery.



## ✨ Features

- **Customizable Lead Criteria**: Define target sectors, regions, and primary goals (Job Search, Investor Research, Sales Prospecting, M&A/Partnership, Market Research).
- **Dynamic Criteria Customization**: Additional fields appear based on your chosen primary goal, allowing for highly specific lead definition, now using dropdowns for predefined choices.
- **Intelligent Lead Ranking (ML-Powered)**: A machine learning model scores leads based on their relevance to your defined criteria.
- **Detailed Lead Information**: Access company data including employee count, revenue, hiring activity, funding, and contact details.
- **Interactive Table Selection**: Select multiple leads from the ranked list using checkboxes.
- **CSV Export**: Download information for selected leads for offline analysis or integration into other tools.
- **Interactive Documentation**: Step-by-step guide with a video tutorial to help users navigate the app effectively.


## 🚀 Getting Started

Follow these steps to set up and run Scoutify on your local machine.

### Prerequisites

- Python 3.8+
- `pip` (Python package installer)
- `git` (for cloning the repository)

---

### 1. Clone the Repository

```bash
https://github.com/serious22/CapraeModernization.git
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
streamlit run Home.py
```

This command launches the app in your default web browser.


## 📂 Project Structure

```
.
├── app.py
├── pages/
│   ├── 1_Home.py
│   ├── 2_Intelligent Lead Scraper copy.py
│   ├── 3_Documentation.py
│   └── 4_About_Me.py
├── data/
│   ├── raw_leads.json
│   └── enriched_leads.json
├── assets/
│   ├── hero.jpg
│   ├── grow.png
│   └── me.jpeg
├── models/
│   └── ranking_model.pkl
├── train_model.py
├── requirements.txt
└── README.md
```

---

## 🛠️ Customization

- **Data**: Replace `raw_leads.json` and `enriched_leads.json` with your own datasets (ensure format consistency).
- **Ranking Logic**: Modify `train_model.py` to adjust how leads are scored, then retrain the model.
- **UI/UX**: Edit `Home.py` and files inside `pages/` to update layout, functionality, or styling.
- **Images**: Customize visuals by replacing images in the `assets/` folder and referencing them in code.



## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request if you'd like to improve Scoutify.



## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.



## 📧 Contact

For questions or more information, you can mail me at siddhaantpahuja@gmail.com.

---
