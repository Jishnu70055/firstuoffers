# -*- coding: utf-8 -*-
# Copyright (c) 2021, tridz and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

 

class FuelPayment(Document):
	def before_save(self):
		customer_info = frappe.db.get_all('Customer',fields = ['refual','balance_trophies','total_trophies_earned','balance_amount','total_earned_cashback','name1','name','membership_type','fuel_type'])#taking values inthe doctype customer
		fuel_details = frappe.get_doc('Fuel Price')#fetching datas in single doctype Fuel Price
		trophy_details = frappe.get_doc('Trophy Setting') #fetching datas in single doctype Trophy Settings
		# self.doc4= frappe.get_doc('Customer',self.customer)
		for i in customer_info: 
			if self.customer == i['name']: #checking values of customer with customer doctype
				if i['fuel_type'] == 'PETROL':#checking fueltype is petrol
					if i['membership_type'] == 'PRIVLAGE':#checking membership type is privilage
						self.current_fuel_price = int(fuel_details.petrol_price) #setted current fuel price as in fuel price doctype
						self.fistu_fuel_price = int(fuel_details.privilage_petrol_price) #added the field firstu fuel price
						self.petrol = (int(self.amount)) / (int(fuel_details.petrol_price))#the how much liter is calculated by dividing amount with petrol price in doctype fuel price 
						self.cashback = (int(fuel_details.petrol_price) - int(fuel_details.privilage_petrol_price)) * self.petrol#calculating cashback with multiplying howmuch liters with difference between petrol price and privillage member petrol price 
						cashback_ledger_new = frappe.new_doc("CashBack Ledger")#fetching the doctype cashback ledger
						cashback_ledger_new.customer = self.customer#assigning value to customerfield
						cashback_ledger_new.status = 'Recieved'#assigning value to status field
						cashback_ledger_new.amount = self.cashback#assigning value to field amount 
						cashback_ledger_new.insert()#updated and saved the doctype cashback ledger
						cashback_ledger_new.submit()#submitted the document

						customer_add = frappe.get_doc('Customer',i['name'])#fetching the values of customer doctype 
						customer_add.total_earned_cashback = int(i['total_earned_cashback']) + int(self.cashback)#adding amount into total cashback
						customer_add.balance_amount = int(customer_add.balance_amount) + int(self.cashback)#adding amount into balance cashback
						if customer_add.refual == '0': #checking the value of refual is 0
							customer_add.total_trophies_earned = int(int(customer_add.total_trophies_earned) + int(trophy_details.number_of_trophy))#adding trophies into total no:of trophies 
							customer_add.balance_trophies = int(customer_add.balance_trophies) + int(trophy_details.number_of_trophy)#adding trophies into balance trophies
							customer_add.refual = int(customer_add.refual) + int(trophy_details.refual_frequency)#addding values into refual
							trophy_ledger_new = frappe.new_doc("Trophy Ledger")#fetching datas in Trophy Ledger
							trophy_ledger_new.customer = self.customer#updating value inside customer field
							trophy_ledger_new.status = 'Credited' #adding values into status field
							trophy_ledger_new.number_of_trophy = trophy_details.number_of_trophy #updating values into number of trophy
							trophy_ledger_new.insert()#updated and saved table Trophy ledger
							trophy_ledger_new.submit()#submitted the document

							# self.doc2.refual = 5
							# self.doc2.total_trophies_earned = int(self.doc2.total_trophies_earned) + int(doc3.number_of_trophy) 
							# self.doc2.balance_trophies = int(self.doc2.balance_trophies) + int(doc3.number_of_trophy)
							# self.doc2.save()
							# i['total_trophies_earned'] = int(self.doc2.total_trophies_earned) + int(doc3.number_of_trophy)
							# i['balance_trophies'] = int(self.doc2.balance_trophies) + int(doc3.number_of_trophy)
							# i['refual'] = int(self.doc2.refual) + int(trophy_details.refual_frequency)
						else:
							customer_add.refual = int(customer_add.refual) - 1#the value of refual is reduced from 1
						customer_add.save() #updated and saved doctype customer

						
					elif i['membership_type'] == 'STATUS':#checked membership type is status
						self.current_fuel_price = fuel_details.petrol_price #setted current fuel price as in fuel price doctype
						self.fistu_fuel_price = fuel_details.status_petrol_price #added the field firstu fuel price
						self.petrol = int(self.amount) / int(fuel_details.petrol_price)#calcualated how much liters
						self.cashback = (int(fuel_details.petrol_price) - int(fuel_details.status_petrol_price)) * self.petrol#calculated cashback

						cashback_ledger_new = frappe.new_doc("CashBack Ledger") #fetching datas of the doctype cashback ledgers and adding new documemnts 
						cashback_ledger_new.customer = self.customer #adding customer
						cashback_ledger_new.status = 'Recieved'#adding field status as recieved
						cashback_ledger_new.amount = self.cashback #adding the field amount 
						cashback_ledger_new.insert() #insert it into the doctpe as a new document
						cashback_ledger_new.submit()#submitted the document


						customer_add = frappe.get_doc('Customer',i['name']) #fetching the values inthe doctype customer
						customer_add.total_earned_cashback = i['total_earned_cashback'] + self.cashback #modified the field total earned cashback
						customer_add.balance_amount = i['balance_amount'] + self.cashback#modified the field balance amount 
						if customer_add.refual == '0': #cheecking refual value is 0
							customer_add.total_trophies_earned = int(customer_add.total_trophies_earned) + int(trophy_details.number_of_trophy) #modified total earned trophies
							customer_add.balance_trophies = int(customer_add.balance_trophies) + int(trophy_details.number_of_trophy)#modified the field balance trophies
							customer_add.refual = int(customer_add.refual) + int(trophy_details.refual_frequency)#modified the field refual
							trophy_ledger_new = frappe.new_doc("Trophy Ledger")#fetching the values inthe doctype trophy ledger
							trophy_ledger_new.customer = self.customer #adding the customer field
							trophy_ledger_new.status = 'Credited' #setting status field as credited
							trophy_ledger_new.number_of_trophy = trophy_details.number_of_trophy #added no:of trophy field
							trophy_ledger_new . insert()#inserted a new document into tropy ledger
							trophy_ledger_new.submit()#submitted the document
						else:
							customer_add.refual = int(customer_add.refual) - 1 #refual value is decreased into 1

						customer_add.save()#updated and saved customer doctype
					
					# else:
					# 	pass

				
				elif i['fuel_type'] == 'DIESAL':#checking fueltype is diesal
						if i['membership_type'] == 'PRIVLAGE':#checking membership is privilage
							self.current_fuel_price = fuel_details.diesal_price #setted current fuel price as in fuel price doctype
							self.fistu_fuel_price = fuel_details.privilage_diesal_price #added the field firstu fuel price
							self.petrol = int(self.amount) / int(fuel_details.diesal_price)#calculating liters
							self.cashback = (int(fuel_details.diesal_price) - int(fuel_details.privilage_diesal_price)) * self.petrol#calculating cashback

							cashback_ledger_new = frappe.new_doc("CashBack Ledger") #fetching the values in doctype cashback ledger
							cashback_ledger_new.customer = self.customer#adding the field customer
							cashback_ledger_new.status = 'Recieved'#adding the field status as recieved
							cashback_ledger_new.amount = self.cashback#adding the field amount 
							cashback_ledger_new.insert()#saved and updated the doctype cashback ledger
							cashback_ledger_new.submit()#submitted the document

							customer_add = frappe.get_doc('Customer',i['name']) #fetched the datas inthe doctype customer
							customer_add.total_earned_cashback = int(i['total_earned_cashback']) + int(self.cashback) #updated the field total cashback earned
							customer_add.balance_amount = int(i['balance_amount']) + int(self.cashback)#updated the field balance amount
							if customer_add.refual == '0':#checked refual field is 0
								customer_add.total_trophies_earned = int(customer_add.total_trophies_earned) + int(trophy_details.number_of_trophy)#updated the field total no:of trophies
								customer_add.balance_trophies = int(customer_add.balance_trophies) + int(trophy_details.number_of_trophy)#updated the field balance trophies
								customer_add.refual = int(customer_add.refual) + int(trophy_details.refual_frequency)#updated the field refual
								trophy_ledger_new = frappe.new_doc("Trophy Ledger")#creating the new document inthe doctype trophy ledger
								trophy_ledger_new.customer = self.customer#adding new field customer
								trophy_ledger_new.status = 'Credited'#adding status as credited
								trophy_ledger_new.number_of_trophy = trophy_details.number_of_trophy #updated the field total trophies  
								trophy_ledger_new . insert()#inserted a new document
								trophy_ledger_new.submit()#submitted the document
							else:
								customer_add.refual = int(customer_add.refual) - 1 #refual value is reduced by 1

							customer_add.save()#updated and saved customer doctype 
						elif i['membership_type'] == 'STATUS':#checking the membership is status
							self.current_fuel_price = fuel_details.diesal_price #setted current fuel price as in fuel price doctype
							self.fistu_fuel_price = fuel_details.status_diesal_price #added the field firstu fuel price
							self.petrol = int(self.amount) / int(fuel_details.diesal_price)#calculating how much liters
							self.cashback = (int(fuel_details.petrol_price) - int(fuel_details.status_diesal_price)) * (self.petrol)#calculating cashbacks


							cashback_ledger_new = frappe.new_doc("CashBack Ledger")#creating a new document in cashback ledger
							cashback_ledger_new.customer = self.customer #added value into field customer
							cashback_ledger_new.status = 'Recieved'#adding values into the field  status as recieved
							cashback_ledger_new.amount = self.cashback#added value into the field amount  
							cashback_ledger_new.insert()#inserted new document 
							cashback_ledger_new.submit()#submitted the document

							customer_add = frappe.get_doc('Customer',i['name'])#fetched values inthe doctype customer
							customer_add.total_earned_cashback = i['total_earned_cashback'] + self.cashback#updated the field total cashback
							customer_add.balance_amount = i['balance_amount'] + self.cashback#updated the field balance amount 
							if customer_add.refual == '0': #checking the vallue of refual is 0
								customer_add.total_trophies_earned = int(customer_add.total_trophies_earned) + int(trophy_details.number_of_trophy)#updated the field total trophies earned
								customer_add.balance_trophies = int(customer_add.balance_trophies) + int(trophy_details.number_of_trophy)#updated the field balane trophies
								customer_add.refual = int(customer_add.refual) + int(trophy_details.refual_frequency)#updaed the field refual
								trophy_ledger_new = frappe.new_doc("Trophy Ledger")#adding a new document into trophyledger
								trophy_ledger_new.customer = self.customer#added customer field 
								trophy_ledger_new.status = 'Credited'#setted status as credited
								trophy_ledger_new.number_of_trophy = trophy_details.number_of_trophy#added no:of trophies field
								trophy_ledger_new . insert()#inserted a new document 
								trophy_ledger_new.submit()#submitted the document
							else:
								customer_add.refual = int(customer_add.refual) - 1#reduce the refual by 1

							customer_add.save()#update and saved the document customer
	
		
							