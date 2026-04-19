# Sales ETL Test Case Query Results

Workbook: `C:\Users\prasanna.mahale\PycharmProjects\PEI\qa_output\Test_Cases_ETL_Sales_and_Validation.xlsx`
Worksheet: `Test Cases`

The source files were loaded into an in-memory SQLite database with tables:
- `customers`
- `orders`
- `shipping`

## 1. Source File Availability

**Description:** Verify all required source files are present and readable before the ETL process starts.

**Expectation:** Customer, Order, and Shipping source files should be available at the configured path and the ETL process should fail fast if any file is missing.

**SQL:** `N/A - Pre-load file system validation.`

**Result:** Not applicable.

## 2. Customer Schema Validation

**Description:** Verify the customer source contains the required columns Customer_ID, First, Last, Age, and Country after load.

**Expectation:** All mandatory customer columns should exist with the expected mapping in the loaded table.

**Statement 1:**

```sql
PRAGMA table_info(customers);
```

| cid | name | type | notnull | dflt_value | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | customer_id | INTEGER | 0 | NULL | 0 |
| 1 | first_name | TEXT | 0 | NULL | 0 |
| 2 | last_name | TEXT | 0 | NULL | 0 |
| 3 | age | INTEGER | 0 | NULL | 0 |
| 4 | country | TEXT | 0 | NULL | 0 |

## 3. Order Schema Validation

**Description:** Verify the order source contains the required columns Order_ID, Item, Amount, and Customer_ID after load.

**Expectation:** All mandatory order columns should exist with the expected mapping in the loaded table.

**Statement 1:**

```sql
PRAGMA table_info(orders);
```

| cid | name | type | notnull | dflt_value | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | order_id | INTEGER | 0 | NULL | 0 |
| 1 | item | TEXT | 0 | NULL | 0 |
| 2 | amount | INTEGER | 0 | NULL | 0 |
| 3 | customer_id | INTEGER | 0 | NULL | 0 |

## 4. Shipping Schema Validation

**Description:** Verify the shipping source contains the required columns Shipping_ID, Status, and Customer_ID after load.

**Expectation:** All mandatory shipping columns should exist with the expected mapping in the loaded table.

**Statement 1:**

```sql
PRAGMA table_info(shipping);
```

| cid | name | type | notnull | dflt_value | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | shipping_id | INTEGER | 0 | NULL | 0 |
| 1 | status | TEXT | 0 | NULL | 0 |
| 2 | customer_id | INTEGER | 0 | NULL | 0 |

## 5. Row Count Reconciliation

**Description:** Verify the row count loaded into each table matches the source row count for a complete ETL load.

**Expectation:** Loaded row counts should match the source row counts for customer, order, and shipping datasets.

**Statement 1:**

```sql
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'orders' AS table_name, COUNT(*) AS row_count FROM orders
UNION ALL
SELECT 'shipping' AS table_name, COUNT(*) AS row_count FROM shipping;
```

| table_name | row_count |
| --- | --- |
| customers | 250 |
| orders | 250 |
| shipping | 250 |

## 6. Customer ID Uniqueness

**Description:** Verify Customer_ID is unique in the customer dataset.

**Expectation:** No duplicate Customer_ID values should exist in customers.

**Statement 1:**

