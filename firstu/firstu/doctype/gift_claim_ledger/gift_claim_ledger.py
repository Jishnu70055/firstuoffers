# -*- coding: utf-8 -*-
# Copyright (c) 2021, tridz and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class GiftClaimLedger(Document):
	def before_save(self):  #call function before saving doctype Gift Claim Ledger
		customer_details = frappe.get_doc("Customer",self.customer)  #taking datas in doctype
		# frappe.throw(self.trophies_needed)
		if int(self.trophies_needed) <= int(customer_details.balance_trophies):  #checking value of gift claim ledger trophies needed is less than or equal to customers balance trophy 
			customer_table = frappe.get_doc("Customer",self.customer) #fetching customer datas
			customer_table.balance_trophies = int(customer_table.balance_trophies) - int(self.trophies_needed) #the difference between balance trophies and gift claim trophy added to customer balance trophies
			customer_table.save()  #save 

			trophy_ledger_new = frappe.new_doc("Trophy Ledger")  #adding a new document into doctype Trophy Ledger
			trophy_ledger_new.customer = self.customer #adding field-customer into Trophy Ledger
			trophy_ledger_new.status = 'Debited' #adding status field
			trophy_ledger_new.number_of_trophy = self.trophies_needed #adding no:of trophies
			trophy_ledger_new . insert()  #insert values into doctype Trophy Ledger
			trophy_ledger_new .submit()


			




			
			# frappe.throw("Achieved",self.gift)
		else:
			frappe.throw(("You Dont Have Required Trophies")) #if customer dont have enough trophies just printing a check box

