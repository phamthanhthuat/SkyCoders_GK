
import copy
import json
import os
import shutil
import unicodedata
from decimal import Decimal, ROUND_HALF_UP

# File JSON nằm cùng thư mục với file .py này
DUONG_DAN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "sinh_vien.json")

TRONG_SO_TP1 = Decimal("0.4")   # Điểm thành phần 1: 40%
TRONG_SO_TP2 = Decimal("0.6")   # Điểm thành phần 2: 60%

def lam_tron(so, so_chu_so_thap_phan):
    """Làm tròn kiểu thông thường (0.05 -> 0.1), tránh lỗi số thực của round()."""
    mau = Decimal(1).scaleb(-so_chu_so_thap_phan)      # 0.1 hoặc 0.01
    return float(Decimal(str(so)).quantize(mau, rounding=ROUND_HALF_UP))

def tinh_diem_mon(diem_tp1, diem_tp2):
    """Điểm môn = Điểm 40% x 0.4 + Điểm 60% x 0.6 (lấy 1 chữ số thập phân)."""
    tong = Decimal(str(diem_tp1)) * TRONG_SO_TP1 + Decimal(str(diem_tp2)) * TRONG_SO_TP2
    return lam_tron(tong, 1)

def tinh_gpa(danh_sach_mon):
    """GPA = trung bình cộng điểm tổng kết các môn (lấy 2 chữ số thập phân)."""
    if not danh_sach_mon:
        return 0.0
    tong = sum(Decimal(str(m["diem_tong_ket"])) for m in danh_sach_mon)
    return lam_tron(tong / len(danh_sach_mon), 2)

def bo_dau(chuoi):
    chuoi = chuoi.replace("đ", "d").replace("Đ", "D")
    chuoi = unicodedata.normalize("NFD", chuoi)
    chuoi = "".join(c for c in chuoi if unicodedata.category(c) != "Mn")
    return chuoi.lower().strip()

def nhap_chuoi_khong_rong(thong_bao):
    while True:
        gia_tri = input(thong_bao).strip()
        if gia_tri:
            return gia_tri
        print("  [!] Không được để trống, vui lòng nhập lại.")

def nhap_diem(thong_bao):
    while True:
        chuoi = input(thong_bao).strip().replace(",", ".")
        try:
            diem = float(chuoi)
        except ValueError:
            print("  [!] Điểm phải là một con số, vui lòng nhập lại.")
            continue
        if 0 <= diem <= 10:
            return diem
        print("  [!] Điểm phải nằm trong khoảng 0 - 10, vui lòng nhập lại.")

def nhap_so_nguyen_duong(thong_bao):
    while True:
        try:
            n = int(input(thong_bao).strip())
            if n <= 0:
                raise ValueError
            return n
        except ValueError:
            print("  [!] Vui lòng nhập một số nguyên dương.")

def tim_theo_mssv(ds_sv, mssv):
    for sv in ds_sv:
        if sv["mssv"].lower() == mssv.lower():
            return sv
    return None

def nhap_mot_mon(da_co=None):
    da_co = da_co or []
    while True:
        ten_mon = nhap_chuoi_khong_rong("  Tên môn học: ")
        if any(bo_dau(ten_mon) == bo_dau(m["ten_mon"]) for m in da_co):
            print("  [!] Môn này đã được nhập cho sinh viên, hãy nhập môn khác.")
        else:
            break
    tp1 = nhap_diem("  Điểm thành phần 1 (40%): ")
    tp2 = nhap_diem("  Điểm thành phần 2 (60%): ")
    diem_tk = tinh_diem_mon(tp1, tp2)
    print(f"  -> Điểm tổng kết môn '{ten_mon}': {diem_tk:.1f}")
    return {"ten_mon": ten_mon, "diem_tp1": tp1, "diem_tp2": tp2,
            "diem_tong_ket": diem_tk}

