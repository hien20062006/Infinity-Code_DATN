CREATE DATABASE DWH_Sales;
GO

USE DWH_Sales;
GO



CREATE TABLE Dim_Customer
(
    Customer_ID VARCHAR(20) PRIMARY KEY,
    Customer_Name NVARCHAR(100),
    Gender NVARCHAR(10),
    Phone VARCHAR(20)
);

CREATE TABLE Dim_Product
(
    Product_ID VARCHAR(20) PRIMARY KEY,
    Product_Name NVARCHAR(200),
    Category NVARCHAR(100)
);

CREATE TABLE Dim_Location
(
    Location_ID INT IDENTITY(1,1) PRIMARY KEY,
    Province NVARCHAR(100),
    District NVARCHAR(100),
    Address NVARCHAR(300)
);

CREATE TABLE Dim_Channel
(
    Channel_ID INT IDENTITY(1,1) PRIMARY KEY,
    Channel_Name NVARCHAR(100)
);


CREATE TABLE Dim_Date
(
    Date_ID INT PRIMARY KEY,
    Full_Date DATE,
    Day_Num INT,
    Month_Num INT,
    Quarter_Num INT,
    Year_Num INT
);


CREATE TABLE Fact_Sales
(
    Order_ID VARCHAR(20),

    Customer_ID VARCHAR(20),
    Product_ID VARCHAR(20),

    Quantity INT,
    Unit_Price FLOAT,

    Discount_Rate FLOAT,

    VAT FLOAT,
    Shipping_Fee FLOAT,

    Revenue FLOAT,

    FOREIGN KEY(Customer_ID)
        REFERENCES Dim_Customer(Customer_ID),

    FOREIGN KEY(Product_ID)
        REFERENCES Dim_Product(Product_ID)
);



                 Dim_Customer
                        |
                        |
Dim_Product ---- Fact_Sales ---- Dim_Location
                        |
                        |
                   Dim_Channel