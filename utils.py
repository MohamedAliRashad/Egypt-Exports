import re
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import zipfile
import os

def parse_money(text: str) -> tuple:
    # Get the money value whether it's in float or int
    money = re.findall(r"[-+]?\d*\.\d+|\d+", text)[0]
    return float(money), text.replace(str(money), '').strip()

def extract_items_data(dom, output_file="items.csv"):
    # Make dataframe for items data
    df_items = pd.DataFrame(columns=["Item", "Amount", "Value"])

    # Get items data
    items_table = dom.xpath("//table")[0].xpath(".//tr")
    for row in items_table:
        # Get all cells
        cells = row.xpath(".//td")
        if len(cells) > 0:
            item_name = cells[0].text.split("-")[-1].strip()
            item_cost = cells[1].text.strip()
            amount, value = parse_money(item_cost)
            df_items = df_items.append({"Item": item_name, "Amount": amount, "Value": value}, ignore_index=True)

    df_items.to_csv(output_file, index=False)

def extract_yearly_data(dom, output_file="yearly.csv"):
    # Make dataframe for yearly data
    df_yearly = pd.DataFrame(columns=["Year", "Export Amount", "Export Value"])
    main_table = dom.xpath("//table")[1]

    # Get yearly exports data
    years = main_table.xpath(".//thead/tr/th/text()")
    yearly_exports_amount = [parse_money(value)[0] for value in main_table.xpath(".//tbody/tr[1]/td/text()")[1:]]
    yearly_exports_value = [parse_money(value)[1] for value in main_table.xpath(".//tbody/tr[1]/td/text()")[1:]]
    df_yearly["Year"] = years
    df_yearly["Export Amount"] = yearly_exports_amount
    df_yearly["Export Value"] = yearly_exports_value
    
    df_yearly.to_csv(output_file, index=False)

def extract_monthly_yearly_data(dom, output_file="monthly.csv"):
    # Make dataframe for yearly-monthly data
    df_monthly = pd.DataFrame(columns=["Year", "Month", "Export Amount"])

    # Get monthly exports data
    yearly_monthly_exports = dom.xpath("//div[@class='row geo_info_item']")
    # print(len(yearly_monthly_exports))
    for yearly_monthly_export in yearly_monthly_exports:
        # Get year
        year = "".join(yearly_monthly_export.xpath(".//div/h2/text()")).strip()
        # Get monthly exports
        months = yearly_monthly_export.xpath(".//table/thead/tr/th/text()")
        # print(year, months)
        monthly_exports = [x for x in yearly_monthly_export.xpath(".//table/tbody/tr/td/text()")]
        # print(monthly_exports)
        for i in range(len(months)):
            df_monthly = df_monthly.append({"Year": year, "Month": months[i], "Export Amount": monthly_exports[i]}, ignore_index=True)

    df_monthly.to_csv(output_file, index=False)

def clean_dataset(dataset_path):
    dataset_path = Path(dataset_path)
    for country_path in tqdm(dataset_path.iterdir()):
        all_files = list(country_path.iterdir())
        if len(all_files) < 4:
            for file in country_path.iterdir():
                file.unlink()
            country_path.rmdir()

def normalize_money(df, money_column_name, value_column_name, normalize_to="مليون"):
    values_dict = {"مليون": 1000000, "ألف": 1000, "مليار": 1000000000}
    df[value_column_name].fillna("لا شئ", inplace=True)
    for key, value in values_dict.items():
        if value != "لا شئ":
            df.loc[df[value_column_name].str.contains(key), money_column_name] = df[money_column_name] * value / values_dict[normalize_to]
    
    return df

def zip_directory(input_dir, output_file):
    # Create a ZipFile object
    zipf = zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED)
    
    # Walk through the directory tree and add each file to the zip file
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            zipf.write(os.path.join(root, file))
    
    # Close the ZipFile
    zipf.close()

def str_money2int(text: str) -> int:
    # Extract number from string (e.g. 543,354)
    money = text.replace(",", "")
    return int(money)


if __name__ == "__main__":
    # print(parse_money(
    # "0 ألف دولار"))
    # clean_dataset("dataset")
    print(str_money2int("0"))