import os
from datetime import datetime

def parse_transactions(raw_lines):
    """Parses raw lines into a clean list of dictionaries."""
    parsed_data = []
    for line in raw_lines:
        parts = line.split('|')
        if len(parts) != 8:
            continue
        try:
            product_name = parts[3].replace(',', ' ')
            qty_str = parts[4].replace(',', '')
            price_str = parts[5].replace(',', '')

            transaction = {
                'TransactionID': parts[0].strip(),
                'Date':          parts[1].strip(),
                'ProductID':     parts[2].strip(),
                'ProductName':   product_name.strip(),
                'Quantity':      int(qty_str),
                'UnitPrice':     float(price_str),
                'CustomerID':    parts[6].strip(),
                'Region':        parts[7].strip()
            }
            parsed_data.append(transaction)
        except ValueError:
            continue
    return parsed_data

def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """Validates transactions and applies optional filters."""
    valid_after_rules = []
    invalid_count = 0
    for tx in transactions:
        is_valid = True
        if not tx['TransactionID'].startswith('T'): is_valid = False
        if not tx['ProductID'].startswith('P'): is_valid = False
        if not tx['CustomerID'].startswith('C'): is_valid = False
        if tx['Quantity'] <= 0: is_valid = False
        if tx['UnitPrice'] <= 0: is_valid = False
        if not tx['CustomerID'] or not tx['Region']: is_valid = False
        
        if is_valid:
            valid_after_rules.append(tx)
        else:
            invalid_count += 1

    filtered_list = valid_after_rules
    if region:
        filtered_list = [t for t in filtered_list if t['Region'] == region]
    if min_amount is not None:
        filtered_list = [t for t in filtered_list if (t['Quantity'] * t['UnitPrice']) >= min_amount]
    if max_amount is not None:
        filtered_list = [t for t in filtered_list if (t['Quantity'] * t['UnitPrice']) <= max_amount]

    summary = {'total_input': len(transactions), 'invalid': invalid_count, 'final_count': len(filtered_list)}
    return filtered_list, invalid_count, summary

def calculate_total_revenue(transactions):
    """Calculates sum of (Quantity * UnitPrice) for all transactions."""
    return sum(t['Quantity'] * t['UnitPrice'] for t in transactions)

def region_wise_sales(transactions):
    """Analyzes sales and transaction counts per region."""
    stats = {}
    total_rev = calculate_total_revenue(transactions)
    for t in transactions:
        region = t['Region']
        rev = t['Quantity'] * t['UnitPrice']
        if region not in stats: stats[region] = {'total_sales': 0.0, 'transaction_count': 0}
        stats[region]['total_sales'] += rev
        stats[region]['transaction_count'] += 1
    for region in stats:
        stats[region]['percentage'] = round((stats[region]['total_sales'] / total_rev) * 100, 2)
    return dict(sorted(stats.items(), key=lambda item: item[1]['total_sales'], reverse=True))

def top_selling_products(transactions, n=5):
    """Finds top n products by total quantity sold."""
    product_data = {}
    for t in transactions:
        name = t['ProductName']
        if name not in product_data: product_data[name] = {'qty': 0, 'rev': 0.0}
        product_data[name]['qty'] += t['Quantity']
        product_data[name]['rev'] += (t['Quantity'] * t['UnitPrice'])
    result = [(name, data['qty'], data['rev']) for name, data in product_data.items()]
    result.sort(key=lambda x: x[1], reverse=True)
    return result[:n]

def customer_analysis(transactions):
    """Analyzes spending and purchase frequency per customer."""
    cust_stats = {}
    for t in transactions:
        cid = t['CustomerID']
        if cid not in cust_stats: cust_stats[cid] = {'total_spent': 0.0, 'purchase_count': 0, 'products_bought': set()}
        cust_stats[cid]['total_spent'] += (t['Quantity'] * t['UnitPrice'])
        cust_stats[cid]['purchase_count'] += 1
        cust_stats[cid]['products_bought'].add(t['ProductName'])
    for cid in cust_stats:
        cust_stats[cid]['avg_order_value'] = round(cust_stats[cid]['total_spent'] / cust_stats[cid]['purchase_count'], 2)
        cust_stats[cid]['products_bought'] = sorted(list(cust_stats[cid]['products_bought']))
    return dict(sorted(cust_stats.items(), key=lambda x: x[1]['total_spent'], reverse=True))

def low_performing_products(transactions, threshold=10):
    """Identifies products sold less than the threshold."""
    product_data = {}
    for t in transactions:
        name = t['ProductName']
        if name not in product_data: product_data[name] = {'qty': 0}
        product_data[name]['qty'] += t['Quantity']
    low_perf = [(name, d['qty']) for name, d in product_data.items() if d['qty'] < threshold]
    low_perf.sort(key=lambda x: x[1])
    return low_perf

def daily_sales_trend(transactions):
    """Groups revenue and unique customer counts by date."""
    trend = {}
    for t in transactions:
        date = t['Date']
        if date not in trend: trend[date] = {'revenue': 0.0, 'transaction_count': 0, 'unique_customers': set()}
        trend[date]['revenue'] += (t['Quantity'] * t['UnitPrice'])
        trend[date]['transaction_count'] += 1
        trend[date]['unique_customers'].add(t['CustomerID'])
    
    final_trend = {}
    for d in sorted(trend.keys()):
        final_trend[d] = {
            'revenue': round(trend[d]['revenue'], 2),
            'transaction_count': trend[d]['transaction_count'],
            'unique_customers': len(trend[d]['unique_customers'])
        }
    return final_trend

