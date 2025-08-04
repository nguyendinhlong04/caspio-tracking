import time
import requests # Thêm thư viện requests để bắt lỗi
from .caspio_client import get_access_token, fetch_pending_orders, update_record, debug_table_info
from .scrapers import scrape_japanpost, scrape_yamato, scrape_sagawa

def main():
    token = get_access_token()
    debug_table_info(token)

    pending = fetch_pending_orders(token)
    if not pending:
        print("✅ No pending orders.")
        return

    count = 0
    # Sửa đổi bắt đầu từ đây
    for row in pending:
        try:
            rid     = row["ID"]
            tn      = row["ma_van_don"].strip()
            carrier = row["don_vi_van_chuyen"].strip()

            print(f"🔄 Processing record ID: '{rid}', Tracking: '{tn}'")

            st = ""
            if carrier == "Bưu điện":
                st = scrape_japanpost(tn)
            elif carrier == "Yamato":
                st = scrape_yamato(tn)
            elif carrier == "Sagawa":
                st = scrape_sagawa(tn)
            else:
                print(f"  ⚠️ Skipping unknown carrier: '{carrier}'")
                continue # Bỏ qua và sang record tiếp theo

            if st:
                print(f"  ➡️ Found status: '{st}'. Attempting update.")
                update_record(token, rid, st)
                count += 1
            else:
                print(f"  ❌ No status found for tracking: '{tn}'")
            
            time.sleep(1)

        # Bắt lỗi timeout hoặc các lỗi kết nối khác
        except requests.exceptions.RequestException as e:
            print(f"  ‼️ NETWORK ERROR for record ID '{rid}': {e}")
            print("  Moving to the next record.")
            continue # Bỏ qua record lỗi và tiếp tục
        # Bắt các lỗi không mong muốn khác
        except Exception as e:
            print(f"  ‼️ UNEXPECTED ERROR for record ID '{rid}': {e}")
            print("  Moving to the next record.")
            continue # Bỏ qua record lỗi và tiếp tục
    # Kết thúc sửa đổi

    print(f"🏁 Completed: {count}/{len(pending)} updated")

if __name__ == "__main__":
    main()
