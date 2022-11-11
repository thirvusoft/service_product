# Copyright (c) 2022, thirvusoft@gmail.com and contributors
# For license information, please see license.txt

import frappe




def execute(filters=None):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	status = filters.get("status")
	
	filters = []
	filters.append(["status", "=",status])
	
	if to_date:
	
		filters.append(["posting_date", "<=", to_date])
	if from_date:
		filters.append(["posting_date", ">=", from_date])

	
	
	result_data=frappe.get_list("Service",fields=["customer","posting_date","expected_delivery_date","status","service_item","item_count","received_employee","total_amount","advance_amount"],	filters=filters)
						
			
	columns = get_columns()
	return columns,result_data
 
def get_columns():
	columns = [
		("Customer")  + ":Data:100",
		("Posting Date") + ":Data:100",
		("Expected Delivery Date") + ":Link/Designation:200",
		("Status") + ":Data:100",
		("Service Item") + ":Data:100",
		("Item Count") + ":Data:100",
		("Received Employee") + ":Data:100",
		("Total Amount") + ":Currency:100",
		("Paid Amount") + ":Currency:100",
		
		]
	
	return columns
	
