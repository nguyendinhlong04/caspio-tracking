import time
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
    for row in pending:
        rid     = row["ID"]
        tn      = row["ma_van_don"].strip()
        carrier = row["don_vi_van_chuyen"].strip()

        if carrier == "Bưu điện":
            st = scrape_japanpost(tn)
        elif carrier == "Yamato":
            st = scrape_yamato(tn)
        elif carrier == "Sagawa":
            st = scrape_sagawa(tn)
        else:
            continue

        if st:
            update_record(token, rid, st)
            count += 1
        time.sleep(1)

    print(f"🏁 Completed: {count}/{len(pending)} updated")

if __name__ == "__main__":
    main()
