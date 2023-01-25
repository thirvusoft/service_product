# Copyright (c) 2022, thirvusoft@gmail.com and contributors
# For license information, please see license.txt
from functools import reduce
from erpnext.accounts.doctype.payment_entry.payment_entry import apply_early_payment_discount, get_bank_cash_account, get_reference_as_per_payment_terms, set_grand_total_and_outstanding_amount, set_paid_amount_and_received_amount, set_party_account, set_party_account_currency, set_payment_type
from erpnext.accounts.party import get_party_bank_account

import frappe
from frappe.utils import date_diff
from frappe.utils import nowdate
import json
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document


class Service(Document):
	def validate(self):
		company = frappe.db.get_single_value("Global Defaults", "default_company")
		paid_to = frappe.db.get_value("Company", company, "default_cash_account")
		paid_from=frappe.db.get_value("Company", company, "default_receivable_account")
		self.paid_to=paid_to
		self.paid_from=paid_from
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

	
	
	if(warehouse):
		filters['warehouse'] = warehouse
	elif frappe.db.get_single_value("Stock Settings", "default_warehouse"):
		filters['warehouse'] = frappe.db.get_single_value("Stock Settings", "default_warehouse")
	rate = frappe.get_all("Bin", filters, pluck = "valuation_rate")
	if(rate):
		return {"rate":rate[0], "income_account": income_account}
	return {"rate": frappe.get_value("Item", item, "valuation_rate"),"uom":frappe.get_value("Item", item, "stock_uom"),"item_name":frappe.get_value("Item", item, "item_name"),"income_account": income_account}

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
								"item_name": "item_name",
								"item_code":"item_code"	,
								"item_name":"description",				
								"doctype": "reference_dt",
								"name": "reference_dn",
								"income_account":"income_account"
							 },
				
			},
		},
		target_doc,
	   
	)
  
	return doc


	
@frappe.whitelist()
def get_payment_entry(dt,dn,party_amount=None, bank_account=None, bank_amount=None):
	print("jjjjjjjjjjjjjjjjjjjjjjjjjj")
	print(dn)
	reference_doc = None
	doc = frappe.get_doc(dt, dn)
	

	party_type = "Customer"
	party_account = set_party_account(dt, dn, doc, party_type)
	party_account_currency = set_party_account_currency(dt, party_account, doc)
	payment_type = set_payment_type(dt, doc)
	grand_total, outstanding_amount = doc.total_amount,doc.total_amount

	# bank or cash
	bank = get_bank_cash_account(doc, bank_account)

	paid_amount, received_amount = set_paid_amount_and_received_amount(
		dt, party_account_currency, bank, outstanding_amount, payment_type, bank_amount, doc)

	paid_amount, received_amount, discount_amount = apply_early_payment_discount(paid_amount, received_amount, doc)
	print(paid_amount)
	pe = frappe.new_doc("Payment Entry")
	pe.payment_type = payment_type
	pe.company = doc.company
	pe.cost_center = doc.get("cost_center")
	pe.posting_date = nowdate()
	pe.mode_of_payment = doc.get("mode_of_payment")
	pe.party_type = party_type
	pe.party = doc.get(frappe.scrub(party_type))
	pe.contact_person = doc.get("contact_person")
	pe.contact_email = doc.get("contact_email")
	pe.ensure_supplier_is_not_blocked()

	pe.paid_from = party_account if payment_type=="Receive" else bank.account
	pe.paid_to = party_account if payment_type=="Pay" else bank.account
	pe.paid_from_account_currency = party_account_currency \
		if payment_type=="Receive" else bank.account_currency
	pe.paid_to_account_currency = party_account_currency if payment_type=="Pay" else bank.account_currency
	pe.paid_amount = paid_amount
	pe.received_amount = received_amount
	pe.letter_head = doc.get("letter_head")

	if dt in ['Purchase Order', 'Sales Order', 'Sales Invoice', 'Purchase Invoice']:
		pe.project = (doc.get('project') or
			reduce(lambda prev,cur: prev or cur, [x.get('project') for x in doc.get('items')], None)) # get first non-empty project from items

	if pe.party_type in ["Customer", "Supplier"]:
		bank_account = get_party_bank_account(pe.party_type, pe.party)
		pe.set("bank_account", bank_account)
		pe.set_bank_account_data()

	# only Purchase Invoice can be blocked individually
	if doc.doctype == "Purchase Invoice" and doc.invoice_is_blocked():
		frappe.msgprint(_('{0} is on hold till {1}').format(doc.name, doc.release_date))
	else:
		if (doc.doctype in ('Sales Invoice', 'Purchase Invoice')
			and frappe.get_value('Payment Terms Template',
			{'name': doc.payment_terms_template}, 'allocate_payment_based_on_payment_terms')):

			for reference in get_reference_as_per_payment_terms(doc.payment_schedule, dt, dn, doc, grand_total, outstanding_amount):
				pe.append('references', reference)
		else:
			if dt == "Dunning":
				pe.append("references", {
					'reference_doctype': 'Sales Invoice',
					'reference_name': doc.get('sales_invoice'),
					"bill_no": doc.get("bill_no"),
					"due_date": doc.get("due_date"),
					'total_amount': doc.get('outstanding_amount'),
					'outstanding_amount': doc.get('outstanding_amount'),
					'allocated_amount': doc.get('outstanding_amount')
				})
				pe.append("references", {
					'reference_doctype': dt,
					'reference_name': dn,
					"bill_no": doc.get("bill_no"),
					"due_date": doc.get("due_date"),
					'total_amount': doc.get('dunning_amount'),
					'outstanding_amount': doc.get('dunning_amount'),
					'allocated_amount': doc.get('dunning_amount')
				})
			else:
				pe.append("references", {
					'reference_doctype': dt,
					'reference_name': dn,
					"bill_no": doc.get("bill_no"),
					"due_date": doc.get("due_date"),
					'total_amount': grand_total,
					'outstanding_amount': outstanding_amount,
					'allocated_amount': outstanding_amount
				})

	pe.setup_party_account_field()
	pe.set_missing_values()

	if party_account and bank:
		if dt == "Employee Advance":
			reference_doc = doc
		pe.set_exchange_rate(ref_doc=reference_doc)
		pe.set_amounts()
		if discount_amount:
			pe.set_gain_or_loss(account_details={
				'account': frappe.get_cached_value('Company', pe.company, "default_discount_account"),
				'cost_center': pe.cost_center or frappe.get_cached_value('Company', pe.company, "cost_center"),
				'amount': discount_amount * (-1 if payment_type == "Pay" else 1)
			})
			pe.set_difference_amount()

	return pe



# @frappe.whitelist()
# def make_payment_entry(source_name, target_doc=None):
# 	print("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
# 	company = frappe.db.get_single_value("Global Defaults", "default_company")
# 	paid_to = frappe.db.get_value("Company", company, "default_cash_account")
# 	paid_from=frappe.db.get_value("Company", company, "default_receivable_account")
# 	# print(cash_account)
# 	# print(receivable_account)
# 	doc = get_mapped_doc(
		
# 		"Service",
# 		source_name,
# 		{
# 			"Service": {
# 				"doctype": "Payment Entry",
				
# 				"field_map": {
					
# 					"payment_type":"payment_type",
# 					"name": "reference_doc",
# 					"party_name": "party_name",
# 					"party_type":"party_type",
# 					"customer": "party",
# 					"total_amount":"paid_amount",
# 					paid_to:"paid_to",
# 					paid_from:"paid_from"

						
# 				}
# 				},
			
			
# 		},
# 		target_doc,
# 	)

# 	return doc

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
