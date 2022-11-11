// Copyright (c) 2022, thirvusoft@gmail.com and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Service Details Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd":1,
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd":1,
			"default": frappe.datetime.get_today(),
			"width": "80"
		},
		{
			"fieldname":"status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "Open\nOn Process\nCompleted\nReady For Delivery\nOverdue\nGoods Delivered\nCancelled",
			"width": "100"
		},
		

	]
};