```sql
SELECT customer_id, COUNT(*) AS duplicate_count
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

_No rows returned._

## 7. Order ID Uniqueness

**Description:** Verify Order_ID is unique in the order dataset.

**Expectation:** No duplicate Order_ID values should exist in orders.

**Statement 1:**

```sql
SELECT order_id, COUNT(*) AS duplicate_count
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;
```

_No rows returned._

## 8. Shipping ID Uniqueness

**Description:** Verify Shipping_ID is unique in the shipping dataset.

**Expectation:** No duplicate Shipping_ID values should exist in shipping.

**Statement 1:**

```sql
SELECT shipping_id, COUNT(*) AS duplicate_count
FROM shipping
GROUP BY shipping_id
HAVING COUNT(*) > 1;
```

_No rows returned._

## 9. Mandatory Field Null Check

**Description:** Verify mandatory columns in customer, order, and shipping datasets do not contain NULL values.

**Expectation:** All mandatory business key and reporting columns should be populated.

**Statement 1:**

```sql
SELECT 'customers' AS table_name, COUNT(*) AS null_count
FROM customers
WHERE customer_id IS NULL OR first_name IS NULL OR last_name IS NULL OR age IS NULL OR country IS NULL
UNION ALL
SELECT 'orders' AS table_name, COUNT(*) AS null_count
FROM orders
WHERE order_id IS NULL OR item IS NULL OR amount IS NULL OR customer_id IS NULL
UNION ALL
SELECT 'shipping' AS table_name, COUNT(*) AS null_count
FROM shipping
WHERE shipping_id IS NULL OR status IS NULL OR customer_id IS NULL;
```

| table_name | null_count |
| --- | --- |
| customers | 0 |
| orders | 0 |
| shipping | 0 |

## 10. Shipping Status Domain Check

**Description:** Verify shipping status contains only valid business values.

**Expectation:** Status values should be restricted to the approved delivery statuses such as Pending or Delivered.

**Statement 1:**

```sql
SELECT DISTINCT status
FROM shipping
WHERE status NOT IN ('Pending', 'Delivered');
```

_No rows returned._

## 11. Numeric Value Validation

**Description:** Verify Age and Amount contain valid positive business values within the accepted range.

**Expectation:** Age should be greater than 0 and within a realistic range, and Amount should be greater than 0.

**Statement 1:**

```sql
SELECT 'customers' AS table_name, COUNT(*) AS invalid_count
FROM customers
WHERE age <= 0 OR age > 100
UNION ALL
SELECT 'orders' AS table_name, COUNT(*) AS invalid_count
FROM orders
WHERE amount <= 0;
```

| table_name | invalid_count |
| --- | --- |
| customers | 0 |
| orders | 0 |

## 12. Customer Order Referential Integrity

**Description:** Verify every order record has a valid matching customer record.

**Expectation:** All order rows should resolve to a valid customer in the customer master dataset.

**Statement 1:**

```sql
SELECT COUNT(*) AS orphan_order_rows
FROM orders o
LEFT JOIN customers c
    ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL;
```

| orphan_order_rows |
| --- |
| 0 |

## 13. Customer Shipping Referential Integrity

**Description:** Verify every shipping record has a valid matching customer record.

**Expectation:** All shipping rows should resolve to a valid customer in the customer master dataset.

**Statement 1:**

```sql
SELECT COUNT(*) AS orphan_shipping_rows
FROM shipping s
LEFT JOIN customers c
    ON c.customer_id = s.customer_id
WHERE c.customer_id IS NULL;
```

| orphan_shipping_rows |
| --- |
| 0 |

## 14. Order Shipping Link Availability

**Description:** Verify shipping data contains an order-level business key to map delivery status to transaction spend without duplication.

**Expectation:** Shipping should contain Order_ID or another unique transaction reference; without it, spend by delivery status is assumption-based and should be flagged.

**Statement 1:**

```sql
PRAGMA table_info(shipping);
```

| cid | name | type | notnull | dflt_value | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | shipping_id | INTEGER | 0 | NULL | 0 |
| 1 | status | TEXT | 0 | NULL | 0 |
| 2 | customer_id | INTEGER | 0 | NULL | 0 |

**Statement 2:**

```sql
SELECT customer_id, COUNT(*) AS shipment_rows
FROM shipping
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

| customer_id | shipment_rows |
| --- | --- |
| 3 | 2 |
| 8 | 2 |
| 9 | 3 |
| 10 | 2 |
| 12 | 2 |
| 15 | 3 |
| 21 | 2 |
| 22 | 3 |
| 24 | 2 |
| 26 | 2 |
| 27 | 3 |
| 30 | 3 |
| 35 | 4 |
| 37 | 3 |
| 38 | 2 |
| 40 | 3 |
| 47 | 2 |
| 50 | 2 |
| 58 | 2 |
| 67 | 3 |
| 69 | 3 |
| 72 | 2 |
| 77 | 2 |
| 85 | 3 |
| 86 | 2 |
| 90 | 2 |
| 91 | 3 |
| 100 | 3 |
| 106 | 3 |
| 112 | 2 |
| 118 | 2 |
| 120 | 2 |
| 128 | 3 |
| 129 | 2 |
| 135 | 2 |
| 137 | 3 |
| 140 | 2 |
| 141 | 2 |
| 143 | 2 |
| 154 | 2 |
| 155 | 2 |
| 156 | 2 |
| 157 | 2 |
| 158 | 2 |
| 161 | 2 |
| 171 | 2 |
| 173 | 4 |
| 177 | 2 |
| 185 | 4 |
| 189 | 4 |
| 190 | 2 |
| 192 | 2 |
| 193 | 2 |
| 195 | 3 |
| 199 | 3 |
| 204 | 2 |
| 205 | 2 |
| 214 | 2 |
| 216 | 3 |
| 219 | 3 |
| 220 | 2 |
| 226 | 2 |
| 232 | 2 |
| 234 | 3 |
| 236 | 2 |
| 242 | 3 |
| 248 | 2 |

## 15. Pending Spend By Country

**Description:** Verify the total amount spent and country for records with Pending delivery status.

