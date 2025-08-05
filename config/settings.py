import os
from dotenv import load_dotenv

load_dotenv()  

CLIENT_ID       = os.getenv("CLIENT_ID")
CLIENT_SECRET   = os.getenv("CLIENT_SECRET")
DEPLOY_URL      = os.getenv("DEPLOY_URL")
TABLE_NAME      = os.getenv("TABLE_NAME", "DonHang")
MAX_RECORDS     = int(os.getenv("MAX_RECORDS") or 500)

STATUS_MAPPING = {
    "差出人に返送": "Thất bại - Hoàn hàng",
    "差出人に返送済み": "Thất bại - Hoàn hàng",
    "ご不在": "Vắng nhà",
    "ご不在のため持ち戻り": "Vắng nhà",
    "持戻（ご不在）": "Vắng nhà",
    "お問合せ": "Lỗi",
    "調査中": "Lỗi",
    "お届け先にお届け済み": "Thành công",
    "窓口でお渡し": "Thành công",
    "配達完了": "Thành công",
    "持ち出し中": "Đang giao",
    "引受": "Đang vận chuyển",
    "到着": "Đang vận chuyển",
    "中継": "Đang vận chuyển",
    "配達希望受付": "Chờ giao",
    "保管": "Lưu kho"

}
