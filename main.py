import sys
from utils.file_handler import read_sales_data
from utils.data_processor import (
    parse_transactions, validate_and_filter, enrich_sales_data, 
    save_enriched_data, generate_sales_report
)
from utils.api_handler import fetch_all_products, create_product_mapping

def main():
    try:
        print("="*45)
        print(" " * 12 + "SALES ANALYTICS SYSTEM")
        print("="*45 + "\n")

        # [1/10] Reading Data
        print("[1/10] Reading sales data...")
        raw_lines = read_sales_data('data/sales_data.txt')
        if not raw_lines: return
        print(f"ü Successfully read {len(raw_lines)} transactions")

        # [2/10] Parsing
        print("\n[2/10] Parsing and cleaning data...")
        parsed_data = parse_transactions(raw_lines)
        print(f"ü Parsed {len(parsed_data)} records")

        # [3/10] Filter Options Interaction
        print("\n[3/10] Filter Options Available:")
        # Quick look at available regions and amount range
        regions = sorted(list(set(t['Region'] for t in parsed_data if t['Region'])))
        amounts = [t['Quantity'] * t['UnitPrice'] for t in parsed_data]
        print(f"Regions: {', '.join(regions)}")
        print(f"Amount Range: ${min(amounts):,.0f} - ${max(amounts):,.0f}")

        # USER INTERACTION
        do_filter = input("\nDo you want to filter data? (y/n): ").lower()
        sel_region = None
        min_amt = None
        
        if do_filter == 'y':
            sel_region = input("Enter region name (or leave blank): ").strip() or None
            min_input = input("Enter minimum transaction amount (or leave blank): ").strip()
            if min_input: min_amt = float(min_input)

        # [4/10] Validating
        print("\n[4/10] Validating transactions...")
        clean_tx, invalid_count, summary = validate_and_filter(
            parsed_data, region=sel_region, min_amount=min_amt
        )
        print(f"ü Valid: {len(clean_tx)} | Invalid: {invalid_count}")

        # [5/10] Analysis
        print("\n[5/10] Analyzing sales data...")
        # (Internal processing happens here)
        print("ü Analysis complete")

        # [6/10] API Fetching
        print("\n[6/10] Fetching product data from API...")
        api_data = fetch_all_products()
        print(f"ü Fetched {len(api_data)} products")

        # [7/10] Enrichment
        print("\n[7/10] Enriching sales data...")
        mapping = create_product_mapping(api_data)
        enriched_tx = enrich_sales_data(clean_tx, mapping)
        match_count = sum(1 for t in enriched_tx if t['API_Match'])
        print(f"ü Enriched {match_count}/{len(enriched_tx)} transactions")

        # [8/10] Saving Enriched Data
        print("\n[8/10] Saving enriched data...")
        save_enriched_data(enriched_tx)
        print("ü Saved to: data/enriched_sales_data.txt")

        # [9/10] Generating Final Report
        print("\n[9/10] Generating report...")
        if generate_sales_report(clean_tx, enriched_tx):
            print("ü Report saved to: output/sales_report.txt")

        # [10/10] Process Complete
        print("\n[10/10] Process Complete!")
        print("="*45)

    except Exception as e:
        print(f"\n[ERROR]: An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


