
USE classicmodels;

-- 1. Show all the customers whose creditLimit is greater than 20000
SELECT
  customerNumber,
  customerName,
  creditLimit
FROM customers
WHERE creditLimit > 20000
ORDER BY creditLimit DESC;

-- 2. Show the employees who report to VP Sales.
SELECT
  e.employeeNumber,
  CONCAT(e.firstName, ' ', e.lastName) AS employee_name,
  e.jobTitle,
  e.reportsTo
FROM employees AS e
WHERE e.reportsTo = (
  SELECT employeeNumber
  FROM employees
  WHERE jobTitle = 'VP Sales'
)
ORDER BY e.employeeNumber;

-- 3. Find all the customers who have set their state, live in USA, and have creditLimit between 100000 and 200000.
SELECT
  customerNumber,
  customerName,
  city,
  state,
  country,
  creditLimit
FROM customers
WHERE state IS NOT NULL
  AND country = 'USA'
  AND creditLimit BETWEEN 100000 AND 200000
ORDER BY creditLimit DESC;

-- 4. Find all the employees who report to Sales Managers of all types.
SELECT
  e.employeeNumber,
  CONCAT(e.firstName, ' ', e.lastName) AS employee_name,
  e.jobTitle,
  mgr.employeeNumber AS managerNumber,
  CONCAT(mgr.firstName, ' ', mgr.lastName) AS manager_name,
  mgr.jobTitle AS manager_title
FROM employees AS e
JOIN employees AS mgr
  ON e.reportsTo = mgr.employeeNumber
WHERE mgr.jobTitle LIKE 'Sales Manager%'
ORDER BY mgr.jobTitle, e.employeeNumber;

-- 5. Find the average credit limit of customers of each country.
SELECT
  country,
  ROUND(AVG(creditLimit), 2) AS avg_credit_limit
FROM customers
GROUP BY country
ORDER BY avg_credit_limit DESC;

-- 6. Find the total no. of orders for each date and customer.
--    Show only dates with total number of orders greater than 10 for date and customer.
SELECT
  orderDate,
  customerNumber,
  COUNT(*) AS total_orders
FROM orders
GROUP BY orderDate, customerNumber
HAVING COUNT(*) > 10
ORDER BY orderDate, customerNumber;

-- 7. Find the name of the supervisor, job title of supervisor and total no. of supervisee using subquery (without JOIN).
SELECT
  employeeNumber,
  CONCAT(firstName, ' ', lastName) AS supervisor_name,
  jobTitle,
  (
    SELECT COUNT(*)
    FROM employees AS sub
    WHERE sub.reportsTo = emp.employeeNumber
  ) AS total_supervisee
FROM employees AS emp
WHERE EXISTS (
  SELECT 1
  FROM employees AS sub
  WHERE sub.reportsTo = emp.employeeNumber
)
ORDER BY total_supervisee DESC, employeeNumber;

-- 8. Find the name of the supervisor, job title of supervisor and total no. of supervisee using subquery (with JOIN).
SELECT
  emp.employeeNumber,
  CONCAT(emp.firstName, ' ', emp.lastName) AS supervisor_name,
  emp.jobTitle,
  COUNT(sub.employeeNumber) AS total_supervisee
FROM employees AS emp
JOIN employees AS sub
  ON sub.reportsTo = emp.employeeNumber
GROUP BY emp.employeeNumber, supervisor_name, emp.jobTitle
ORDER BY total_supervisee DESC, emp.employeeNumber;

-- 9. Find all customers with a credit limit greater than average credit limit using WITH clause.
WITH avg_credit AS (
  SELECT AVG(creditLimit) AS avg_limit
  FROM customers
)
SELECT
  customerNumber,
  customerName,
  creditLimit
FROM customers
WHERE creditLimit > (SELECT avg_limit FROM avg_credit)
ORDER BY creditLimit DESC;

-- 10. Find the rank of customer and the customer with the third highest credit limit.
WITH ranked_customers AS (
  SELECT
    customerNumber,
    customerName,
    creditLimit,
    RANK() OVER (ORDER BY creditLimit DESC) AS credit_rank
  FROM customers
)
SELECT
  customerNumber,
  customerName,
  creditLimit,
  credit_rank
FROM ranked_customers
ORDER BY credit_rank, customerNumber;

WITH ranked_customers AS (
  SELECT
    customerNumber,
    customerName,
    creditLimit,
    RANK() OVER (ORDER BY creditLimit DESC) AS credit_rank
  FROM customers
)
SELECT
  customerNumber,
  customerName,
  creditLimit,
  credit_rank
FROM ranked_customers
WHERE credit_rank = 3;

-- 11. Generate a report that shows total no. of employees working in each office.
SELECT
  o.officeCode,
  o.city AS office_name,
  o.state,
  o.country,
  COUNT(e.employeeNumber) AS total_employees
FROM offices AS o
LEFT JOIN employees AS e
  ON o.officeCode = e.officeCode
