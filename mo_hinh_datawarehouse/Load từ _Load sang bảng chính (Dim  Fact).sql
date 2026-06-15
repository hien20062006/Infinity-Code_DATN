1. Dim_Customer
INSERT INTO Dim_Customer (Customer_ID, Customer_Name, Gender, Phone)
SELECT Customer_ID, Customer_Name, Gender, Phone
FROM Dim_Customer_Load;
2. Dim_Product
INSERT INTO Dim_Product (Product_ID, Product_Name, Category)
SELECT Product_ID, Product_Name, Category
FROM Dim_Product_Load;
3. Dim_Location
INSERT INTO Dim_Location (Location_ID, Province, District, Address)
SELECT Location_ID, Province, District, Address
FROM Dim_Location_Load;
4. Dim_Date
INSERT INTO Dim_Date (Date_ID, Full_Date, Day_Num, Month_Num, Quarter_Num, Year_Num)
SELECT Date_ID, Full_Date, Day_Num, Month_Num, Quarter_Num, Year_Num
FROM Dim_Date_Load;
5. Dim_Channel
INSERT INTO Dim_Channel (Channel_ID, Channel_Name)
SELECT Channel_ID, Channel_Name
FROM Dim_Channel_Load;
6. Fact_Sales
INSERT INTO Fact_Sales
(Order_ID, Customer_ID, Product_ID, Quantity, Unit_Price, Discount_Rate, VAT, Shipping_Fee, Revenue)
SELECT
Order_ID, Customer_ID, Product_ID, Quantity, Unit_Price, Discount_Rate, VAT, Shipping_Fee, Revenue
FROM Fact_Sales_Load;

Kiểm tra dữ liệu đã vào
SELECT COUNT(*) FROM Dim_Customer;
SELECT COUNT(*) FROM Dim_Product;
SELECT COUNT(*) FROM Dim_Location;
SELECT COUNT(*) FROM Dim_Date;
SELECT COUNT(*) FROM Dim_Channel;
SELECT COUNT(*) FROM Fact_Sales;