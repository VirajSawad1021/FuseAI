-- ============================================================
--   SQL Assignment Solutions — ClassicModels Database
-- ============================================================

USE classicmodels;


-- Q1. Show all customers whose creditLimit is greater than 20,000
SELECT *
FROM customers
WHERE creditLimit > 20000;


-- Q2. Show employees who report to VP Sales
SELECT e.*
FROM employees e
JOIN employees mgr ON e.reportsTo = mgr.employeeNumber
WHERE mgr.jobTitle = 'VP Sales';


-- Q3. Customers who have set their state, live in USA,
--     and have credit limit between 100,000 and 200,000
SELECT *
FROM customers
WHERE state IS NOT NULL
  AND country = 'USA'
  AND creditLimit BETWEEN 100000 AND 200000;


-- Q4. Employees who report to any type of Sales Manager
SELECT e.*
FROM employees e
JOIN employees mgr ON e.reportsTo = mgr.employeeNumber
WHERE mgr.jobTitle LIKE '%Sales Manager%';


-- Q5. Average credit limit of customers per country
SELECT
    country,
    ROUND(AVG(creditLimit), 2) AS avg_creditLimit
FROM customers
GROUP BY country
ORDER BY avg_creditLimit DESC;


-- Q6. Total orders per date and customer — show only where count > 10
SELECT
    orderDate,
    customerNumber,
    COUNT(*) AS total_orders
FROM orders
GROUP BY orderDate, customerNumber
HAVING COUNT(*) > 10;


-- Q7. Supervisor name, job title, and total supervisees WITHOUT using JOIN
SELECT
    CONCAT(firstName, ' ', lastName) AS supervisor_name,
    jobTitle,
    (SELECT COUNT(*)
     FROM employees e2
     WHERE e2.reportsTo = e1.employeeNumber) AS total_supervisees
FROM employees e1
WHERE (SELECT COUNT(*)
       FROM employees e2
       WHERE e2.reportsTo = e1.employeeNumber) > 0;


-- Q8. Supervisor name, job title, and total supervisees USING JOIN
SELECT
    CONCAT(mgr.firstName, ' ', mgr.lastName) AS supervisor_name,
    mgr.jobTitle,
    COUNT(emp.employeeNumber)                 AS total_supervisees
FROM employees mgr
JOIN employees emp ON emp.reportsTo = mgr.employeeNumber
GROUP BY mgr.employeeNumber, mgr.firstName, mgr.lastName, mgr.jobTitle
ORDER BY total_supervisees DESC;


-- Q9. Customers with credit limit above average — using WITH clause
WITH avg_credit AS (
    SELECT AVG(creditLimit) AS avg_limit
    FROM customers
)
SELECT c.*
FROM customers c
JOIN avg_credit ON c.creditLimit > avg_credit.avg_limit
ORDER BY c.creditLimit DESC;


-- Q10a. Rank every customer by credit limit (highest = rank 1)
SELECT
    customerName,
    creditLimit,
    RANK() OVER (ORDER BY creditLimit DESC) AS credit_rank
FROM customers;

-- Q10b. Customer with the 3rd highest credit limit
WITH ranked_customers AS (
    SELECT
        customerName,
        creditLimit,
        RANK() OVER (ORDER BY creditLimit DESC) AS credit_rank
    FROM customers
)
SELECT *
FROM ranked_customers
WHERE credit_rank = 3;


-- Q11. Total employees working in each office
SELECT
    o.officeCode,
    o.city,
    o.country,
    COUNT(e.employeeNumber) AS total_employees
FROM offices o
LEFT JOIN employees e ON o.officeCode = e.officeCode
GROUP BY o.officeCode, o.city, o.country
ORDER BY total_employees DESC;


-- Q12. Total customers served by each office
SELECT
    o.officeCode,
    o.city,
    o.country,
    COUNT(c.customerNumber) AS total_customers
FROM offices o
LEFT JOIN employees e ON o.officeCode = e.officeCode
LEFT JOIN customers c  ON c.salesRepEmployeeNumber = e.employeeNumber
GROUP BY o.officeCode, o.city, o.country
ORDER BY total_customers DESC;


-- Q13. Total payment received by each office
SELECT
    o.city        AS office_name,
    o.state,
    o.country,
    ROUND(SUM(p.amount), 2) AS total_payments_received
