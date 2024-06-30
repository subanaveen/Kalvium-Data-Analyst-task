import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_page(soup):
    data = []
    tbl = soup.find_all('table')
    for table in tbl:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all(['td', 'th'])
            cols = [col.text.strip() for col in cols if col.text.strip()]
            if cols:
                data.append(cols)
    return data

def scrp_web(url):
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    data = scrape_page(soup)
    
    if not data:
        raise ValueError("No data found!")
    
    cols = ["Party", "Won", "Leading", "Total"]
    df = pd.DataFrame(data[1:], columns=cols)
    
    print("Scraped DataFrame head:")
    print(df.head())
    
    df['Won']     = pd.to_numeric(df['Won'], errors='coerce')
    df['Leading'] = pd.to_numeric(df['Leading'], errors='coerce')
    df['Total']   = pd.to_numeric(df['Total'], errors='coerce')
    
    total_seats = df['Total'].sum()
    df['Seat %'] = df['Won'] / total_seats * 100
    
    return df

def create_csv(df, filename):
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def insight_analyze(df):
    insi = []
    
    total_seats = df['Total'].sum()
    insi.append(f"Total seats: {total_seats}")
    
    maj_party     = df.loc[df['Won'].idxmax()]['Party']
    maj_seat     = int(df.loc[df['Won'].idxmax()]['Won'])
    insi.append(f"Party with majority vote: {maj_party}, {maj_seat} seats")
    
    sorted_df          = df.sort_values(by='Won', ascending=False)
    sec_par       = sorted_df.iloc[1]['Party']
    sec_seat       = int(sorted_df.iloc[1]['Won'])
    insi.append(f"Party with second majority: {sec_par}, {sec_seat} seats")
    
    lead_par      = df.loc[df['Leading'].idxmax()]['Party']
    lead_con = int(df.loc[df['Leading'].idxmax()]['Leading'])
    insi.append(f"Party leading in most constituencies: {lead_par}, {lead_con} constituencies")
    
    min_par   = df[df['Won'] == 1.0]['Party'].tolist()
    min_lead      = ", ".join(min_par)
    insi.append(f"Minority parties: {min_lead}")
    
    max_per = df.loc[df['Seat %'].idxmax()]['Party']
    hi_par = df.loc[df['Seat %'].idxmax()]['Seat %']
    insi.append(f"Party with highest % seats won: {max_per}, {hi_par:.2f}%")
    
    s_per = df.sort_values(by='Seat %', ascending=False)
    sec_par_p = s_per.iloc[1]['Party']
    sec_per_party = s_per.iloc[1]['Seat %']
    insi.append(f"Party with second highest % seats won: {sec_par_p}, {sec_per_party:.2f}%")
    
    top2_par = sorted_df.iloc[:2]['Party'].tolist()
    insi.append(f"Competitive parties: {', '.join(top2_par)}")
    
    main_par = df[(df['Seat %'] > 1) & (df['Party'] != maj_party)]['Party'].tolist()
    insi.append(f"Parties that may impact results: {', '.join(main_par)}")
    
    bjp_S = df[df['Party'] == 'Bharatiya Janata Party - BJP']['Won'].values[0]
    inc_s = df[df['Party'] == 'Indian National Congress - INC']['Won'].values[0]
    required_seats = bjp_S - inc_s + 1
    
    op_s = df[(df['Party'] != 'Bharatiya Janata Party - BJP') & 
                       (df['Party'] != 'Indian National Congress - INC')].sort_values(by='Won', ascending=False)
    
    allies = 0
    al_par = []
    for _, row in op_s.iterrows():
        allies += row['Won']
        al_par.append(row['Party'])
        if allies + inc_s >= bjp_S:
            break
    
    insi.append(f"Minimum parties Congress needs to beat BJP: {', '.join(al_par)}")
    
    return insi

def crete_ins(insi, filename):
    with open(filename, 'w') as f:
        for idx, insight in enumerate(insi, start=1):
            f.write(f"{idx}. {insight}\n")
    print(f"Analysis and insi written to {filename}")

if __name__ == "__main__":
    url = "https://results.eci.gov.in/PcResultGenJune2024/index.htm#"
    
    try:
        df = scrp_web(url)
        print("Data scraping successfully done!")
        
        create_csv(df, 'election_res.csv')
        
        insi = insight_analyze(df)
        
        crete_ins(insi, 'election_res_report.txt')
        
    except Exception as e:
        print(f"An error occurred: {e}")
