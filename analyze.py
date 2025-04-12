import xml.etree.ElementTree as ET
import pandas as pd
import argparse
import os
import urllib.request

NAMESPACE = {'ns': 'http://www.sec.gov/edgar/document/thirteenf/informationtable'}

def download_xml(url):
    with urllib.request.urlopen(url) as response:
        return response.read()

def parse_xml(xml_content):
    tree = ET.ElementTree(ET.fromstring(xml_content))
    root = tree.getroot()
    data = []
    for info_table in root.findall('.//ns:infoTable', NAMESPACE):
        row = {child.tag.split('}')[-1]: child.text for child in info_table}
        data.append(row)
    return pd.DataFrame(data)

def filter_dataframe(df):
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    return df

def print_info(df, top_n, position_type=None):
    print("DataFrame:")
    print(df)
    print("\nColumn Names:")
    print(df.columns)
    print("\nTotal Value:")
    print(df['value'].astype(int).sum())
    print("\nCount of Rows:")
    print(len(df))

    if 'putCall' in df.columns:
        if position_type in ['Put', 'Call']:
            df = df[df['putCall'] == position_type]
            print(f"\nFiltered to {position_type} Positions Only:")
        elif position_type is None:
            df = df[df['putCall'].isna()]
            print("\nFiltered to Regular (Non-Derivative) Positions Only:")
    else:
        print("\nNo 'putCall' column found — assuming all are regular positions.")

    top_positions = df.nlargest(top_n, 'value')
    print(f"\nTop {top_n} Positions by Value ({'All' if not position_type else position_type} Holdings):")
    print(top_positions[['nameOfIssuer', 'value'] + (['putCall'] if 'putCall' in top_positions.columns else [])])

def main():
    parser = argparse.ArgumentParser(description='Analyze 13F XML file')
    parser.add_argument('-u', '--url', default=None, help='URL of the 13F XML file')
    parser.add_argument('-n', '--top-positions', type=int, default=20, help='Number of top positions to display (default: 20)')
    parser.add_argument('-t', '--type', choices=['Put', 'Call', 'All'], default='All', help='Filter by position type: Put, Call, or All (default: All)')
    args = parser.parse_args()

    url = args.url
    if url is None:
        url = input("Please enter the URL of the 13F XML file: ")

    xml_content = download_xml(url)
    df = parse_xml(xml_content)
    df = filter_dataframe(df)

    position_type = None if args.type == 'All' else args.type
    print_info(df, args.top_positions, position_type)

if __name__ == '__main__':
    main()
