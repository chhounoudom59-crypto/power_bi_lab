import csv
import os

staff_csv_path = r"C:\Users\ROG Zephyrus G15\Desktop\bitest\lab-final\HR_Warehouse\HR_Warehouse\Staff.csv"
salary_csv_path = r"C:\Users\ROG Zephyrus G15\Desktop\bitest\lab-final\HR_Warehouse\HR_Warehouse\Salary.csv"
leave_csv_path = r"C:\Users\ROG Zephyrus G15\Desktop\bitest\lab-final\HR_Warehouse\HR_Warehouse\Leave.csv"
attendance_csv_path = r"C:\Users\ROG Zephyrus G15\Desktop\bitest\lab-final\HR_Warehouse\HR_Warehouse\AttendanceReport.csv"
evaluate_csv_path = r"C:\Users\ROG Zephyrus G15\Desktop\bitest\lab-final\HR_Warehouse\HR_Warehouse\Evaluate.csv"

# Load existing staff
existing_staff = set()
with open(staff_csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if row:
            existing_staff.add(row[0])

# Find all staff IDs in other files
all_staff_ids = {}

def process_file(path, staff_idx, date_idx):
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            next(reader) # skip header
        except StopIteration:
            return
        for row in reader:
            if len(row) > max(staff_idx, date_idx):
                sid = row[staff_idx]
                dt = row[date_idx].split(' ')[0] # strip time
                if sid:
                    if sid not in all_staff_ids:
                        all_staff_ids[sid] = []
                    all_staff_ids[sid].append(dt)

process_file(salary_csv_path, 4, 1) # StaffId is 5th col, Date is 2nd col
process_file(leave_csv_path, 1, 3) # StaffId is 2nd col, StartTime is 4th col
process_file(attendance_csv_path, 1, 2) # StaffId is 2nd col, Date is 3rd col
process_file(evaluate_csv_path, 2, 1) # StaffId is 3rd col, Date is 2nd col

missing_sids = [sid for sid in all_staff_ids if sid not in existing_staff]
print(f"Found {len(missing_sids)} missing staff IDs: {missing_sids}")

if not missing_sids:
    print("No missing staff found!")
    exit()

# Get details from Salary.csv
salary_details = {}
with open(salary_csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if len(row) >= 11:
            sid = row[4]
            if sid in missing_sids:
                salary_details[sid] = {
                    'amount': row[7],
                    'contract_id': row[8],
                    'position_id': row[9],
                    'working_rate': row[10]
                }

# Append new staff
new_rows = []
for idx, sid in enumerate(missing_sids, 1):
    dates = all_staff_ids[sid]
    start_date = min(dates) if dates else "2024-01-01"
    
    details = salary_details.get(sid, {
        'amount': '250.0',
        'contract_id': '075bae61-235e-4872-85c1-8cacfaa9d20e', # Full Time
        'position_id': 'bf762931-b59c-4ad1-a9f2-17a6818be5aa', # Technician II
        'working_rate': '1.2'
    })
    
    name = f"បុគ្គលិកមិនស្គាល់ {idx + 3}"
    
    new_rows.append([
        sid,
        name,
        start_date,
        '', # EndDate is empty
        details['position_id'],
        details['contract_id'],
        details['amount'],
        '44', # WorkingHours default
        details['working_rate']
    ])

# Write back to Staff.csv
with open(staff_csv_path, 'a', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(new_rows)

print(f"Appended {len(new_rows)} staff members to Staff.csv!")