GROUP BY o.officeCode, o.city, o.state, o.country
ORDER BY total_employees DESC, o.officeCode;

-- 12. Generate a report that shows total no. of customers visited each office.
SELECT
  o.officeCode,
  o.city AS office_name,
  o.state,
  o.country,
  COUNT(c.customerNumber) AS total_customers
FROM offices AS o
LEFT JOIN employees AS e
  ON o.officeCode = e.officeCode
LEFT JOIN customers AS c
  ON e.employeeNumber = c.salesRepEmployeeNumber
GROUP BY o.officeCode, o.city, o.state, o.country
ORDER BY total_customers DESC, o.officeCode;

-- 13. Generate a report that shows total payment received by each office.
SELECT
  o.city AS office_name,
  o.state,
  o.country,
  ROUND(SUM(p.amount), 2) AS total_payments
FROM offices AS o
JOIN employees AS e
  ON o.officeCode = e.officeCode
JOIN customers AS c
  ON e.employeeNumber = c.salesRepEmployeeNumber
JOIN payments AS p
  ON c.customerNumber = p.customerNumber
GROUP BY o.city, o.state, o.country
ORDER BY total_payments DESC;

-- 14. Generate a report that shows total sales(in amount) by each office.
SELECT
  o.city AS office_name,
  o.state,
  o.country,
  ROUND(SUM(od.quantityOrdered * od.priceEach), 2) AS total_sales
FROM offices AS o
JOIN employees AS e
  ON o.officeCode = e.officeCode
JOIN customers AS c
  ON e.employeeNumber = c.salesRepEmployeeNumber
JOIN orders AS ord
  ON c.customerNumber = ord.customerNumber
JOIN orderdetails AS od
  ON ord.orderNumber = od.orderNumber
WHERE ord.status IN ('Shipped', 'Resolved')
GROUP BY o.city, o.state, o.country
ORDER BY total_sales DESC;

-- 15. Generate a report that shows total payment pending for each office.
WITH office_sales AS (
  SELECT
    o.officeCode,
    o.city AS office_name,
    o.state,
    o.country,
    ROUND(SUM(od.quantityOrdered * od.priceEach), 2) AS total_sales
  FROM offices AS o
  JOIN employees AS e
    ON o.officeCode = e.officeCode
  JOIN customers AS c
    ON e.employeeNumber = c.salesRepEmployeeNumber
  JOIN orders AS ord
    ON c.customerNumber = ord.customerNumber
  JOIN orderdetails AS od
    ON ord.orderNumber = od.orderNumber
  WHERE ord.status IN ('Shipped', 'Resolved')
  GROUP BY o.officeCode, o.city, o.state, o.country
), office_payments AS (
  SELECT
    o.officeCode,
    ROUND(SUM(p.amount), 2) AS total_payments
  FROM offices AS o
  JOIN employees AS e
    ON o.officeCode = e.officeCode
  JOIN customers AS c
    ON e.employeeNumber = c.salesRepEmployeeNumber
  JOIN payments AS p
    ON c.customerNumber = p.customerNumber
  GROUP BY o.officeCode
)
SELECT
  s.office_name,
  s.state,
  s.country,
  s.total_sales,
  COALESCE(p.total_payments, 0) AS total_payments,
  ROUND(s.total_sales - COALESCE(p.total_payments, 0), 2) AS total_payment_pending
FROM office_sales AS s
LEFT JOIN office_payments AS p
  ON s.officeCode = p.officeCode
ORDER BY total_payment_pending DESC;

-- 16. Find the creditLimit of each person and proportion of creditLimit of each person in each country.
SELECT
  customerNumber,
  customerName,
  country,
  creditLimit,
  ROUND(creditLimit / SUM(creditLimit) OVER (PARTITION BY country), 4) AS credit_proportion_in_country
FROM customers
ORDER BY country, creditLimit DESC;

-- 17. Create a view showing the customer name, complete address, and their total number of orders.
CREATE OR REPLACE VIEW customer_order_summary AS
SELECT
  c.customerNumber,
  c.customerName,
  CONCAT_WS(', ', c.addressLine1, c.addressLine2, c.city, c.state, c.postalCode, c.country) AS complete_address,
  COUNT(o.orderNumber) AS total_orders
FROM customers AS c
LEFT JOIN orders AS o
  ON c.customerNumber = o.customerNumber
GROUP BY c.customerNumber, c.customerName, complete_address;

SELECT *
FROM customer_order_summary
ORDER BY total_orders DESC, customerName;

-- 18. Update the country of a customer (example record).
UPDATE customers
SET country = 'Canada'
WHERE customerNumber = 103;

-- 19. Delete all payments below 20,000.
DELETE FROM payments
WHERE amount < 20000;

-- 20. Add new payments manually for an existing customer.
INSERT INTO payments (customerNumber, checkNumber, paymentDate, amount)
VALUES
  (103, 'NEWCHK001', '2026-05-04', 25000.00),
  (103, 'NEWCHK002', '2026-05-04', 32000.00);
