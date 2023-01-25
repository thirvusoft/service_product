import frappe

def on_submit(doc,event):
    if(doc.reference_doc and frappe.db.exists("Service", doc.reference_doc)):
        if(doc.status == "Submitted"):
            
            services=frappe.get_doc("Service",doc.reference_doc)
            services.advance_amount += doc.paid_amount
            services.save()

def on_canceled(doc,event):
    if(doc.reference_doc and frappe.db.exists("Service", doc.reference_doc)):
            services=frappe.get_doc("Service",doc.reference_doc)
            services.advance_amount -= doc.paid_amount
            if(services.advance_amount <0):
                services.advance_amount = 0

            services.save()