FROM offices o
JOIN employees e ON o.officeCode = e.officeCode
JOIN customers c ON c.salesRepEmployeeNumber = e.employeeNumber
JOIN payments p  ON p.customerNumber = c.customerNumber
GROUP BY o.officeCode, o.city, o.state, o.country
ORDER BY total_payments_received DESC;


-- Q14. Total sales (amount) by each office using orderdetails
SELECT
    o.city   AS office_name,
    o.state,
    o.country,
    ROUND(SUM(od.quantityOrdered * od.priceEach), 2) AS total_sales
FROM offices o
JOIN employees    e   ON o.officeCode  = e.officeCode
JOIN customers    c   ON c.salesRepEmployeeNumber = e.employeeNumber
JOIN orders       ord ON ord.customerNumber = c.customerNumber
JOIN orderdetails od  ON od.orderNumber    = ord.orderNumber
WHERE ord.status IN ('Shipped', 'Resolved')  -- only count completed orders
GROUP BY o.officeCode, o.city, o.state, o.country
ORDER BY total_sales DESC;


-- Q15. Total payment pending for each office (total sales − total payments)
WITH office_sales AS (
    SELECT
        o.officeCode,
        o.city,
        o.state,
        o.country,
        SUM(od.quantityOrdered * od.priceEach) AS total_sales
    FROM offices o
    JOIN employees    e   ON o.officeCode  = e.officeCode
    JOIN customers    c   ON c.salesRepEmployeeNumber = e.employeeNumber
    JOIN orders       ord ON ord.customerNumber = c.customerNumber
    JOIN orderdetails od  ON od.orderNumber    = ord.orderNumber
    WHERE ord.status IN ('Shipped', 'Resolved')  -- only completed sales
    GROUP BY o.officeCode, o.city, o.state, o.country
),
office_payments AS (
    SELECT
        o.officeCode,
        SUM(p.amount) AS total_paid
    FROM offices o
    JOIN employees e ON o.officeCode = e.officeCode
    JOIN customers c ON c.salesRepEmployeeNumber = e.employeeNumber
    JOIN payments  p ON p.customerNumber = c.customerNumber
    GROUP BY o.officeCode
)
SELECT
    os.city,
    os.state,
    os.country,
    ROUND(os.total_sales, 2)                          AS total_sales,
    ROUND(COALESCE(op.total_paid, 0), 2)              AS total_paid,
    ROUND(os.total_sales - COALESCE(op.total_paid, 0), 2) AS payment_pending
FROM office_sales os
LEFT JOIN office_payments op ON os.officeCode = op.officeCode  -- LEFT JOIN so offices with no payments still appear
ORDER BY payment_pending DESC;


-- Q16. Credit limit and proportion of each customer within their country
SELECT
    customerName,
    country,
    creditLimit,
    ROUND(
        creditLimit / SUM(creditLimit) OVER (PARTITION BY country),
        4
    ) AS proportion_in_country
FROM customers
ORDER BY country, proportion_in_country DESC;


-- Q17. View: customer name, complete address, total number of orders
CREATE OR REPLACE VIEW customer_order_summary AS
SELECT
    c.customerName,
    CONCAT(
        c.addressLine1,
        IFNULL(CONCAT(', ', c.addressLine2), ''),
        ', ', c.city,
        IFNULL(CONCAT(', ', c.state), ''),
        ', ', c.country,
        IFNULL(CONCAT(' ', c.postalCode), '')
    ) AS complete_address,
    COUNT(o.orderNumber) AS total_orders
FROM customers c
LEFT JOIN orders o ON c.customerNumber = o.customerNumber
GROUP BY
    c.customerNumber,
    c.customerName,
    c.addressLine1,
    c.addressLine2,
    c.city,
    c.state,
    c.country,
    c.postalCode;


-- Q18. Update the country of a customer (customerNumber = 103)
UPDATE customers
SET country = 'Canada'
WHERE customerNumber = 103;


-- Q19. Delete all payments below 20,000
DELETE FROM payments
WHERE amount < 20000;


-- Q20. Add a new payment manually for an existing customer (customerNumber = 112)
INSERT INTO payments (customerNumber, checkNumber, paymentDate, amount)
VALUES (112, 'CHK-NEW-001', CURDATE(), 75000.00);