**Expectation:** Pending delivery spend should be aggregated accurately by country only when a valid order-to-shipping join key is available.

**Statement 1:**

```sql
SELECT
    c.country,
    COUNT(*) AS pending_transactions,
    ROUND(SUM(o.amount), 2) AS total_amount_spent
FROM orders o
INNER JOIN customers c
    ON c.customer_id = o.customer_id
INNER JOIN shipping s
    ON s.customer_id = o.customer_id
WHERE s.status = 'Pending'
GROUP BY c.country
ORDER BY total_amount_spent DESC, c.country;
```

| country | pending_transactions | total_amount_spent |
| --- | --- | --- |
| UK | 52 | 136300.0 |
| USA | 55 | 65500.0 |
| UAE | 37 | 53800.0 |

## 16. Customer Sales Summary

**Description:** Verify total transactions, total amount spent, and product details are generated correctly for each customer.

**Expectation:** Each customer should appear with aggregated transaction count, amount spent, and product details; customers with no orders should be handled as per business rule.

**Statement 1:**

```sql
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.country,
    COUNT(o.order_id) AS total_transactions,
    ROUND(COALESCE(SUM(o.amount), 0), 2) AS total_amount_spent,
    COALESCE(GROUP_CONCAT(o.item, ', '), 'No products') AS product_details
FROM customers c
LEFT JOIN orders o
    ON o.customer_id = c.customer_id
GROUP BY c.customer_id, customer_name, c.country
ORDER BY total_amount_spent DESC, c.customer_id;
```

