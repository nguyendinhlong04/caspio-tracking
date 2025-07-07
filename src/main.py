import time
from caspio_client import get_access_token, fetch_pending_orders, update_record, debug_table_info
import scrapers

def main():
    token = get_access_token()
    debug_table_info(token)

    pending = fetch_pending_orders(token)
    if not pending:
        print("✅ No pending orders."); return

    now = time.strftime("%Y-%m-%d %H:%M:%S")
    count = 0
    for row in pending:
        rid = row["ID"]; tn = row["ma_van_don"].strip(); carrier = row["don_vi_van_chuyen"].strip()
        if carrier == "Bưu điện":
            st = scrapers.scrape_japanpost(tn)
        elif carrier == "Yamato":
            st = scrapers.scrape_yamato(tn)
        elif carrier == "Sagawa":
            st = scrapers.scrape_sagawa(tn)
        else:
            continue

        if st:
            update_record(token, rid, st)
            count += 1
        time.sleep(1)

    print(f"🏁 Completed: {count}/{len(pending)} updated")

if __name__ == "__main__":
    main()
