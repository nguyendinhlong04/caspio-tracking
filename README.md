# Caspio Tracking Sync

**Mô tả**: Scrape tình trạng vận đơn từ Japan Post, Yamato, Sagawa, rồi update vào Caspio.

## Thiết lập

1. Copy `.env.example` → `.env`, điền `CLIENT_ID`, `CLIENT_SECRET`, `DEPLOY_URL`,…
2. Commit code và push lên GitHub.
3. Vào `Settings → Secrets → Actions`, tạo secrets tương ứng.
4. Workflow sẽ tự chạy theo cron, hoặc bạn có thể trigger thủ công.

## Cấu trúc

- `config/settings.py`: load biến môi trường  
- `src/`: mã chính, tách rõ client & scraper  
- `.github/workflows/`: workflow chạy theo lịch  
