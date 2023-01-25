// Copyright (c) 2022, thirvusoft@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Service', {

    refresh: async function (frm) {
        cur_frm.set_df_property("barcode", "read_only", 1)
        await frappe.db.get_single_value("Service Settings", "enable_barcode").then((r) => {
            if (r) {
                frm.set_df_property("barcode", "hidden", 0)
            }
            else {
                frm.set_df_property("barcode", "hidden", 1)
            }

        });
        frm.fields_dict.barcode.get_barcode_html(frm.doc.barcode);
        if (frm.doc.status == "Goods Delivered") {
            frm.disable_form();
        }

        if (!frm.is_new()) {
            frm.page.set_inner_btn_group_as_primary(__("Create"));
            frappe.call({
                method: "service.service.doctype.service.service.button_enabled",
                args: { reference: frm.docname },
                callback: function (r) {

                    if (r.message) {

                        frm.add_custom_button("Sales Invoice", () => create_sales_invoice(frm), __("Create"));
                    }
                }
            })
            // frappe.call({
            //     method: "service.service.doctype.service.service.sales_button_disabled",
            //     args: { reference: frm.docname },
            //     callback: function (r) {

            //         if (r.message) {

            //             frm.add_custom_button("Payment Entry", () => create_payment_entry(frm), __("Create"));
            //         }
            //     }
            // })



        }
    },

    customer: function (frm, cdt, cdn) {
        let data = locals[cdt][cdn];
        var partyname = data.customer;
        frm.set_value("party_name", partyname)
    },
    invoice_no: function (frm, cdt, cdn) {
        let data = locals[cdt][cdn];
        frappe.call({
            method: "service.service.doctype.service.service.waranty",
            args: { invoice: data.invoice_no },
            callback: function (r) {
                if (r.message > 365) {
                    frm.set_value("waranty_status", "Out Of Waranty")
                }
                else {
                    frm.set_value("waranty_status", "Under Waranty")
                }

            }
        })
    },
    after_save: function (frm, cdt, cdn) {
    
        frm.reload_doc()
    }


});

frappe.ui.form.on("Required Items for Service", {
    item_code: async function (frm, cdt, cdn) {
        let data = locals[cdt][cdn];
        if (!data.warehouse) {
            await frappe.call({
                method: "service.service.doctype.service.service.get_default_warehouse",
                callback: function (r) {
                    frappe.model.set_value(cdt, cdn, "warehouse", r.message || "");
                },
            });
        }
        if (data.item_code) {
            await frappe.call({
                method: "service.service.doctype.service.service.get_item_details",
                args: {
                    item: data.item_code,
                    warehouse: data.warehouse || "",
                    company: frm.doc.company,
                },
                callback: function (r) {
                    console.log( r.message.uom)
                    console.log( r.message.income_account)
                    frappe.model.set_value(cdt, cdn, "rate", r.message.rate);
                    frappe.model.set_value(cdt, cdn, "item_name", r.message.item_name || "");
                    frappe.model.set_value(cdt, cdn, "uom", r.message.uom || "");
                    frappe.model.set_value(cdt, cdn, "income_account", r.message.income_account || "");
                    if (!data.qty) {
                        frappe.model.set_value(cdt, cdn, "qty", 1);
                    }
                },
            });
        }
        amountcalc(frm, cdt, cdn);
        total_qty_and_amount(frm);
    },
    warehouse: function (frm) {
        frm.trigger("item_code");
    },
    amount: function (frm) {
        total_qty_and_amount(frm);
    },
    qty: function (frm, cdt, cdn) {
        amountcalc(frm, cdt, cdn);
        total_qty_and_amount(frm);
    },
    rate: function (frm, cdt, cdn) {
        amountcalc(frm, cdt, cdn);
        total_qty_and_amount(frm);
    },
});

function total_qty_and_amount(frm) {
    let total_qty = 0,
        total_amt = 0;
    (frm.doc.required_items || []).forEach((row) => {
        total_qty += row.qty || 0;
        total_amt = total_qty * row.rate;
    });
    frm.set_value("total_qty", total_qty);
    frm.set_value("total_amount", total_amt);
}

// function amountcalc(frm, cdt, cdn) {
//     let data = locals[cdt][cdn];
//     frappe.model.set_value(cdt, cdn, "amount", (data.qty || 0) * (data.rate || 0));
// }

function create_sales_invoice(frm) {
    frappe.model.open_mapped_doc({
        method: "service.service.doctype.service.service.make_sales_invoice",
        frm: frm,
    });

}
function amountcalc(frm, cdt, cdn) {
    let data = locals[cdt][cdn];
    frappe.model.set_value(cdt, cdn, "amount", (data.qty || 0) * (data.rate || 0));
}

function create_payment_entry(frm) {
    return frappe.call({
        method:
        "service.service.doctype.service.service.get_payment_entry",
        args: {
            dt: frm.doc.doctype,
            dn: frm.doc.name,
        },
        callback: function (r) {
            var doc = frappe.model.sync(r.message);
            frappe.set_route("Form", doc[0].doctype, doc[0].name);
        },
    });
    // frappe.model.open_mapped_doc({
    //     method: "service.service.doctype.service.service.get_payment_entry",
    //     args:{
    //         "dt":cur_frm.doc.doctype,
    //         "dn":cur_frm.doc.name
    //     },

    // });


}
