
| Check | Actual result | Status |
| --- | --- | --- |
| Customer rows loaded | 250 | Pass |
| Order rows loaded | 250 | Pass |
| Shipping rows loaded | 250 | Pass |
| Unique customers in orders | 160 | Info |
| Unique customers in shipping | 154 | Info |
| Common customers between orders and shipping | 99 | Risk |
| Customers with no orders | 90 | Info |

The order and shipping sources cannot be joined safely for spend validation because they only share `Customer_ID`, and both files contain repeated customer IDs. This creates a many-to-many join risk.

## Test scenarios

| Scenario ID | Test scenario | Objective |
| --- | --- | --- |
| TS01 | Source file and schema validation | Confirm all source files can be loaded and contain the columns needed for reporting |
| TS02 | Join integrity validation | Verify whether the three sources can be joined without duplication or data loss |
| TS03 | Pending delivery spend by country | Validate total amount spent by country for pending delivery status |
| TS04 | Customer sales summary | Validate transactions, amount spent, and product details for each customer |
| TS05 | Country-wise top product | Validate the highest purchased product for each country |
| TS06 | Age-band top product | Validate the most purchased product for age `< 30` and `>= 30` |
| TS07 | Minimum country metrics | Validate the country with minimum transactions and minimum sales amount |
| TS08 | Requirement gap validation | Identify missing fields or ambiguous business rules that block exact testing |

## Test cases and results

| TC ID | Scenario | SQL reference | Expected result | Actual result | Status |
| --- | --- | --- | --- | --- | --- |
| TC01 | TS01 | Query 1 | All 3 files should load into test tables | 250 customer rows, 250 order rows, 250 shipping rows loaded | Pass |
| TC02 | TS02 | Query 1 | Order and shipping data should have a reliable business key for reporting joins | Only 99 common customers between orders and shipping; no order-to-shipping key exists | Fail |
| TC03 | TS03 | Query 2 | Pending delivery spend should be testable by country | Requirement is not reliably testable because `shipping` cannot be mapped to `orders` without duplication risk | Blocked |
| TC04 | TS04 | Query 3 | Each customer should show transactions, amount spent, and product details | Full output generated in `qa_output\\customer_summary_results.csv`; 90 customers have zero orders | Pass |
| TC05 | TS04 | Query 3 | Total quantity sold should be testable for each customer | No quantity column exists in any source | Blocked |
| TC06 | TS05 | Query 4 | Top product should be derivable for each country | UAE = Keyboard (12), UK = Mousepad (24), USA = Mousepad (18) | Pass with assumption |
| TC07 | TS06 | Query 5 | Top product should be derivable for each age band | Less than 30 = Mousepad (17), 30 and above = Keyboard (35) | Pass with assumption |
| TC08 | TS07 | Query 6 and 7 | Country with minimum transactions and minimum sales amount should be derivable | UAE has minimum transactions (40) and minimum sales amount (49950.00) | Pass |

## Expected values from SQL execution

### 1. Pending delivery status: total amount spent by country

This result is assumption-based only because the source model does not provide a valid order-to-shipping link.

| Country | Pending transactions | Total amount spent |
| --- | --- | --- |
| UK | 52 | 136300.00 |
| USA | 55 | 65500.00 |
| UAE | 37 | 53800.00 |

### 2. Customer summary

The full customer-level output is available in `C:\Users\prasanna.mahale\PycharmProjects\PEI\qa_output\customer_summary_results.csv`.

Top values from the generated result:

| Customer ID | Customer name | Country | Total transactions | Total amount spent | Product details |
| --- | --- | --- | --- | --- | --- |
| 166 | Morgan Cooper | USA | 3 | 17350.00 | Harddisk, Monitor, Webcam |
| 123 | Philip Robinson | UK | 2 | 17000.00 | Harddisk, Monitor |
| 129 | Amber Banks | UK | 2 | 17000.00 | Harddisk, Monitor |
| 96 | Eric Harvey | USA | 4 | 14700.00 | DDR RAM, Headset, Monitor, Mouse |
| 193 | Yesenia White | UK | 4 | 13950.00 | DDR RAM, Monitor, Mousepad, Mousepad |

Note:

- 90 customers have no matching order rows and therefore show `0` transactions and `0.00` amount spent.
- Quantity sold is not available in the provided sources.

### 3. Maximum product purchased for each country

Purchase was interpreted as transaction count because quantity is not available.

| Country | Product | Transaction count | Total sales amount |
| --- | --- | --- | --- |
| UAE | Keyboard | 12 | 4800.00 |
| UK | Mousepad | 24 | 5350.00 |
| USA | Mousepad | 18 | 4100.00 |

### 4. Most purchased product by age category

Purchase was interpreted as transaction count because quantity is not available.

| Age category | Product | Transaction count | Total sales amount |
| --- | --- | --- | --- |
| Less than 30 | Mousepad | 17 | 3900.00 |
| 30 and above | Keyboard | 35 | 14000.00 |

### 5. Country with minimum transactions and sales amount

| Metric | Country | Value |
| --- | --- | --- |
| Minimum transactions | UAE | 40 |
| Minimum sales amount | UAE | 49950.00 |

## Requirement gaps

1. `Shipping.json` cannot be linked reliably to `Order.csv`.
The shipping file has `Shipping_ID`, `Status`, and `Customer_ID`, but it does not contain `Order_ID`. Because both orders and shipping repeat the same customer IDs, joining on `Customer_ID` creates a many-to-many duplication risk.

2. Quantity sold is missing from all sources.
The requirement asks for total quantity sold and uses wording such as "maximum product purchased" and "most purchased product", but the source data only provides `Item` and `Amount`. The current validation can only use transaction count as a proxy.

3. "Maximum product purchased" is ambiguous.
This could mean highest quantity, highest transaction count, or highest sales amount. The current test uses transaction count because quantity is unavailable.

4. "Country that had minimum transactions and sales amount" is ambiguous.
This can be read as one country that satisfies both conditions, or as two separate checks. In the current data both metrics point to UAE, but the requirement should still be clarified.

5. Pending delivery spend by country is ambiguous.
The wording implies shipping status should drive sales amount, but the data model does not show whether shipping status belongs to an order, a shipment, or a customer-level record.