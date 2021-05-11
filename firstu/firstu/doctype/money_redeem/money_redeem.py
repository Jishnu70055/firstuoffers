# -*- coding: utf-8 -*-
# Copyright (c) 2021, tridz and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from requests.auth import HTTPBasicAuth
import requests
import hmac
import hashlib
import sys
import frappe

class MoneyRedeem(Document):
	def before_submit(self):
		customer = frappe.get_doc("Customer" , self.customer)
		if int(customer.balance_amount) < int(self.amount):
			frappe.throw("Invalid Balance")
		else:
			if customer.contact_id == None:
				url = 'https://api.razorpay.com/v1/contacts'
				headers =  {"Content-Type": "application/json"}
				auth=HTTPBasicAuth('rzp_test_BNRLROGFnxu3NQ', 'RjCCeIapanWPIgT95oUFQeJ8')
				body = {
                    "name":customer.name1,
                        "email":customer.email,
                        "contact":customer.mobile_number,
                        "type":"employee",
                        "reference_id":"Acme Contact ID 12345",
                        "notes":{
                                "notes_key_1":"Tea, Earl Grey, Hot",
                                "notes_key_2":"Tea, Earl Grey… decaf."
                        }
                	}
				req = requests.post(url, headers=headers , auth=auth ,  json=body)
				request = req.json()
				# frappe.throw(frappe.as_json(req)
				contact_id = request["id"]
				customer.contact_id = contact_id
				customer.save()
				amount = self.amount * 100
				resp = fund_account(self ,contact_id )
			else:
				contact_id = customer.contact_id
				amount = self.amount * 100
				resp = fund_account(self ,contact_id)

def fund_account(self ,contact_id):
	customer = frappe.get_doc("Customer",self.customer)
	url = "https://api.razorpay.com/v1/fund_accounts"
	auth=HTTPBasicAuth('rzp_test_BNRLROGFnxu3NQ', 'RjCCeIapanWPIgT95oUFQeJ8')
	headers = {"Content-Type": "application/json"}
	body = {
        "contact_id":contact_id,
        "account_type":customer.account_type,
        "bank_account":{
        "name":customer.name1,
        "ifsc":customer.ifsc,
        "account_number":customer.account_number
            }
    }
	req = requests.post(url, headers=headers , auth=auth ,  json=body)
	request = req.json()
	fund_id = request['id']
	fund = payout(self ,fund_id)

def payout(self ,fund_id):
	customer = frappe.get_doc("Customer" ,self.customer)
	url = 'https://api.razorpay.com/v1/payouts'
	auth=HTTPBasicAuth('rzp_test_BNRLROGFnxu3NQ', 'RjCCeIapanWPIgT95oUFQeJ8')
	headers = {"Content-Type": "application/json"}
	body = {
        "account_number": customer.account_number,
        "fund_account_id": fund_id,
        "amount": self.amount * 100,
        "currency": "INR",
        "mode": "IMPS",
        "purpose": "refund",
        "queue_if_low_balance": True,
        "reference_id": "Acme Transaction ID 12345",
        "narration": "Acme Corp Fund Transfer",
        "notes": {
                "notes_key_1":"Tea, Earl Grey, Hot",
                "notes_key_2":"Tea, Earl Grey… decaf."
            }
    }
	req = requests.post(url, headers=headers , auth=auth ,  json=body)
	request = req.json()
	cashback_ledger_new = frappe.new_doc("CashBack Ledger")
	cashback_ledger_new.customer = self.customer
	cashback_ledger_new.status = 'Redeemed'
	cashback_ledger_new.amount = self.amount
	cashback_ledger_new.fund_id = fund_id
	cashback_ledger_new.payment_id = request["id"]
	cashback_ledger_new.payment_status = request["status"]
	cashback_ledger_new.insert()