| customer_id | customer_name | country | total_transactions | total_amount_spent | product_details |
| --- | --- | --- | --- | --- | --- |
| 166 | Morgan Cooper | USA | 3 | 17350.0 | Monitor, Harddisk, Webcam |
| 123 | Philip Robinson | UK | 2 | 17000.0 | Harddisk, Monitor |
| 129 | Amber Banks | UK | 2 | 17000.0 | Monitor, Harddisk |
| 96 | Eric Harvey | USA | 4 | 14700.0 | Mouse, Headset, DDR RAM, Monitor |
| 193 | Yesenia White | UK | 4 | 13950.0 | Monitor, Mousepad, DDR RAM, Mousepad |
| 229 | Philip Newton | UK | 3 | 13700.0 | Monitor, Mousepad, DDR RAM |
| 13 | Omar Martin | UK | 3 | 13300.0 | Headset, Monitor, Keyboard |
| 23 | Margaret Hardy | UK | 3 | 12800.0 | Keyboard, Monitor, Keyboard |
| 92 | Paul Brown | USA | 3 | 12750.0 | Webcam, Monitor, Keyboard |
| 143 | Stacey Welch | UK | 3 | 12650.0 | Mouse, Monitor, Webcam |
| 221 | Sarah Gilbert | USA | 3 | 12650.0 | Monitor, Mousepad, Keyboard |
| 151 | Javier Jones | USA | 3 | 12600.0 | Monitor, Keyboard, Mousepad |
| 98 | Steve Braun | UK | 3 | 12500.0 | Mousepad, Monitor, Mouse |
| 55 | Christy Rodriguez | UAE | 2 | 12400.0 | Keyboard, Monitor |
| 118 | R0bert Shepherd | UK | 2 | 12400.0 | Keyboard, Monitor |
| 167 | Matthew Stokes | USA | 2 | 12400.0 | Keyboard, Monitor |
| 239 | Janet Holmes | UK | 2 | 12400.0 | Monitor, Keyboard |
| 68 | Regina Wong | UK | 2 | 12300.0 | Monitor, Mouse |
| 49 | Erin Taylor | UK | 1 | 12000.0 | Monitor |
| 61 | Jade Wall | USA | 1 | 12000.0 | Monitor |
| 131 | Miranda Williams | USA | 1 | 12000.0 | Monitor |
| 158 | Zachary Williams | UK | 1 | 12000.0 | Monitor |
| 206 | Courtney Lopez | USA | 1 | 12000.0 | Monitor |
| 207 | Chelsea Moyer | USA | 1 | 12000.0 | Monitor |
| 242 | Mark R0berts | USA | 1 | 12000.0 | Monitor |
| 57 | Lacey Mercado | USA | 3 | 6700.0 | Mousepad, Harddisk, DDR RAM |
| 119 | Robin Snyder | UK | 2 | 6500.0 | DDR RAM, Harddisk |
| 164 | Sandra Mcmahon | UK | 2 | 6500.0 | Harddisk, DDR RAM |
| 159 | Brooke Durham | UK | 2 | 5900.0 | Headset, Harddisk |
| 247 | John Miller | USA | 3 | 5650.0 | Keyboard, Harddisk, Mousepad |
| 85 | Michele Maxwell | UAE | 2 | 5400.0 | Keyboard, Harddisk |
| 181 | Adrian West | USA | 2 | 5400.0 | Harddisk, Keyboard |
| 124 | Rachel Larson | UK | 2 | 5350.0 | Webcam, Harddisk |
| 47 | Carolyn Green | USA | 2 | 5300.0 | Harddisk, Mouse |
| 186 | Xavier Miles | USA | 2 | 5250.0 | Mousepad, Harddisk |
| 12 | Jodi Gonzalez | USA | 1 | 5000.0 | Harddisk |
| 30 | Michael Mann | UAE | 1 | 5000.0 | Harddisk |
| 38 | Michael Williams | UK | 1 | 5000.0 | Harddisk |
| 52 | Haley Martinez | USA | 1 | 5000.0 | Harddisk |
| 56 | Jose Poole | USA | 1 | 5000.0 | Harddisk |
| 65 | David Fritz | UAE | 1 | 5000.0 | Harddisk |
| 71 | Michelle Edwards | USA | 1 | 5000.0 | Harddisk |
| 75 | Allen Wright | UAE | 1 | 5000.0 | Harddisk |
| 81 | Allison Sweeney | USA | 1 | 5000.0 | Harddisk |
| 102 | Jessica Welch | USA | 1 | 5000.0 | Harddisk |
| 196 | Taylor Reed | USA | 1 | 5000.0 | Harddisk |
| 228 | Andrea Velasquez | UK | 1 | 5000.0 | Harddisk |
| 223 | Megan Morris | UK | 3 | 3300.0 | Headset, DDR RAM, Headset |
| 249 | Patricia Garcia | UK | 4 | 2850.0 | Headset, DDR RAM, Mousepad, Mousepad |
| 86 | Emily Thomas | USA | 3 | 2800.0 | Keyboard, DDR RAM, Headset |
| 8 | Jason Montgomery | UK | 4 | 2300.0 | Mousepad, DDR RAM, Webcam, Mousepad |
| 172 | Jeffrey Diaz | USA | 3 | 2000.0 | Mousepad, Mousepad, DDR RAM |
| 99 | Ryan Rojas | UK | 2 | 1900.0 | DDR RAM, Keyboard |
| 67 | Guy Bennett | USA | 2 | 1800.0 | Mouse, DDR RAM |
| 97 | Debbie Rogers | USA | 2 | 1800.0 | Mouse, DDR RAM |
| 107 | Breanna Santos | USA | 2 | 1750.0 | Mousepad, DDR RAM |
| 176 | Tiffany Bowers | USA | 2 | 1750.0 | Mousepad, DDR RAM |
| 195 | Christopher Doyle | UAE | 2 | 1700.0 | Mousepad, DDR RAM |
| 89 | David Yoder | UK | 3 | 1600.0 | Mouse, Headset, Keyboard |
| 101 | Brian Olson | USA | 3 | 1600.0 | Webcam, Webcam, Headset |
| 157 | Sharon Warner | USA | 3 | 1550.0 | Mouse, Headset, Webcam |
| 5 | William Jackson | UAE | 1 | 1500.0 | DDR RAM |
| 20 | Derek Peterson | UAE | 1 | 1500.0 | DDR RAM |
| 33 | Erica Owens | UK | 1 | 1500.0 | DDR RAM |
| 40 | Jonathan Middleton | UAE | 1 | 1500.0 | DDR RAM |
| 136 | Natalie Page | USA | 1 | 1500.0 | DDR RAM |
| 184 | Anthony Nicholson | UK | 1 | 1500.0 | DDR RAM |
| 194 | Nancy Miller | UK | 1 | 1500.0 | DDR RAM |
| 236 | Al1cia Jensen | USA | 1 | 1500.0 | DDR RAM |
| 70 | Juan Cruz | UAE | 4 | 1450.0 | Keyboard, Mousepad, Keyboard, Keyboard |
| 238 | Kyle Ruiz | UK | 2 | 1200.0 | Headset, Mouse |
| 50 | Charles Garcia | UAE | 2 | 1150.0 | Headset, Mousepad |
| 134 | James Keith | UK | 3 | 1050.0 | Keyboard, Mouse, Webcam |
| 32 | Tiffany Carter | USA | 1 | 900.0 | Headset |
| 106 | Veronica Stein | USA | 1 | 900.0 | Headset |
| 111 | Audrey Richardson | USA | 1 | 900.0 | Headset |
| 138 | Brian Bowman | UK | 1 | 900.0 | Headset |
| 150 | Sherry Parsons | UAE | 1 | 900.0 | Headset |
| 161 | Gabrielle Smith | USA | 1 | 900.0 | Headset |
| 178 | Christine Smith | UK | 1 | 900.0 | Headset |
| 197 | Katherine Ferguson | USA | 1 | 900.0 | Headset |
| 214 | N!cole Mcintyre | UK | 1 | 900.0 | Headset |
| 225 | Michael Phelps | UAE | 1 | 900.0 | Headset |
| 231 | Eric Levine | USA | 1 | 900.0 | Headset |
| 244 | Mark Rivers | UK | 1 | 900.0 | Headset |
| 246 | Justin Stewart | USA | 1 | 900.0 | Headset |
| 63 | Sarah Greer | UK | 3 | 850.0 | Mousepad, Webcam, Mouse |
| 153 | Janet Valdez | UK | 3 | 850.0 | Keyboard, Mousepad, Mousepad |
| 146 | Terry Bailey | USA | 2 | 800.0 | Keyboard, Keyboard |
| 87 | Mark Rogers | USA | 2 | 750.0 | Keyboard, Webcam |
| 235 | Melissa Gaines | UAE | 2 | 750.0 | Keyboard, Webcam |
| 60 | Jeremy Rodriguez | UAE | 2 | 700.0 | Webcam, Webcam |
| 78 | Thomas Wood | UK | 2 | 700.0 | Webcam, Webcam |
| 190 | Grace Hartman | UAE | 2 | 700.0 | Keyboard, Mouse |
| 24 | Arthur Hayes | UK | 2 | 650.0 | Keyboard, Mousepad |
| 53 | Adam Holmes | UK | 2 | 650.0 | Keyboard, Mousepad |
| 103 | Stephanie Faulkner | UK | 2 | 650.0 | Webcam, Mouse |
| 198 | R0bert Bryan | UK | 2 | 650.0 | Mousepad, Keyboard |
| 208 | Brittany Golden | UK | 2 | 650.0 | Keyboard, Mousepad |
| 200 | Rebecca Robinson | UAE | 2 | 600.0 | Keyboard, Mousepad |
| 10 | Darrell Dillon | UAE | 1 | 400.0 | Keyboard |
| 28 | Jonathan Manning | UK | 1 | 400.0 | Keyboard |
| 35 | Brian Palmer | UAE | 1 | 400.0 | Keyboard |
| 39 | Ruth Smith | UK | 1 | 400.0 | Keyboard |
| 59 | Amanda Cohen | UK | 1 | 400.0 | Keyboard |
| 69 | Desiree Webster | UK | 1 | 400.0 | Keyboard |
| 80 | Kevin Watkins | UAE | 1 | 400.0 | Keyboard |
| 109 | R0bert Moore | UK | 1 | 400.0 | Keyboard |
| 112 | Maureen Bryant | USA | 1 | 400.0 | Keyboard |
| 114 | Jeffrey Sullivan | UK | 1 | 400.0 | Keyboard |
| 126 | Aimee Jacobs | USA | 1 | 400.0 | Keyboard |
| 139 | Ryan Martin | UK | 1 | 400.0 | Keyboard |
| 162 | N!cole Bennett | USA | 1 | 400.0 | Keyboard |
| 171 | L@rry Cole | USA | 1 | 400.0 | Keyboard |
| 215 | Vincent Kline | UAE | 1 | 400.0 | Keyboard |
| 224 | Zachary Davis | UK | 1 | 400.0 | Keyboard |
| 226 | Christopher Robinson | USA | 1 | 400.0 | Keyboard |
| 234 | Diane Tanner | UK | 1 | 400.0 | Keyboard |
| 243 | Alejandro Bailey | UK | 1 | 400.0 | Keyboard |
| 15 | Jason Brown | UAE | 1 | 350.0 | Webcam |
| 17 | Kimberly Mora | USA | 1 | 350.0 | Webcam |
| 108 | Jeremy Lee | UK | 1 | 350.0 | Webcam |
| 117 | Steven Black | USA | 1 | 350.0 | Webcam |
| 135 | Shawn Johnson | UAE | 1 | 350.0 | Webcam |
| 163 | Heather Ali | UK | 1 | 350.0 | Webcam |
| 201 | Bethany Anderson | USA | 1 | 350.0 | Webcam |
| 232 | Michael Lopez | USA | 1 | 350.0 | Webcam |
| 73 | Laura House | UK | 1 | 300.0 | Mouse |
| 84 | John Bennett | UK | 1 | 300.0 | Mouse |
| 122 | Charles Nunez | USA | 1 | 300.0 | Mouse |
| 145 | Michael Case | UAE | 1 | 300.0 | Mouse |
| 156 | Jessica Marshall | USA | 1 | 300.0 | Mouse |
| 174 | Emily Jones | UK | 1 | 300.0 | Mouse |
| 180 | Brenda Lewis | UAE | 1 | 300.0 | Mouse |
| 183 | April Beck | UK | 1 | 300.0 | Mouse |
| 192 | David Arnold | USA | 1 | 300.0 | Mouse |
| 218 | Thomas Mclaughlin | UK | 1 | 300.0 | Mouse |
| 250 | Stephen Jones | USA | 1 | 300.0 | Mouse |
| 37 | Connor Adams | USA | 1 | 250.0 | Mousepad |
| 66 | Hannah Wu | USA | 1 | 250.0 | Mousepad |
| 95 | Alyssa Walker | UAE | 1 | 250.0 | Mousepad |
| 113 | Derrick R0berts | UK | 1 | 250.0 | Mousepad |
| 125 | Stephen Sharp | UAE | 1 | 250.0 | Mousepad |
| 202 | Mary Williams | USA | 1 | 250.0 | Mousepad |
| 203 | Carlos Wallace | UK | 1 | 250.0 | Mousepad |
| 209 | Russell Berry | UK | 1 | 250.0 | Mousepad |
| 4 | Eric Carter | UK | 1 | 200.0 | Mousepad |
| 29 | Angela Bryant | UK | 1 | 200.0 | Mousepad |
| 64 | Sandra Golden | UK | 1 | 200.0 | Mousepad |
| 91 | Stephanie Hicks | USA | 1 | 200.0 | Mousepad |
| 94 | Krystal Carroll | UK | 1 | 200.0 | Mousepad |
| 105 | Monique Wright | UAE | 1 | 200.0 | Mousepad |
| 110 | Tiffany Pearson | UAE | 1 | 200.0 | Mousepad |
| 144 | Brett Burns | UK | 1 | 200.0 | Mousepad |
| 152 | Jill Kane | USA | 1 | 200.0 | Mousepad |
| 177 | Linda Craig | USA | 1 | 200.0 | Mousepad |
| 188 | Michele Rogers | UK | 1 | 200.0 | Mousepad |
| 191 | Joseph Miller | USA | 1 | 200.0 | Mousepad |
| 211 | Al1cia Thompson | USA | 1 | 200.0 | Mousepad |
| 222 | Jeremy Andrews | USA | 1 | 200.0 | Mousepad |
| 1 | Joseph Rice | USA | 0 | 0.0 | No products |
| 2 | Gary Moore | USA | 0 | 0.0 | No products |
| 3 | John Walker | UK | 0 | 0.0 | No products |
| 6 | N!cole Jones | USA | 0 | 0.0 | No products |
| 7 | David Davis | USA | 0 | 0.0 | No products |
| 9 | Kent Weaver | UK | 0 | 0.0 | No products |
| 11 | Jacqueline Wang | USA | 0 | 0.0 | No products |
| 14 | N!cole Lara | UK | 0 | 0.0 | No products |
| 16 | David Benson | USA | 0 | 0.0 | No products |
| 18 | Erik Macias | UK | 0 | 0.0 | No products |
| 19 | James Johnson | UK | 0 | 0.0 | No products |
| 21 | Diane Henson | USA | 0 | 0.0 | No products |
| 22 | Cody Lyons | USA | 0 | 0.0 | No products |
| 25 | Raymond Taylor | UAE | 0 | 0.0 | No products |
| 26 | Tina Moore | USA | 0 | 0.0 | No products |
| 27 | Kylie White | USA | 0 | 0.0 | No products |
| 31 | Craig Myers | USA | 0 | 0.0 | No products |
| 34 | Patricia Parker | UK | 0 | 0.0 | No products |
| 36 | Melissa Smith | USA | 0 | 0.0 | No products |
| 41 | Francis Velez | USA | 0 | 0.0 | No products |
| 42 | Matthew Velez | USA | 0 | 0.0 | No products |
| 43 | Kim Shaw | UK | 0 | 0.0 | No products |
| 44 | Gary Jones | UK | 0 | 0.0 | No products |
| 45 | Nicholas Clayton | UAE | 0 | 0.0 | No products |
| 46 | Anthony Chavez | USA | 0 | 0.0 | No products |
| 48 | Janice Roman | UK | 0 | 0.0 | No products |
| 51 | John Huber | USA | 0 | 0.0 | No products |
| 54 | Patricia Jones | UK | 0 | 0.0 | No products |
| 58 | Danielle Garcia | UK | 0 | 0.0 | No products |
| 62 | Janice Garcia | USA | 0 | 0.0 | No products |
| 72 | Alexander Griffin | USA | 0 | 0.0 | No products |
| 74 | Brittany Hanna | UK | 0 | 0.0 | No products |
| 76 | Ricky Phillips | USA | 0 | 0.0 | No products |
| 77 | Adrian Cross | USA | 0 | 0.0 | No products |
| 79 | Jillian Massey | UK | 0 | 0.0 | No products |
| 82 | Joseph Hernandez | USA | 0 | 0.0 | No products |
| 83 | Steven Little | UK | 0 | 0.0 | No products |
| 88 | John Cruz | UK | 0 | 0.0 | No products |
| 90 | James Reynolds | UAE | 0 | 0.0 | No products |
| 93 | Alexandra Morales | UK | 0 | 0.0 | No products |
| 100 | Andrew Levine | UAE | 0 | 0.0 | No products |
| 104 | Dawn Johnson | UK | 0 | 0.0 | No products |
| 115 | Amy Harris | UAE | 0 | 0.0 | No products |
| 116 | Rhonda Flores | USA | 0 | 0.0 | No products |
| 120 | Elijah Cook | UAE | 0 | 0.0 | No products |
| 121 | Dennis Hill | USA | 0 | 0.0 | No products |
| 127 | Brittany Miller | USA | 0 | 0.0 | No products |
| 128 | Sabrina Mclaughlin | UK | 0 | 0.0 | No products |
| 130 | Casey Todd | UAE | 0 | 0.0 | No products |
| 132 | Alexander Williams | USA | 0 | 0.0 | No products |
| 133 | Jesus Higgins | UK | 0 | 0.0 | No products |
| 137 | Zachary Fowler | USA | 0 | 0.0 | No products |
| 140 | Jennifer Silva | UAE | 0 | 0.0 | No products |
| 141 | Joseph Sparks | USA | 0 | 0.0 | No products |
| 142 | Mary Bishop | USA | 0 | 0.0 | No products |
| 147 | Christopher Mcdonald | USA | 0 | 0.0 | No products |
| 148 | Andres Becker | UK | 0 | 0.0 | No products |
| 149 | Chase Mcdaniel | UK | 0 | 0.0 | No products |
| 154 | Karen Ford | UK | 0 | 0.0 | No products |
| 155 | Jamie Johnson | UAE | 0 | 0.0 | No products |
| 160 | Ryan Murray | UAE | 0 | 0.0 | No products |
| 165 | Bailey Mercado | UAE | 0 | 0.0 | No products |
| 168 | Timothy Mullins | UK | 0 | 0.0 | No products |
| 169 | Kenneth Rubio | UK | 0 | 0.0 | No products |
| 170 | Mary Zamora | UAE | 0 | 0.0 | No products |
| 173 | Joseph Brown | UK | 0 | 0.0 | No products |
| 175 | Tara Davis | UAE | 0 | 0.0 | No products |
| 179 | Matthew Williams | UK | 0 | 0.0 | No products |
| 182 | Amy Scott | USA | 0 | 0.0 | No products |
| 185 | Shari Garcia | UAE | 0 | 0.0 | No products |
| 187 | Rachael Gilbert | USA | 0 | 0.0 | No products |
| 189 | Derek Dixon | UK | 0 | 0.0 | No products |
| 199 | Zachary Kane | UK | 0 | 0.0 | No products |
| 204 | Rhonda Matthews | UK | 0 | 0.0 | No products |
| 205 | Donald Barker | UAE | 0 | 0.0 | No products |
| 210 | Joshua Jackson | UAE | 0 | 0.0 | No products |
| 212 | Clifford Gray | USA | 0 | 0.0 | No products |
| 213 | Gloria Miller | UK | 0 | 0.0 | No products |
| 216 | Amber Hunter | USA | 0 | 0.0 | No products |
| 217 | Shelby Gomez | USA | 0 | 0.0 | No products |
| 219 | Nathan Graham | UK | 0 | 0.0 | No products |
| 220 | Thomas Guzman | UAE | 0 | 0.0 | No products |
| 227 | Aaron Mckee | USA | 0 | 0.0 | No products |
| 230 | Kathleen Palmer | UAE | 0 | 0.0 | No products |
| 233 | Samantha Smith | UK | 0 | 0.0 | No products |
| 237 | Donna Bird | USA | 0 | 0.0 | No products |
| 240 | Edward Bray | UAE | 0 | 0.0 | No products |
| 241 | Brenda Hines | USA | 0 | 0.0 | No products |
| 245 | Christopher Miles | UAE | 0 | 0.0 | No products |
| 248 | Thomas Hickman | UK | 0 | 0.0 | No products |

