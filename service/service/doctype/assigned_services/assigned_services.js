// Copyright (c) 2022, thirvusoft@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Assigned Services', {
	// : function(frm) {

	// }
});


frappe.ui.form.on("Required Items for Employee", {
    item_code: async function (frm, cdt, cdn) {
        let data = locals[cdt][cdn];
    
       
        if (data.item_code) {
            await frappe.call({
                method: "service.service.doctype.service.service.get_item_details",
                args: {
                    item: data.item_code,
                   
                },
                callback: function (r) {
                    frappe.model.set_value(cdt, cdn, "rate", r.message.rate || 0);
                   
                    if (!data.qty) {
                        frappe.model.set_value(cdt, cdn, "qty", 1);
                    }
                },
            });
        }

    amountcalc(frm, cdt, cdn);
    total_qty_and_amount(frm);
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
        total_amt = total_qty * row.amount;
    });
    frm.set_value("total_qty", total_qty);
    frm.set_value("total_amount", total_amt);
}


function amountcalc(frm, cdt, cdn) {
let data = locals[cdt][cdn];
frappe.model.set_value(cdt, cdn, "amount", (data.qty || 0) * (data.rate || 0));
}


 
