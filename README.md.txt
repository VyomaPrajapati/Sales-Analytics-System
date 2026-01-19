
# Sales Data Analytics System

A comprehensive Python-based system designed to process, clean, and analyze e-commerce sales transactions. This system integrates with external APIs for data enrichment and generates detailed business intelligence reports.

## 🚀 Features

- **Robust Data Cleaning:**
  - Handles non-UTF-8 file encoding (UTF-8, Latin-1, CP1252).
  - Removes invalid records (missing IDs, non-positive quantities/prices).
  - Cleans messy formatting (removes commas from product names and numeric strings).
- **Interactive User Experience:**
  - Console-based menu allowing users to filter data by Region and Transaction Amount.
- **Advanced Data Analytics:**
  - Total Revenue and Average Order Value calculations.
  - Region-wise performance analysis with percentage distributions.
  - Top 5 best-selling products and top customer spending analysis.
  - Daily sales trends and identification of peak sales days.
- **API Integration:**
  - Fetches real-time product metadata from the [DummyJSON API](https://dummyjson.com).
  - Performs data enrichment by mapping local Product IDs to API categories, brands, and ratings.
- **Automated Reporting:**
  - Generates a formatted `sales_report.txt` with tables and summaries.
  - Exports enriched data to `enriched_sales_data.txt`.

## 📁 Project Structure
                      
sales-analytics-system/
  ├── README.md                       # Project documentation
  ├── main.py                         # Main execution script and CLI
  ├── utils/                          # Modular logic components
  │   ├── file_handler.py             # File I/O and encoding logic
  │   ├── data_processor.py           # Cleaning, analytics, and reporting
  │   └── api_handler.py              # API communication and mapping
  ├── data/                             # Input and enriched output files
  │   └── sales_data.txt (provided)
  ├── output/                            # Generated analytical reports
  └── requirements.txt
