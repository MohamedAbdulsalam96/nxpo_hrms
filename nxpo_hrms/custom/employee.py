# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
import frappe
from frappe import _
from dateutil.relativedelta import relativedelta
from frappe.utils import (
	getdate,
	today,
)
import json


def update_employee_data(doc, method=None):
    # Date pass probation
    doc.custom_date_pass_probation = (
        getdate(doc.date_of_joining) +
        relativedelta(days=doc.custom_probation_days)
    )
    # Experience YTD
    date = doc.relieving_date or today()
    diff = relativedelta(getdate(date), getdate(doc.date_of_joining))
    doc.custom_experience_ytd = _("{0} Years {1} Months {2} Days").format(
        diff.years, diff.months, diff.days
    )

@frappe.whitelist()
def get_employee_basic_html(employee):
    data = json.loads(employee)
    return frappe.render_template("nxpo_hrms/custom/employee/basic.html", {"data": data})

@frappe.whitelist()
def get_employee_property_history_html(employee):
    employee = json.loads(employee)
    employee = employee["name"]
    docs = []
    doctypes = {"Employee Transfer": "transfer_date", "Employee Promotion": "promotion_date"}
    for doctype, docfield in doctypes.items():
        docs += frappe.get_all(
            doctype,
            filters={
                "docstatus": 1,
                "employee": employee,
            },
            fields=["name", docfield],
            as_list=True
        )
    docs = dict(docs)
    data = frappe.get_all(
            "Employee Property History",
            filters={
                "parent": ["in", docs.keys()],
            },
            fields=["parenttype", "parent", "property", "current", "new"]
        )
    for d in data:
        d["date"] = docs[d["parent"]]
    data = sorted(data, key=lambda x: (x["date"], x["property"], x["parent"]))
    # remove date when same as previous for readability
    result = []
    prev_date = False
    for d in data:
        if d["date"] == prev_date:
            d["date"] = False
        else:
            prev_date = d["date"]
        result.append(d)
    return frappe.render_template("nxpo_hrms/custom/employee/property_history.html", {"data": data})

# ----
# JOBS
# ----
def update_all_employee_data():
    for employee in frappe.get_all("Employee", pluck="name"):
        doc = frappe.get_doc("Employee", employee)
        update_employee_data(doc)