## 17. Quantity Field Availability

**Description:** Verify the transactional source contains a quantity field to support total quantity sold reporting.

**Expectation:** A quantity column should exist in the order-level dataset; if it is missing, total quantity sold cannot be validated and should be raised as a requirement gap.

**Statement 1:**

```sql
PRAGMA table_info(orders);
```

| cid | name | type | notnull | dflt_value | pk |
| --- | --- | --- | --- | --- | --- |
| 0 | order_id | INTEGER | 0 | NULL | 0 |
| 1 | item | TEXT | 0 | NULL | 0 |
| 2 | amount | INTEGER | 0 | NULL | 0 |
| 3 | customer_id | INTEGER | 0 | NULL | 0 |

## 18. Top Product By Country

**Description:** Verify the maximum product purchased is identified correctly for each country.

**Expectation:** The highest purchased product per country should be returned based on the approved purchase definition.

**Statement 1:**

```sql
WITH country_product AS (
    SELECT
        c.country,
        o.item,
        COUNT(*) AS transaction_count,
        ROUND(SUM(o.amount), 2) AS total_sales_amount,
        DENSE_RANK() OVER (
            PARTITION BY c.country
            ORDER BY COUNT(*) DESC
        ) AS product_rank
    FROM orders o
    INNER JOIN customers c
        ON c.customer_id = o.customer_id
    GROUP BY c.country, o.item
)
SELECT
    country,
    item,
    transaction_count,
    total_sales_amount
FROM country_product
WHERE product_rank = 1
ORDER BY country, item;
```

