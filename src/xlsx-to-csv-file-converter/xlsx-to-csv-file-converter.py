import pandas as pd
import os
from pathlib import Path


def convert_xlsx_to_csv(file_path):
    # Get current directory
    current_path = os.getcwd()
    file_path = os.path.join(current_path, "src","xlsx-to-csv-file-converter",file_path)

    # Ensure the input file exists
    file_path = Path(file_path).resolve()

    print("----------------------------------")
    print(f"File path : {file_path}")
    print("----------------------------------")
    if not file_path.is_file():
        print(f"File '{file_path}' does not exist.")
        return

    try:
        # Load the XLSX file
        xlsx = pd.ExcelFile(file_path)

        # Create a directory for CSV files
        base_name = file_path.stem
        output_dir = file_path.parent / base_name  # Save in the same directory as the input file
        output_dir.mkdir(exist_ok=True)
        print(f"Output directory created at: {output_dir.resolve()}")

        # Iterate through each sheet and save as CSV
        for sheet_name in xlsx.sheet_names:
            df = pd.read_excel(xlsx, sheet_name=sheet_name)
            csv_file_name = f"{sheet_name}.csv"
            csv_file_path = output_dir / csv_file_name
            df.to_csv(csv_file_path, index=False)
            print(f"Converted sheet '{sheet_name}' to CSV: {csv_file_path.resolve()}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    file_path = "new.xlsx"
    convert_xlsx_to_csv(file_path)
