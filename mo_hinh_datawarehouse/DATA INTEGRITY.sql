1. Kiểm tra NULL trong Fact
SELECT *
FROM Fact_Sales_load 
WHERE Customer_ID IS NULL
   OR Product_ID IS NULL;
2. Kiểm tra dữ liệu mồ côi (Fact không có Dim)
SELECT *
FROM Fact_Sales f
LEFT JOIN Dim_Customer c
ON f.Customer_ID = c.Customer_ID
WHERE c.Customer_ID IS NULL;

SELECT *
FROM Fact_Sales_load f
LEFT JOIN Dim_Product p
ON f.Product_ID = p.Product_ID
WHERE p.Product_ID IS NULL;
3. Kiểm tra trùng
SELECT Order_ID, COUNT(*)
FROM Fact_Sales
GROUP BY Order_ID
HAVING COUNT(*) > 1;