def find_peak_sales_day(transactions):
    """Returns the date with the highest total revenue."""
    trend = daily_sales_trend(transactions)
    if not trend: return None
    peak_date = max(trend, key=lambda d: trend[d]['revenue'])
    return (peak_date, trend[peak_date]['revenue'], trend[peak_date]['transaction_count'])

def enrich_sales_data(transactions, product_mapping):
    """Adds API-fetched metadata to transaction records."""
    enriched_list = []
    for tx in transactions:
        enriched_tx = tx.copy()
        try:
            prod_id_num = int(tx['ProductID'][1:])
        except:
            prod_id_num = -1
            
        if prod_id_num in product_mapping:
            info = product_mapping[prod_id_num]
            enriched_tx.update({
                'API_Category': info['category'], 
                'API_Brand': info['brand'], 
                'API_Rating': info['rating'], 
                'API_Match': True
            })
        else:
            enriched_tx.update({
                'API_Category': None, 
                'API_Brand': None, 
                'API_Rating': None, 
                'API_Match': False
            })
        enriched_list.append(enriched_tx)
    return enriched_list

def save_enriched_data(enriched_transactions, filename='data/enriched_sales_data.txt'):
    """Saves enriched data to a pipe-delimited text file."""
    headers = ["TransactionID", "Date", "ProductID", "ProductName", "Quantity", "UnitPrice", "CustomerID", "Region", "API_Category", "API_Brand", "API_Rating", "API_Match"]
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("|".join(headers) + "\n")
        for tx in enriched_transactions:
            row = [str(tx.get(h, "None")) for h in headers]
            f.write("|".join(row) + "\n")
    print(f"Enriched data saved to {filename}")

def generate_sales_report(transactions, enriched_transactions, output_file='output/sales_report.txt'):
    """Generates a comprehensive formatted text report file."""
    
    # 1. Ensure the output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 2. Gather data for the report
    total_rev = calculate_total_revenue(transactions)
    total_tx = len(transactions)
    avg_order = total_rev / total_tx if total_tx > 0 else 0
    dates = [t['Date'] for t in transactions]
    date_range = f"{min(dates)} to {max(dates)}" if dates else "N/A"
    
    reg_stats = region_wise_sales(transactions)
    top_prods = top_selling_products(transactions, n=5)
    trend = daily_sales_trend(transactions)
    peak_day, peak_rev, _ = find_peak_sales_day(transactions)
    low_prods = low_performing_products(transactions, threshold=10)
    
    # API Enrichment Stats
    total_enriched = sum(1 for t in enriched_transactions if t['API_Match'])
    success_rate = (total_enriched / len(enriched_transactions) * 100) if enriched_transactions else 0
    failed_products = sorted(list(set(t['ProductName'] for t in enriched_transactions if not t['API_Match'])))

    # 3. Build the report content
    report = []
    report.append("="*60)
    report.append(" " * 20 + "SALES ANALYTICS REPORT")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Records Processed: {len(transactions)}")
    report.append("="*60 + "\n")

    report.append("OVERALL SUMMARY")
    report.append("-" * 30)
    report.append(f"Total Revenue:       ${total_rev:,.2f}")
    report.append(f"Total Transactions:  {total_tx}")
    report.append(f"Average Order Value: ${avg_order:,.2f}")
    report.append(f"Date Range:          {date_range}\n")

    report.append("REGION-WISE PERFORMANCE")
    report.append("-" * 60)
    report.append(f"{'Region':<12} {'Sales':<15} {'% of Total':<12} {'Transactions'}")
    for reg, data in reg_stats.items():
        report.append(f"{reg:<12} ${data['total_sales']:<14,.2f} {data['percentage']:<12}% {data['transaction_count']}")
    
    report.append("\nTOP 5 PRODUCTS")
    report.append("-" * 60)
    report.append(f"{'Rank':<5} {'Product Name':<25} {'Qty Sold':<10} {'Revenue'}")
    for i, (name, qty, rev) in enumerate(top_prods, 1):
        report.append(f"{i:<5} {name:<25} {qty:<10} ${rev:,.2f}")

    report.append("\nDAILY SALES TREND")
    report.append("-" * 60)
    report.append(f"{'Date':<15} {'Revenue':<15} {'Orders':<10} {'Unique Customers'}")
    for date, data in trend.items():
        report.append(f"{date:<15} ${data['revenue']:<14,.2f} {data['transaction_count']:<10} {data['unique_customers']}")

    report.append("\nPRODUCT PERFORMANCE ANALYSIS")
    report.append("-" * 30)
    report.append(f"Best Selling Day:  {peak_day} (${peak_rev:,.2f})")
    report.append(f"Low Performers:    {', '.join([p[0] for p in low_prods]) if low_prods else 'None'}")
    
    report.append("\nAPI ENRICHMENT SUMMARY")
    report.append("-" * 30)
    report.append(f"Total Products Enriched: {total_enriched}")
    report.append(f"Success Rate:            {success_rate:.1f}%")
    if failed_products:
        report.append(f"Unmatched Products:      {', '.join(failed_products[:5])}...")

    # 4. Write to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(report))
        return True
    except Exception as e:
        print(f"Error writing report: {e}")
        return False