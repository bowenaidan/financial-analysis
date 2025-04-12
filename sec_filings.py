import requests
import argparse
import pandas as pd

SEC_BASE = "https://data.sec.gov"
HEADERS = {"User-Agent": "Aidan Bowen rivott35@hotmail.com"}

def get_cik(ticker):
    """Get the CIK for a given ticker"""
    url = f"https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    for entry in data.values():
        if entry['ticker'].lower() == ticker.lower():
            return str(entry['cik_str']).zfill(10)
    raise ValueError("Ticker not found")

def get_filings(cik, form_type, count=5):
    """Fetch recent filings metadata for a CIK"""
    url = f"{SEC_BASE}/submissions/CIK{cik}.json"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    filings = data.get("filings", {}).get("recent", {})
    
    df = pd.DataFrame(filings)
    df = df[df['form'] == form_type.upper()]
    return df.head(count)

def show_filings(df, cik):
    """Print basic info and construct filing URLs"""
    for i, row in df.iterrows():
        accession = row['accessionNumber'].replace('-', '')
        url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/index.json"
        print(f"\n{row['form']} - {row['filingDate']}")
        print(f"Link: https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/")
        print(f"Primary Document: {row['primaryDocument']}")

def main():
    parser = argparse.ArgumentParser(description="SEC Filing Fetcher")
    parser.add_argument("ticker", help="Company ticker symbol (e.g., AAPL)")
    parser.add_argument("-f", "--form", default="10-K", help="Form type (e.g., 10-K, 10-Q, 8-K, 4, SC 13D)")
    parser.add_argument("-n", "--num", type=int, default=5, help="Number of filings to show (default: 5)")
    args = parser.parse_args()

    try:
        cik = get_cik(args.ticker)
        df = get_filings(cik, args.form, args.num)
        if df.empty:
            print(f"No {args.form} filings found for {args.ticker.upper()}")
        else:
            show_filings(df, cik)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