def nhap_sinh_vien(ds_sv):
    print("\n--- NHẬP SINH VIÊN MỚI ---")
    while True:
        mssv = nhap_chuoi_khong_rong("MSSV: ")
        if tim_theo_mssv(ds_sv, mssv):
            print("  [!] MSSV đã tồn tại, vui lòng nhập MSSV khác.")
        else:
            break
    ho_ten = nhap_chuoi_khong_rong("Họ tên: ")
    so_mon = nhap_so_nguyen_duong("Số môn học: ")

    mon_hoc = []
    for i in range(1, so_mon + 1):
        print(f"\n Môn thứ {i}/{so_mon}:")
        mon_hoc.append(nhap_mot_mon(mon_hoc))

    sv = {"mssv": mssv, "ho_ten": ho_ten, "mon_hoc": mon_hoc,
          "gpa": tinh_gpa(mon_hoc)}
    ds_sv.append(sv)
    print(f"\n=> Đã thêm sinh viên {ho_ten} - GPA: {sv['gpa']:.2f}")

def them_mon_cho_sinh_vien(ds_sv):
    print("\n--- THÊM MÔN CHO SINH VIÊN ---")
    mssv = nhap_chuoi_khong_rong("Nhập MSSV: ")
    sv = tim_theo_mssv(ds_sv, mssv)
    if sv is None:
        print("  [!] Không tìm thấy sinh viên.")
        return
    sv["mon_hoc"].append(nhap_mot_mon(sv["mon_hoc"]))
    sv["gpa"] = tinh_gpa(sv["mon_hoc"])
    print(f"=> Đã cập nhật. GPA mới của {sv['ho_ten']}: {sv['gpa']:.2f}")

def luu_json(ds_sv, duong_dan=DUONG_DAN_FILE):
    try:
        with open(duong_dan, "w", encoding="utf-8") as f:
            json.dump(ds_sv, f, ensure_ascii=False, indent=4)
        print(f"=> Đã lưu {len(ds_sv)} sinh viên vào file: {duong_dan}")
        return True
    except (OSError, TypeError) as loi:
        print(f"  [!] Lỗi khi lưu file: {loi}")
        return False

def la_diem_hop_le(x):
    return (isinstance(x, (int, float)) and not isinstance(x, bool)
            and 0 <= x <= 10)

def chuan_hoa_sinh_vien(sv):
    """Kiểm tra 1 bản ghi đọc từ JSON. Hợp lệ -> trả về bản ghi chuẩn
    (điểm tổng kết và GPA được tính lại cho nhất quán). Sai -> raise ValueError."""
    if not isinstance(sv, dict):
        raise ValueError("bản ghi không phải là một đối tượng JSON")
    for truong in ("mssv", "ho_ten", "mon_hoc"):
        if truong not in sv:
            raise ValueError(f"thiếu trường '{truong}'")
    mssv, ho_ten = str(sv["mssv"]).strip(), str(sv["ho_ten"]).strip()
    if not mssv or not ho_ten:
        raise ValueError("MSSV hoặc họ tên bị trống")
    if not isinstance(sv["mon_hoc"], list) or not sv["mon_hoc"]:
        raise ValueError("danh sách môn học rỗng hoặc sai định dạng")

    mon_hoc = []
    for m in sv["mon_hoc"]:
        if not isinstance(m, dict) or not str(m.get("ten_mon", "")).strip():
            raise ValueError("môn học thiếu tên hoặc sai định dạng")
        tp1, tp2 = m.get("diem_tp1"), m.get("diem_tp2")
        if not (la_diem_hop_le(tp1) and la_diem_hop_le(tp2)):
            raise ValueError(f"điểm môn '{m['ten_mon']}' không hợp lệ (phải là số 0-10)")
        mon_hoc.append({"ten_mon": str(m["ten_mon"]).strip(),
                        "diem_tp1": float(tp1), "diem_tp2": float(tp2),
                        "diem_tong_ket": tinh_diem_mon(tp1, tp2)})
    return {"mssv": mssv, "ho_ten": ho_ten, "mon_hoc": mon_hoc,
            "gpa": tinh_gpa(mon_hoc)}

def sao_luu_file(duong_dan, di_chuyen):
    """Giữ lại bản sao của file gốc (.bak) để không bị mất dữ liệu khi lưu đè."""
    ten_bak = duong_dan + ".bak"
    try:
        (os.replace if di_chuyen else shutil.copy2)(duong_dan, ten_bak)
        print(f"  [i] Đã giữ lại file gốc tại: {ten_bak}")
    except OSError as loi:
        print(f"  [!] Không sao lưu được file gốc: {loi}")

