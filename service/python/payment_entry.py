import frappe

def on_submit(doc,event):
    if(doc.reference_doc and frappe.db.exists("Service", doc.reference_doc)):
        if(doc.status == "Submitted"):
            
            services=frappe.get_doc("Service",doc.reference_doc)
            print(services)
            services.advance_amount += doc.paid_amount
            services.save()
    # if(doc.references):
       
    #     a=frappe.get_all("Payment Entry Reference",
	# 			filters={"parent":doc.name},
	# 			fields=["reference_doctype","reference_name"])
    #     for i in a:
    #         if (i["reference_doctype"]=="Sales Invoice"):
    #             service_doc=frappe.get_doc("Sales Invoice",i["reference_name"])
    #             if (service_doc.reference_doc):
    #                 services=frappe.get_doc("Service",service_doc.reference_doc)
    #                 services.advance_amount += doc.paid_amount
    #         services.save(ignore_permissions=True)


        # print(a)
        # print(doc.references)
        # print(doc.name1)
def on_canceled(doc,event):
    if(doc.reference_doc and frappe.db.exists("Service", doc.reference_doc)):
            services=frappe.get_doc("Service",doc.reference_doc)
            services.advance_amount -= doc.paid_amount
            if(services.advance_amount <0):
                services.advance_amount = 0

            services.save()
