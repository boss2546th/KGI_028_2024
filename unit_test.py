import os
import pandas as pd
import shutil
import time
import numpy as np

# กำหนดเส้นทางสำหรับ output_dir
output_dir = os.path.expanduser("~/Desktop/competition_api")
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created main directory: {output_dir}")

# ฟังก์ชันสำหรับโหลดข้อมูลจากไฟล์
def load_previous(file_type, teamName):
    folder_path = os.path.join(output_dir, "Previous", file_type)
    file_path = os.path.join(folder_path, f"{teamName}_{file_type}.csv")
    
    if os.path.exists(file_path):
        try:
            data = pd.read_csv(file_path)
            print(f"Loaded '{file_type}' data for team {teamName}.")
            return data
        except Exception as e:
            print(f"Error loading file: {e}")
            return None
    else:
        print(f"File not found: {file_path}")
        return None

# ฟังก์ชันสำหรับบันทึกข้อมูล
def save_output(data, file_type, teamName):
    folder_path = os.path.join(output_dir, "Previous", file_type)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f"{teamName}_{file_type}.csv")
    data.to_csv(file_path, index=False)
    print(f"Saved '{file_type}' data for team {teamName} to {file_path}.")
# ฟังก์ชันสำหรับการตรวจสอบความถูกต้องของไฟล์
def check_file_validity(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    return True



def check_files():
    global result_dir,portfolio_file ,statement_file ,summary_file
    if check_file_validity(portfolio_file): print("File ok")
    #     portfolio_df = pd.read_csv(portfolio_file)
    #     validate_portfolio(portfolio_df)

    # if check_file_validity(statement_file):
    #     statement_df = pd.read_csv(statement_file)
    #     validate_statement(statement_df)

    # if check_file_validity(summary_file):
    #     summary_df = pd.read_csv(summary_file)
    #     validate_summary(summary_df)


# ฟังก์ชันสำหรับการทดสอบอัตโนมัติ
tick_list = [11,12,13,16,17,18,19]
def automated_testing():
    global result_dir,portfolio_file ,statement_file ,summary_file
    for tick in tick_list[5:]:  # จาก Tick11 ถึง Tick17
        # 1. นำ Daily_Ticks.csv ใน Tick11 - 16 มาไว้ ~/Desktop/Daily_Ticks.csv
        daily_ticks_path = f"D:/KGI_algotrad/Tick{tick}/Daily_Ticks.csv"
        destination_path = "~/Desktop/Daily_Ticks.csv"
        shutil.copy(daily_ticks_path, os.path.expanduser(destination_path))
        print(f"Copied Daily_Ticks.csv from Tick{tick} to {destination_path}")

        # 2. รัน 028_WarrenBuffet.py
        os.system("python D:/KGI_algotrad/028test_19.py")  # เปลี่ยนเส้นทางตามที่คุณต้องการ
        time.sleep(5)  # รอให้สคริปต์ทำงานเสร็จ

        # 3. เช็คความถูกต้องสมเหตุสมผลของ output csv ทั้ง 3
        result_dir = os.path.join(output_dir, "Result")
        portfolio_file = os.path.join(result_dir, "portfolio/028_WarrenBuffet_portfolio.csv")
        statement_file = os.path.join(result_dir, "statement/028_WarrenBuffet_statement.csv")
        summary_file = os.path.join(result_dir, "summary/028_WarrenBuffet_summary.csv")
        check_files()
        # สมมติว่า df เป็น DataFrame ที่คุณโหลดมาจากไฟล์ CSV

        # 4. ย้ายข้อมูลจาก Result ไป Previous โดยทับไฟล์เดิม
        previous_dir = os.path.join(output_dir, "Previous")
        os.makedirs(previous_dir, exist_ok=True)


        # คัดลอกไฟล์จาก Result ไปยัง Previous โดยทับไฟล์เดิม
        for file_name in ["portfolio/028_WarrenBuffet_portfolio.csv", 
                        "statement/028_WarrenBuffet_statement.csv", 
                        "summary/028_WarrenBuffet_summary.csv"]:
            
            # สร้างเส้นทางสำหรับไฟล์ใน Previous
            previous_file_path = os.path.join(previous_dir, file_name)
            
            # สร้างโฟลเดอร์ที่จำเป็นใน Previous หากยังไม่มีอยู่
            previous_folder = os.path.dirname(previous_file_path)
            os.makedirs(previous_folder, exist_ok=True)

            result_file_path = os.path.join(result_dir, file_name)
            
            if os.path.exists(result_file_path):
                shutil.copy(result_file_path, previous_file_path)
                print(f"Copied {file_name} from Result to Previous, overwriting existing file.")
            else:
                print(f"File not found in Result: {result_file_path}")

        # ลบ Result directory
        if os.path.exists(result_dir):
            shutil.rmtree(result_dir)
            print(f"Deleted Result directory: {result_dir}")

# เรียกใช้ฟังก์ชันการทดสอบอัตโนมัติ
automated_testing()


