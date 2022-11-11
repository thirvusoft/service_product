# Copyright (c) 2022, thirvusoft@gmail.com and contributors
# For license information, please see license.txt
import frappe
from frappe.utils import date_diff
from frappe.utils import nowdate
import json
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document

class Service(Document):
	def validate(self):
		self.barcode = self.name
		for row in self.required_items:
			row.remaining_qty_to_invoice = (row.qty or 0)- (row.invoiced_qty or 0)
	def after_insert(self):
		
		if not frappe.db.exists("Assigned Services", {"reference_doc": self.name}):
			print(frappe.db.exists("Assigned Services", {"reference_doc": self.name}))
			print("jbkvjdbjvdb")
			new_doc=frappe.new_doc("Assigned Services")
			new_doc.assigned_date=self.posting_date,
			new_doc.expected_delivery_date=self.expected_delivery_date,
			new_doc.employee=self.received_employee,
			new_doc.reference_doc=self.name
		
			for i in self.required_items:
				
				new_doc.append("required_items", {"item_code": i.item_code or "", "qty": i.qty or "","amount":i.amount or ""})

			new_doc.insert()
		else:
			print("dgdgdjgadjadb")
			assignedservice=frappe.get_all("Assigned Services",filters={"reference_doc":self.name})
			print(assignedservice)
			for i in assignedservice:
				print(i)
				servicedoc=frappe.get_doc("Assigned Services",i["name"])
				print(servicedoc)
				servicedoc.update({			
				"assigned_date":self.posting_date,
				"expected_delivery_date":self.expected_delivery_date,
				"employee":self.received_employee or "",
				})
				servicedoc.set("required_items", [])
				for i in self.required_items:
					print(i)
					servicedoc.append("required_items", {"item_code": i.item_code or "", "qty": i.qty or "","amount":i.amount or ""
	})
				servicedoc.insert()
				servicedoc.save()
				print(servicedoc)
	def on_submit(self):
		if(not self.docstatus==1 and not self.status=="Completed"):
			frappe.throw("Completed Status Only Move to Submitted")

		
	# def on_submit(self):
	# 	if(not self.status=="Completed")



@frappe.whitelist()
def button_enabled(reference):
	a= frappe.get_all("Payment Entry", filters={"reference_doc":reference, "docstatus": ['!=', 2]})
	if not a:
		return True

@frappe.whitelist()
def sales_button_disabled(reference):
	a= frappe.get_all("Sales Invoice", filters={"reference_doc":reference, "docstatus": ['!=', 2]})
	if not a:
		return True

@frappe.whitelist()
def get_default_warehouse():
	return frappe.db.get_single_value("Stock Settings", "default_warehouse")
@frappe.whitelist()
def get_item_details(item, warehouse = '', company = ''):
	if(not company):
		company = frappe.db.get_single_value("Global Defaults", "default_company")
	income_account = frappe.db.get_value("Company", company, "default_income_account")
	filters = {}
	if(item):
		filters['item_code'] = item
	filters1 = filters.copy()
	filters1['rate'] = ['!=', 0]
	rate = frappe.get_all("Required Items for Service", filters1, pluck = "rate")
	if(rate):
		return {"rate":rate[0], "income_account": income_account}
	
	if(warehouse):
		filters['warehouse'] = warehouse
	elif frappe.db.get_single_value("Stock Settings", "default_warehouse"):
		filters['warehouse'] = frappe.db.get_single_value("Stock Settings", "default_warehouse")
	rate = frappe.get_all("Bin", filters, pluck = "valuation_rate")
	if(rate):
		return {"rate":rate[0], "income_account": income_account}
	
	return {"rate": frappe.get_value("Item", item, "valuation_rate"), "income_account": income_account}

@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None):
	doc = get_mapped_doc(
		"Service",
		source_name,
		{
			"Service": {
				"doctype": "Sales Invoice",
				"field_map": {
					"expected_delivery_date": "due_date",
					
					"name": "reference_doc"
				}
				},
			"Required Items for Service": {
				"doctype": "Sales Invoice Item",
				"field_map": {
								"qty": "qty",
								"item_name": "description",
								"doctype": "reference_dt",
								"name": "reference_dn"
							 },
				
			},
		},
		target_doc,
	)

	return doc

@frappe.whitelist()
def make_payment_entry(source_name, target_doc=None):
	doc = get_mapped_doc(
		"Service",
		source_name,
		{
			"Service": {
				"doctype": "Payment Entry",
				
				"field_map": {
					
					"payment_type":"payment_type",
					"name": "reference_doc",
					"party_name": "party_name",
					"party_type":"party_type",
					"customer": "party",
					"total_amount":"paid_amount"
						
				}
				},
			
		},
		target_doc,
	)

	return doc

# @frappe.whitelist()
# def make_assigned_employee(posting_date,delivery_date,employee,table=None,reference=None):
# 	print(reference)
	
# 	print(posting_date)
# 	if not frappe.db.exists("Assigned Services", {"reference_doc": reference}):
# 		print(frappe.db.exists("Assigned Services", {"reference_doc": reference}))
# 		print("jbkvjdbjvdb")
# 		new_doc=frappe.new_doc("Assigned Services")
# 		new_doc.assigned_date=posting_date,
# 		new_doc.expected_delivery_date=delivery_date,
# 		new_doc.employee=employee,
# 		new_doc.reference_doc=reference
	
# 		for i in json.loads(table):
			
# 			new_doc.append("required_items", {"item_code": i["item_code"] or "", "qty": i["qty"] or "","amount":i["amount"] or ""})

# 		new_doc.insert()
# 	else:
# 		print("dgdgdjgadjadb")
# 		assignedservice=frappe.get_all("Assigned Services",filters={"reference_doc":reference})
# 		print(assignedservice)
# 		for i in assignedservice:
# 			print(i)
# 			tablevalue=json.loads(table)
# 			print(tablevalue)
# 			servicedoc=frappe.get_doc("Assigned Services",i["name"])
# 			print(servicedoc)
# 			servicedoc.update({			
# 			"assigned_date":posting_date,
# 			"expected_delivery_date":delivery_date,
# 			"employee":employee,
# 			"reference_doc":reference,
# 			})
# 			servicedoc.set("required_items", [])
# 			for i in tablevalue:
# 				print(i)
# 				servicedoc.append("required_items", {"item_code": i["item_code"] or "", "qty": i["qty"] or "","amount":i["amount"] or ""
# })
# 			servicedoc.save()
# 			print(servicedoc)





		
@frappe.whitelist()
def waranty(invoice):
	a=frappe.get_all("Sales Invoice",filters={"name":invoice},fields=['posting_date'])
	b=nowdate()
	
	for i in a:
		e=date_diff(b,i["posting_date"])
		return e