def doc_json(duong_dan=DUONG_DAN_FILE):
    try:
        with open(duong_dan, "r", encoding="utf-8") as f:
            du_lieu = json.load(f)
        if not isinstance(du_lieu, list):
            raise ValueError("cấu trúc file JSON không đúng (phải là một danh sách)")
    except FileNotFoundError:
        print("  [i] Chưa có file dữ liệu.")
        return None
    except ValueError as loi:           
        print(f"  [!] File JSON bị hỏng hoặc sai cấu trúc: {loi}")
        sao_luu_file(duong_dan, di_chuyen=True)
        return None
    except OSError as loi:
        print(f"  [!] Lỗi khi đọc file: {loi}")
        return None

    ds_sv, mssv_da_co, so_bi_bo = [], set(), 0
    for i, sv in enumerate(du_lieu, 1):
        try:
            sv = chuan_hoa_sinh_vien(sv)
            if sv["mssv"].lower() in mssv_da_co:
                raise ValueError(f"trùng MSSV '{sv['mssv']}'")
        except ValueError as loi:
            print(f"  [!] Bỏ qua bản ghi thứ {i}: {loi}")
            so_bi_bo += 1
            continue
        mssv_da_co.add(sv["mssv"].lower())
        ds_sv.append(sv)
    if so_bi_bo:
        sao_luu_file(duong_dan, di_chuyen=False)
    return ds_sv

def in_chi_tiet_sinh_vien(sv):
    print(f"\nMSSV: {sv['mssv']} | Họ tên: {sv['ho_ten']} | GPA: {sv['gpa']:.2f}")
    print(f"  {'Môn học':<25}{'TP1 (40%)':>10}{'TP2 (60%)':>10}{'Tổng kết':>10}")
    print("  " + "-" * 55)
    for m in sv["mon_hoc"]:
        print(f"  {m['ten_mon']:<25}{m['diem_tp1']:>10.1f}"
              f"{m['diem_tp2']:>10.1f}{m['diem_tong_ket']:>10.1f}")

def in_bang_tom_tat(ds_sv, tieu_de="DANH SÁCH SINH VIÊN"):
    print(f"\n=== {tieu_de} ===")
    if not ds_sv:
        print("(Danh sách trống)")
        return
    print(f"{'STT':<5}{'MSSV':<14}{'Họ tên':<28}{'Số môn':>7}{'GPA':>8}")
    print("-" * 62)
    for i, sv in enumerate(ds_sv, 1):
        print(f"{i:<5}{sv['mssv']:<14}{sv['ho_ten']:<28}"
              f"{len(sv['mon_hoc']):>7}{sv['gpa']:>8.2f}")

def hien_thi_tat_ca(ds_sv):
    if not ds_sv:
        print("\n(Chưa có sinh viên nào)")
        return
    for sv in ds_sv:
        in_chi_tiet_sinh_vien(sv)

def tim_kiem(ds_sv):
    print("\n--- TÌM KIẾM SINH VIÊN ---")
    tu_khoa = nhap_chuoi_khong_rong("Nhập MSSV hoặc họ tên (có thể gõ không dấu): ")
    k = bo_dau(tu_khoa)
    ket_qua = [sv for sv in ds_sv
               if k in bo_dau(sv["mssv"]) or k in bo_dau(sv["ho_ten"])]
    if not ket_qua:
        print("  [!] Không tìm thấy sinh viên phù hợp.")
        return
    print(f"=> Tìm thấy {len(ket_qua)} kết quả:")
    for sv in ket_qua:
        in_chi_tiet_sinh_vien(sv)

def sap_xep_theo_gpa(ds_sv):
    if not ds_sv:
        print("\n(Chưa có sinh viên nào)")
        return
    print("\n--- SẮP XẾP THEO GPA ---")
    lua_chon = input("1. Giảm dần (cao -> thấp)\n2. Tăng dần (thấp -> cao)\n"
                     "Chọn (mặc định 1): ").strip()
    giam_dan = lua_chon != "2"
    ds_sx = sorted(ds_sv, key=lambda sv: sv["gpa"], reverse=giam_dan)
    in_bang_tom_tat(ds_sx, "SẮP XẾP GPA " + ("GIẢM DẦN" if giam_dan else "TĂNG DẦN"))