| country | item | transaction_count | total_sales_amount |
| --- | --- | --- | --- |
| UAE | Keyboard | 12 | 4800.0 |
| UK | Mousepad | 24 | 5350.0 |
| USA | Mousepad | 18 | 4100.0 |

## 19. Top Product By Age Category

**Description:** Verify the most purchased product is identified correctly for customers below 30 years and for customers 30 years and above.

**Expectation:** The highest purchased product should be returned separately for age category less than 30 and age category 30 and above.

**Statement 1:**

```sql
WITH age_product AS (
    SELECT
        CASE WHEN c.age < 30 THEN 'Less than 30' ELSE '30 and above' END AS age_category,
        o.item,
        COUNT(*) AS transaction_count,
        ROUND(SUM(o.amount), 2) AS total_sales_amount,
        DENSE_RANK() OVER (
            PARTITION BY CASE WHEN c.age < 30 THEN 'Less than 30' ELSE '30 and above' END
            ORDER BY COUNT(*) DESC
        ) AS product_rank
    FROM orders o
    INNER JOIN customers c
        ON c.customer_id = o.customer_id
    GROUP BY age_category, o.item
)
SELECT
    age_category,
    item,
    transaction_count,
    total_sales_amount
FROM age_product
WHERE product_rank = 1
ORDER BY age_category;
```

