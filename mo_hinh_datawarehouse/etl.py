import pandas as pd

# =====================
# EXTRACT
# =====================

df = pd.read_excel(
    "htdl1.xlsx",
    sheet_name="DuLieu_10000"
)

print("So dong du lieu:", len(df))

# =====================
# DATA CLEANING
# =====================

df = df.drop_duplicates()

# =====================
# DIM_CUSTOMER
# =====================

dim_customer = df[
    [
        'Ma_Khach_Hang',
        'Ten_Khach_Hang',
        'Gioi_Xung_Ho',
        'So_Dien_Thoai'
    ]
].drop_duplicates()

dim_customer.columns = [
    'Customer_ID',
    'Customer_Name',
    'Gender',
    'Phone'
]

# =====================
# DIM_PRODUCT
# =====================

dim_product = df[
    [
        'Ma_San_Pham',
        'Ten_San_Pham',
        'Nhom_Hang'
    ]
].drop_duplicates()

dim_product.columns = [
    'Product_ID',
    'Product_Name',
    'Category'
]

# =====================
# DIM_LOCATION
# =====================

dim_location = df[
    [
        'Tinh_Thanh',
        'Phuong_Xa',
        'Dia_Chi_Cu_The'
    ]
].drop_duplicates()

dim_location.columns = [
    'Province',
    'District',
    'Address'
]

dim_location.insert(
    0,
    'Location_ID',
    range(1, len(dim_location) + 1)
)

# =====================
# DIM_DATE
# =====================

dim_date = pd.DataFrame()

dim_date['Full_Date'] = pd.to_datetime(
    df['Ngay_Dat']
).drop_duplicates()

dim_date = dim_date.sort_values(
    'Full_Date'
).reset_index(drop=True)

dim_date.insert(
    0,
    'Date_ID',
    range(1, len(dim_date) + 1)
)

dim_date['Day_Num'] = dim_date['Full_Date'].dt.day
dim_date['Month_Num'] = dim_date['Full_Date'].dt.month
dim_date['Quarter_Num'] = dim_date['Full_Date'].dt.quarter
dim_date['Year_Num'] = dim_date['Full_Date'].dt.year

# =====================
# DIM_CHANNEL
# =====================

dim_channel = df[
    [
        'Kenh_Ban'
    ]
].drop_duplicates()

dim_channel.columns = [
    'Channel_Name'
]

dim_channel.insert(
    0,
    'Channel_ID',
    range(1, len(dim_channel) + 1)
)

# =====================
# FACT_SALES
# =====================

fact_sales = df[
    [
        'Ma_Don',
        'Ma_Khach_Hang',
        'Ma_San_Pham',
        'So_Luong',
        'Don_Gia',
        'VAT_10',
        'Phi_Van_Chuyen',
        'Tong_Thanh_Toan'
    ]
].copy()

fact_sales.columns = [
    'Order_ID',
    'Customer_ID',
    'Product_ID',
    'Quantity',
    'Unit_Price',
    'VAT',
    'Shipping_Fee',
    'Revenue'
]

fact_sales.insert(
    5,
    'Discount_Rate',
    0
)

# =====================
# DATA INTEGRITY
# =====================

print("\n===== DATA INTEGRITY =====")

print(
    "So dong trung lap:",
    df.duplicated().sum()
)

print("\nGia tri NULL:")
print(df.isnull().sum())

# =====================
# LOAD CSV
# =====================

dim_customer.to_csv(
    "Dim_Customer.csv",
    index=False
)

dim_product.to_csv(
    "Dim_Product.csv",
    index=False
)

dim_location.to_csv(
    "Dim_Location.csv",
    index=False
)

dim_date.to_csv(
    "Dim_Date.csv",
    index=False
)

dim_channel.to_csv(
    "Dim_Channel.csv",
    index=False
)

fact_sales.to_csv(
    "Fact_Sales.csv",
    index=False
)

print("\nETL thanh cong!")