def thong_ke(ds_sv):
    print("\n--- THỐNG KÊ ---")
    if not ds_sv:
        print("(Chưa có sinh viên nào)")
        return
    gpa_max = max(sv["gpa"] for sv in ds_sv)
    gpa_min = min(sv["gpa"] for sv in ds_sv)
    gpa_tb = lam_tron(sum(Decimal(str(sv["gpa"])) for sv in ds_sv) / len(ds_sv), 2)

    print(f"Tổng số sinh viên : {len(ds_sv)}")
    print(f"GPA cao nhất      : {gpa_max:.2f}")
    for sv in ds_sv:
        if sv["gpa"] == gpa_max:
            print(f"   - {sv['mssv']} | {sv['ho_ten']}")
    print(f"GPA thấp nhất     : {gpa_min:.2f}")
    for sv in ds_sv:
        if sv["gpa"] == gpa_min:
            print(f"   - {sv['mssv']} | {sv['ho_ten']}")
    print(f"GPA trung bình nhóm: {gpa_tb:.2f}")

def xoa_sinh_vien(ds_sv):
    print("\n--- XÓA SINH VIÊN ---")
    sv = tim_theo_mssv(ds_sv, nhap_chuoi_khong_rong("Nhập MSSV cần xóa: "))
    if sv is None:
        print("  [!] Không tìm thấy sinh viên.")
        return
    if input(f"Xóa {sv['ho_ten']}? (y/n): ").strip().lower() == "y":
        ds_sv.remove(sv)
        print("=> Đã xóa.")

MENU = """
============= QUẢN LÝ KẾT QUẢ HỌC TẬP =============
 1. Nhập sinh viên mới
 2. Thêm môn học cho sinh viên đã có
 3. Hiển thị danh sách (chi tiết)
 4. Tìm kiếm theo MSSV / họ tên
 5. Sắp xếp theo GPA
 6. Thống kê GPA (cao nhất, thấp nhất, trung bình)
 7. Lưu dữ liệu vào file JSON
 8. Đọc lại dữ liệu từ file JSON
 9. Xóa sinh viên
 0. Thoát
===================================================="""

def main():
    ds_sv = doc_json() or []                # tự động đọc dữ liệu cũ (nếu có)
    ban_da_luu = copy.deepcopy(ds_sv)       # để biết còn thay đổi chưa lưu hay không
    if ds_sv:
        print(f"=> Đã nạp {len(ds_sv)} sinh viên từ file JSON.")

    while True:
        print(MENU)
        chon = input("Chọn chức năng: ").strip()
        try:
            if chon == "1":
                nhap_sinh_vien(ds_sv)
            elif chon == "2":
                them_mon_cho_sinh_vien(ds_sv)
            elif chon == "3":
                hien_thi_tat_ca(ds_sv)
            elif chon == "4":
                tim_kiem(ds_sv)
            elif chon == "5":
                sap_xep_theo_gpa(ds_sv)
            elif chon == "6":
                thong_ke(ds_sv)
            elif chon == "7":
                if luu_json(ds_sv):
                    ban_da_luu = copy.deepcopy(ds_sv)
            elif chon == "8":
                moi = doc_json()
                if moi is None:
                    print("=> Giữ nguyên dữ liệu hiện tại trong bộ nhớ.")
                elif ds_sv != ban_da_luu and input(
                        "Có thay đổi CHƯA LƯU, đọc lại sẽ làm mất chúng. "
                        "Tiếp tục? (y/n): ").strip().lower() != "y":
                    print("=> Đã hủy, giữ nguyên dữ liệu hiện tại.")
                else:
                    ds_sv = moi
                    ban_da_luu = copy.deepcopy(ds_sv)
                    print(f"=> Đã đọc {len(ds_sv)} sinh viên từ file JSON.")
                    hien_thi_tat_ca(ds_sv)
            elif chon == "9":
                xoa_sinh_vien(ds_sv)
            elif chon == "0":
                if ds_sv != ban_da_luu and input(
                        "Có thay đổi chưa lưu. Lưu trước khi thoát? (y/n): "
                        ).strip().lower() == "y":
                    luu_json(ds_sv)
                print("Tạm biệt!")
                break
            else:
                print("  [!] Lựa chọn không hợp lệ, hãy chọn từ 0 đến 9.")
        except (KeyboardInterrupt, EOFError):
            print("\n  [!] Đã hủy thao tác hiện tại, quay lại menu.")
        except Exception as loi:        # lưới an toàn cuối cùng
            print(f"  [!] Có lỗi không mong muốn: {loi}")

if __name__ == "__main__":
    main()
