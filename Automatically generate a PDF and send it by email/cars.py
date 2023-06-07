#!/usr/bin/env python3

import json
import locale
import sys
import reports
import emails

def load_data(filename):
  """Loads the contents of filename as a JSON file."""
  with open(filename) as json_file:
    data = json.load(json_file)
  return data


def format_car(car):
  """Given a car dictionary, returns a nicely formatted name."""
  return f"{car['car_make']} {car['car_model']} ({car['car_year']})"

def sort_by_sales(item):
    return item[1]

def process_data(data):
  """Analyzes the data, looking for maximums.

  Returns a list of lines that summarize the information.
  """
  locale.setlocale(locale.LC_ALL, '')
  max_revenue = {"revenue": 0}
  max_sales = {"total_sales": 0, "car_model": ""}
  pop_car_yr = {}

  for item in data:
    # Calculate the revenue generated by this model (price * total_sales)
    # We need to convert the price from "$1234.56" to 1234.56
    item_price = locale.atof(item["price"].strip("$"))
    item_revenue = item["total_sales"] * item_price
    if item_revenue > max_revenue["revenue"]:
      item["revenue"] = item_revenue
      max_revenue = item
    
    #dealing with peak sales
    if item["total_sales"] > max_sales["total_sales"]:
      max_sales["total_sales"] = item["total_sales"]
      max_sales["car_model"] = item["car"]["car_model"]

    #dealing with most popular car_year
    pop_car_yr[item["car"]["car_year"]] = pop_car_yr.get(item["car"]["car_year"], 0) +  item["total_sales"]

  pop_car_yr_sorted = sorted(pop_car_yr.items(), key=sort_by_sales, reverse=True)
  
  summary = [
    f"The {format_car(max_revenue['car'])} generated the most revenue: ${max_revenue['revenue']}",
    f"The {max_sales['car_model']} had the most sales: {max_sales['total_sales']}",
    f"The most popular year was {pop_car_yr_sorted[0][0]} with {pop_car_yr_sorted[0][1]} sales.",
  ]

  return summary


def sort_by_total_sales(item):
    return int(item[3])

def cars_dict_to_table(car_data):
    """Turns the data in car_data into a list of lists."""
    table_cols = [["ID", "Car", "Price", "Total Sales"]]
    cars_list = []
    for item in car_data:
        cars_list.append([item["id"], format_car(item["car"]), item["price"], item["total_sales"]])
    
    cars_list.sort(key=sort_by_total_sales, reverse=True)
    return table_cols + cars_list



def main(argv):
  """Process the JSON data and generate a full report out of it."""
  data = load_data("car_sales.json")
  summary = process_data(data)
  print(summary)

  #turning this into a PDF report
  car_data = cars_dict_to_table(data)
  reports.generate("/tmp/cars.pdf", "Sales summary for last month", "<br/>".join(summary), car_data)

  #sending the PDF report as an email attachment
  message = emails.generate("automation@example.com", "<studentID>@example.com", "Sales summary for last month", "\n".join(summary), "/tmp/cars.pdf")
  emails.send(message)


if __name__ == "__main__":
  main(sys.argv)