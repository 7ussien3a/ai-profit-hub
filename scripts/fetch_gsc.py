import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
KEY_FILE_LOCATION = 'scripts/service-account.json'

def main():
    # Authenticate
    credentials = service_account.Credentials.from_service_account_file(
        KEY_FILE_LOCATION,
        scopes=SCOPES,
    )
    service = build('searchconsole', 'v1', credentials=credentials)
    
    # Try different site URL formats just in case
    site_url = 'https://ai-profit-hub.com/'
    
    end_date = datetime.date.today() - datetime.timedelta(days=1) # GSC is usually delayed by 1-2 days
    start_date = end_date - datetime.timedelta(days=6) # 7 days total
    
    print(f"Fetching data for {site_url} from {start_date} to {end_date}")
    
    try:
        # Total Stats
        request_totals = {
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
        }
        totals_response = service.searchanalytics().query(siteUrl=site_url, body=request_totals).execute()
        
        print("\n=== WEEKLY TOTALS ===")
        if 'rows' in totals_response:
            row = totals_response['rows'][0]
            print(f"Impressions: {row['impressions']}")
            print(f"Clicks:      {row['clicks']}")
            print(f"CTR:         {row['ctr']*100:.2f}%")
            print(f"Avg Position:{row['position']:.2f}")
        else:
            print("No data found for totals.")
            
        # Top Queries
        request_queries = {
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'dimensions': ['query'],
            'rowLimit': 10
        }
        queries_response = service.searchanalytics().query(siteUrl=site_url, body=request_queries).execute()
        
        print("\n=== TOP QUERIES ===")
        if 'rows' in queries_response:
            for row in queries_response['rows']:
                print(f"{row['keys'][0]} - Clicks: {row['clicks']} | Imp: {row['impressions']} | Pos: {row['position']:.1f}")
        
        # Top Pages
        request_pages = {
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'dimensions': ['page'],
            'rowLimit': 10
        }
        pages_response = service.searchanalytics().query(siteUrl=site_url, body=request_pages).execute()
        
        print("\n=== TOP PAGES ===")
        if 'rows' in pages_response:
            for row in pages_response['rows']:
                print(f"{row['keys'][0]} - Clicks: {row['clicks']} | Imp: {row['impressions']} | Pos: {row['position']:.1f}")
                
    except Exception as e:
        print("API Error:", e)

if __name__ == '__main__':
    main()