| age_category | item | transaction_count | total_sales_amount |
| --- | --- | --- | --- |
| 30 and above | Keyboard | 35 | 14000.0 |
| Less than 30 | Mousepad | 17 | 3900.0 |

## 20. Minimum Transaction Country

**Description:** Verify the country with the minimum number of transactions is identified correctly.

**Expectation:** The output should return the country with the lowest transaction count after aggregation.

**Statement 1:**

```sql
WITH country_summary AS (
    SELECT
        c.country,
        COUNT(*) AS total_transactions,
        ROUND(SUM(o.amount), 2) AS total_sales_amount
    FROM orders o
    INNER JOIN customers c
        ON c.customer_id = o.customer_id
    GROUP BY c.country
)
SELECT
    country,
    total_transactions,
    total_sales_amount
FROM country_summary
ORDER BY total_transactions ASC, total_sales_amount ASC, country
LIMIT 1;
```

| country | total_transactions | total_sales_amount |
| --- | --- | --- |
| UAE | 40 | 49950.0 |

## 21. Minimum Sales Country

**Description:** Verify the country with the minimum sales amount is identified correctly.

**Expectation:** The output should return the country with the lowest aggregated sales amount.

**Statement 1:**

```sql
WITH country_summary AS (
    SELECT
        c.country,
        COUNT(*) AS total_transactions,
        ROUND(SUM(o.amount), 2) AS total_sales_amount
    FROM orders o
    INNER JOIN customers c
        ON c.customer_id = o.customer_id
    GROUP BY c.country
)
SELECT
    country,
    total_transactions,
    total_sales_amount
FROM country_summary
ORDER BY total_sales_amount ASC, total_transactions ASC, country
LIMIT 1;
```

| country | total_transactions | total_sales_amount |
| --- | --- | --- |
| UAE | 40 | 49950.0 |

## 22. Purchased Metric Definition

**Description:** Verify the business definition of purchased is documented for all product ranking reports.

**Expectation:** The requirement should explicitly define whether purchased means quantity sold, transaction count, or sales amount before final sign-off.

**SQL:** `N/A - Requirement clarification needed.`

**Result:** Not applicable.
