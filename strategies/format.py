import pandas as pd
import requests
import xlsxwriter
writer = pd.ExcelWriter("recommended trades.xlsx", engine="xlsxwriter")

background_color = "#0a0a23"
font_color = "#ffffff"

string_format = writer.book.add_format(
    {
        "font_color": font_color,
        "bg_color": background_color,
        "border": 1,
    }
)
dollar_format = writer.book.add_format(
    {
        "num_format": "$0.00",
        "font_color": font_color,
        "bg_color": background_color,
        "border": 1,
    }
)
integer_format = writer.book.add_format(
    {
        "num_format": "0",
        "font_color": font_color,
        "bg_color": background_color,
        "border": 1,
    }
)