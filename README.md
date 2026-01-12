# ⚽ Pro Player Analysis Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://YOUR-APP-LINK-HERE.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Library](https://img.shields.io/badge/Library-Mplsoccer-green?style=for-the-badge)](https://mplsoccer.readthedocs.io/en/latest/)

## 📋 Overview
This project is an advanced **Football Player Analysis Dashboard** built with **Python** and **Streamlit**. It transforms raw event data (SofaScore JSONs) into interactive, professional-grade visualizations used in modern football analytics.

The dashboard provides scouts and analysts with deep insights into player performance, including passing networks, shot maps, defensive actions, and heatmaps.

## 🚀 Key Features
* **Interactive Visualizations:**
    * **Pass Maps:** Filter by outcome, progression, key passes, and crosses.
    * **Shot Maps:** Accurate coordinate calibration for goals, misses, and saves.
    * **Heatmaps:** Density plots to visualize player positioning and movement.
    * **Defensive Maps:** Tacking tackles, interceptions, and clearances.
* **Advanced Metrics:**
    * Calculation of **Progressive Passes** based on distance gain.
    * Dynamic KPI Cards for quick stats (Goals, Assists, Pass Accuracy, etc.).
* **Coordinate System Calibration:** Custom logic to correct and map raw data coordinates to `mplsoccer` pitch dimensions.
* **Video Integration:** Embedded match highlights synchronized with statistical analysis.

## 🛠️ Tech Stack
* **Frontend:** [Streamlit](https://streamlit.io/)
* **Data Processing:** [Pandas](https://pandas.pydata.org/)
* **Visualization:** [Matplotlib](https://matplotlib.org/) & [Mplsoccer](https://mplsoccer.readthedocs.io/)
* **Data Source:** JSON Event Data (SofaScore format)

## 📂 Project Structure
```text
├── app.py                 # Main application code
├── requirements.txt       # Python dependencies
├── shot.json              # Shot event data
├── raphinha_data.json     # Player event data
├── raphina_stats.json     # General statistics
└── raphinha.mp4       # Video highlights


## 🔧 Installation & Usage
Clone the repository:

Bash

git clone [https://github.com/abdelati88/raphinha-analysis-dashboard.git](https://github.com/abdelati88/raphinha-analysis-dashboard.git)
cd raphinha-analysis-dashboard
Install dependencies:

Bash

pip install -r requirements.txt
Run the app:

Bash

streamlit run app.py
