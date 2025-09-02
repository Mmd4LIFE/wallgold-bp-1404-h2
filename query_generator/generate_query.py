# read last folder (only directories) in data folder and daily_breakdown_regression_30_7_2.csv in it
import os
import pandas as pd

data_folder = "data"
# Only include directories
folders = [f for f in os.listdir(data_folder) if os.path.isdir(os.path.join(data_folder, f))]
if not folders:
    raise FileNotFoundError("No folders found in the data directory.")
last_folder = sorted(folders)[-1]
print(last_folder)

df = pd.read_csv(f"data/{last_folder}/daily_breakdown_regression_30_7_2.csv")
df = df[["persian_date", "date_id", "date_string", "line", "metric", "sub_metric", "daily_target", "unit"]]

select_statements = []
for index, row in df.iterrows():
    select_stmt = (
        f"SELECT '{row['persian_date']}' AS persian_date, "
        f"{row['date_id']} AS date_id, "
        f"'{row['date_string']}' AS date_string, "
        f"'{row['line']}' AS line, "
        f"'{row['metric']}' AS metric, "
        f"'{row['sub_metric']}' AS sub_metric, "
        f"{row['daily_target']} AS daily_target, "
        f"'{row['unit']}' AS unit"
    )
    select_statements.append(select_stmt)

sql_query = "\nUNION ALL\n".join(select_statements)

# Save the SQL query to a text file
output_file = f"data/{last_folder}/generated_query.sql"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(sql_query)

print(f"SQL query saved to {output_file}")