import requests

from config.settings import CLIENT_ID, CLIENT_SECRET, DEPLOY_URL, TABLE_NAME, MAX_RECORDS

def get_access_token() -> str:
    r = requests.post(
        f"{DEPLOY_URL}/oauth/token",
        data={"grant_type":"client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET),
        timeout=10
    )
    r.raise_for_status()
    return r.json()["access_token"]

def fetch_pending_orders(token: str):
    url = f"{DEPLOY_URL}/rest/v2/tables/{TABLE_NAME}/records"
    params = {
        "response": "rows",
        "q.select": "ID,ma_van_don,don_vi_van_chuyen,tinh_trang_van_chuyen",  
        "q.where": (
            "tinh_trang_van_chuyen IS NULL OR "
            "tinh_trang_van_chuyen = '' OR "
            "tinh_trang_van_chuyen NOT IN "
            "('Thành công','Thất bại - Hoàn hàng')"
        ),
        "q.limit": str(MAX_RECORDS)  
    }
    r = requests.get(url, headers={"Authorization":f"Bearer {token}"}, params=params, timeout=15)
    r.raise_for_status()
    result = r.json().get("Result", [])
    
    # Thêm dòng log này
    print(f"✅ Fetched {len(result)} pending records from Caspio.")
    
    return result

def update_record(token: str, record_id: str, status: str):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "tinh_trang_van_chuyen": status
    }
    
    print(f"  Attempting to update record ID: '{record_id}'")
    
    try:
        url = f"{DEPLOY_URL}/rest/v2/tables/{TABLE_NAME}/records"
        params = {
            "q.where": f"ID='{record_id}'"
        }
        print(f"  Trying with ID field: {url}?{requests.compat.urlencode(params)}")
        resp = requests.put(url, headers=headers, params=params, json=payload, timeout=10)
        resp.raise_for_status()
        print(f"  ✅ Method 1 (ID field) succeeded")
        return
    except requests.exceptions.HTTPError as e:
        print(f"  Method 1 failed: {e.response.status_code}")
        print(f"  Response: {e.response.text[:200]}")

def debug_table_info(token: str):
    print("🔍 Debugging table structure...")
    
    try:
        url = f"{DEPLOY_URL}/rest/v2/tables/{TABLE_NAME}"
        resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        resp.raise_for_status()
        print(f"✅ Table metadata retrieved successfully")
        metadata = resp.json()
        print(f"  Table name: {metadata.get('Name', 'Unknown')}")
        
        fields = metadata.get('Fields', [])
        print(f"  Fields ({len(fields)}):")
        for field in fields[:5]:  
            print(f"    - {field.get('Name', 'Unknown')} ({field.get('Type', 'Unknown')})")
        
        id_field = next((f for f in fields if f.get('Name') == 'id'), None)
        if id_field:
            print(f"  ID field found: {id_field}")
        else:
            print(f"  ⚠️  No 'id' field found in table metadata")
            
    except Exception as e:
        print(f"❌ Failed to get table metadata: {e}")
    
    try:
        url = f"{DEPLOY_URL}/rest/v2/tables/{TABLE_NAME}/records"
        params = {"q.limit": "1", "response": "rows"}
        resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params, timeout=10)
        resp.raise_for_status()
        sample_data = resp.json()
        
        if sample_data.get('Result'):
            sample_record = sample_data['Result'][0]
            print(f"✅ Sample record structure:")
            for key, value in sample_record.items():
                print(f"    {key}: {type(value).__name__} = {str(value)[:50]}")
        else:
            print("  No sample records found")
            
    except Exception as e:
        print(f"❌ Failed to get sample record: {e}")
