# -*- coding: utf-8 -*-
# Copyright (c) 2021, tridz and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CashBackLedger(Document):
	def before_save(self):   #callling funchtion before save
		if self.status == 'Redeemed':  #checking status field is redemmed
			customer_data = frappe.get_doc("Customer",self.customer)  #fetching values in customer doctype
			if int(customer_data.balance_amount) >= int(self.amount):  #checking balance cashback of customer doctype is greater than amount in cashback ledger
				customer_data.balance_amount = int(customer_data.balance_amount) - int(self.amount) #the difference between balance cashback and amount is fetched into the field balance doctype 
				# frappe.throw(customer_data.redeemed_amount)
				customer_data.redeemed_amount = int(customer_data.redeemed_amount) + int(self.amount) #updaed the field redeemed amount
				customer_data.save()# updated customer table and saved
			else:
				frappe.throw("Not Sufficent Balance")



