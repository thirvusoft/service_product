# Copyright (c) 2022, thirvusoft@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AssignedServices(Document):
	def on_submit(self):
		if(self.docstatus==1 and self.status=="Completed"):
			frappe.db.set_value("Service",self.reference_doc,"status","Ready For Delivery")

			requireditems=frappe.get_doc("Service",self.reference_doc)
			print("1")
			requireditems.set("required_items", [])
			requireditems.set("total_qty",self.total_qty)
			requireditems.set("total_amount",self.total_amount)
			requireditems.set("expected_delivery_date",self.expected_delivery_date)
			print("2")
			for i in self.required_items:

				# print(i)
				requireditems.append("required_items", {"item_code": i.item_code or "", "qty": i.qty or "","amount":i.amount or ""
	})
            
			requireditems.save()
			print(requireditems)
		
		else:
			frappe.throw("Completed Status Only Move to Submitted")
	
	def validate(self):
		
		if(self.status=="On Process"):
			frappe.db.set_value("Service",self.reference_doc,"status","On Process")
		if(self.status=="Not Yet Started"):
			frappe.db.set_value("Service",self.reference_doc,"status","Not Yet Started")
	# def on_update_after_submit(self):
	# 	p


@frappe.whitelist()
def get_item_details(item):
	item_rate=frappe.get_doc("Item",item)
	rate = item_rate.valuation_rate
	return rate

