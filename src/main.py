import time
import requests
from .caspio_client import get_access_token, fetch_pending_orders, update_record, debug_table_info
from .scrapers import scrape_japanpost, scrape_yamato, scrape_sagawa

def main():
    print("🚀 Starting tracking script...")
    try:
        token = get_access_token()
        print("✅ Successfully obtained Caspio access token.")
    except requests.exceptions.RequestException as e:
        print(f"❌ CRITICAL: Could not get Caspio access token. Error: {e}")
        return

    # In thông tin bảng để debug (có thể bật/tắt nếu cần)
    debug_table_info(token)

    try: # <-- THÊM KHỐI TRY Ở ĐÂY
        pending_orders = fetch_pending_orders(token)
    except requests.exceptions.RequestException as e: # <-- BẮT LỖI
        print(f"❌ CRITICAL: Failed to fetch pending orders from Caspio. Error: {e}")
        print("🏁 Exiting script.")
        return
    if not pending_orders:
        print("✅ No pending orders to process. Exiting.")
        return

    print(f"🔍 Found {len(pending_orders)} pending orders. Starting processing...")
    updated_count = 0

    for row in pending_orders:
        rid = "" 
        try:
            rid     = row.get("ID", "Unknown ID")
            tn      = row.get("ma_van_don", "").strip()
            carrier = row.get("don_vi_van_chuyen", "").strip()

            if not tn or not carrier:
                print(f"  ⚠️ Skipping record ID '{rid}' due to missing tracking number or carrier.")
                continue

            print(f"🔄 Processing record ID: '{rid}', Carrier: '{carrier}', Tracking: '{tn}'")

            original_status = ""
            
            # === THAY ĐỔI QUAN TRỌNG NẰM Ở ĐÂY ===
            # Chấp nhận cả "Bưu điện" (tiếng Việt) và "JapanPost" (tiếng Anh)
            if carrier in ["Bưu điện", "JapanPost"]:
                print(f"  Scraping with: Japan Post scraper")
                original_status = scrape_japanpost(tn)
            # ====================================
            
            elif carrier == "Yamato":
                print(f"  Scraping with: Yamato scraper")
                original_status = scrape_yamato(tn)
            elif carrier == "Sagawa":
                print(f"  Scraping with: Sagawa scraper")
                original_status = scrape_sagawa(tn)
            else:
                print(f"  ⚠️ Skipping unknown carrier: '{carrier}'")
                continue

            if original_status:
                update_record(token, rid, original_status)
                updated_count += 1
            else:
                print(f"  ❌ No status found for tracking: '{tn}'")
            
            time.sleep(1.5)

        except requests.exceptions.Timeout:
            print(f"  ‼️ TIMEOUT ERROR for record ID '{rid}'. Moving to the next record.")
            continue
        except requests.exceptions.RequestException as e:
            print(f"  ‼️ NETWORK ERROR for record ID '{rid}': {e}. Moving to the next record.")
            continue
        except Exception as e:
            print(f"  ‼️ UNEXPECTED ERROR for record ID '{rid}': {e.__class__.__name__} - {e}")
            print("  Moving to the next record.")
            continue

    print(f"\n🏁🏁🏁 Process completed! 🏁🏁🏁")
    print(f"  - Total records processed: {len(pending_orders)}")
    print(f"  - Successfully updated: {updated_count}")

if __name__ == "__main__":
    main()
