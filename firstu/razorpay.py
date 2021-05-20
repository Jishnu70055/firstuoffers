
from __future__ import unicode_literals
from frappe.model.document import Document
from requests.auth import HTTPBasicAuth
import requests
import hmac
import hashlib
import sys
import frappe

@frappe.whitelist()
def create_account(customer_id,amount):
    customer = frappe.get_doc('Customer' ,customer_id)
    if int(customer.balance_amount) < int(amount):
        return("Do Not Have Valid Balance")
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
            contact_id = request["id"]
            customer.contact_id = contact_id
            customer.save()
            amount = amount
            resp = fund_account(contact_id,amount,customer_id)
            return resp
        else:
            contact_id = customer.contact_id
            amount = amount
            resp = fund_account(contact_id,amount,customer_id)
            return resp
@frappe.whitelist()
def fund_account(contact_id,amount,customer_id):
    customer = frappe.get_doc("Customer" ,customer_id)
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
    fund = payout(fund_id,amount,customer_id)
    return fund

def payout(fund_id,amount,customer_id):
    customer = frappe.get_doc("Customer" ,customer_id)
    url = 'https://api.razorpay.com/v1/payouts'
    auth=HTTPBasicAuth('rzp_test_BNRLROGFnxu3NQ', 'RjCCeIapanWPIgT95oUFQeJ8')
    headers = {"Content-Type": "application/json"}
    body = {
        "account_number": customer.account_number,
        "fund_account_id": fund_id,
        "amount": amount * 100,
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
    cashback_ledger_new.customer = customer_id
    cashback_ledger_new.status = 'Redeemed'
    cashback_ledger_new.cashback_amount = amount
    cashback_ledger_new.fund_id = fund_id
    cashback_ledger_new.payment_id = request["id"]
    cashback_ledger_new.payment_status = request["status"]
    cashback_ledger_new.insert()
    cashback_ledger_new.submit()
    return request



@frappe.whitelist()
def webhook_razorpay(payload):
    payout = payload['payout']
    entity = payout['entity']
    payout_id = entity['id']
    status = entity['status']
    fuel_payment = frappe.db.get_all("Fuel Payment" , filters = {'payout_id':payout_id} , fields = ['name','payout_id'])
    if payout_id:
        for i in fuel_payment:
            if payout_id == i['payout_id']:
                fuel_payment_edit = frappe.get_doc("Fuel Payment" ,i['name'])
                fuel_payment_edit.payment_status = status
                fuel_payment_edit.save()
                fuel_payment_edit.submit()
                if fuel_payment_edit.payment_status == 'processed':
                    customer = frappe.get_doc("Customer" , fuel_payment_edit.customer)
                    customer.total_earned_cashback = int(customer.total_earned_cashback) + int(fuel_payment_edit.cashback)    
                    customer.balance_amount = int(customer.balance_amount) + int(fuel_payment_edit.cashback)
                    customer.save()
                    cashback_ledger = frappe.new_doc("CashBack Ledger")
                    cashback_ledger.fuel_payment_id = i['name']
                    cashback_ledger.customer = fuel_payment_edit.customer
                    cashback_ledger.amount = fuel_payment_edit.amount
                    cashback_ledger.cashback_amount = fuel_payment_edit.cashback
                    cashback_ledger.status = 'Recieved'
                    cashback_ledger.insert()
                    cashback_ledger.submit()
                    return 'sucess'
        else:
            ledger = frappe.db.get_all("CashBack Ledger", filters = {'payment_id': payout_id,}, fields = ['name','payment_id'])
            if payout_id:
                for i in ledger:
                    if payout_id == i['payment_id']:
                        ledger_update = frappe.get_doc("CashBack Ledger" ,i['name'])
                        ledger_update.payment_status = status
                        ledger_update.save()
                        ledger_update.submit()
                        if ledger_update.payment_status == 'processed':
                            customer = frappe.get_doc("Customer" , ledger_update.customer)
                            customer.total_earned_cashback = int(customer.total_earned_cashback) - int(ledger_update.cashback_amount)
                            customer.balance_amount = int(customer.balance_amount) - int(ledger_update.cashback_amount)
                            customer.save()
                            return "cashback sucess"




                     




# @frappe.whitelist()
# def razorpay_webhook(payload):
#     payment = payload['payment']
#     entity = payment['entity']
#     payout_id = entity['id']
#     status = entity['status']
#     ledger = frappe.db.get_all("CashBack Ledger", filters = {'payment_id': payout_id,}, fields = ['name','payment_id'])
#     if payout_id:
#         for i in ledger:
#             if payout_id == i['payment_id']:
#                 ledger_update = frappe.get_doc("CashBack Ledger" ,i['name'])
#                 ledger_update.payment_status = status
#                 ledger_update.save()
#                 ledger_update.submit()
#                 if status == 'captured':
#                     if ledger_update.customer == None:
#                         return ("Not A Customer")
                        
#                     else:
#                         customer = frappe.get_doc("Customer" ,ledger_update.customer)
#                         customer.balance_amount = int(customer.balance_amount) - int(ledger_update.amount)
#                         customer.save()
#                         return("balance Changed")

                    
#                 return("Sucess")
#             else:
#                 return ("payout Id Not Found")










# Save API Secret: 8ac2f21b72b3466


#     @frappe.whitelist()
# def razorpay_webhook(payload):
#     payment = payload['payment']
#     entity = payment['entity']
#     payout_id = entity['id']
#     status = entity['status']
#     ledger = frappe.db.get_all("CashBack Ledger", filters = {'payout_id': payout_id,}, fields = ['name','payout_id'])
#     if payout_id:
#         for i in ledger:
#             if payout_id == i['payout_id']:
#                 ledger_update = frappe.get_doc("CashBack Ledger" ,i['name'])
#                 ledger_update.cash_status = status
#                 ledger_update.save()
#                 ledger_update.submit()
#                 return("Sucess")
#             else:
#                 return ("This Payout_ID Not Found")

# @frappe.whitelist()
# def fund_account(contact_id,amount,customer):
# 	customer = frappe.get_doc("Customer",customer)
#     return 'hiii'
	# url = "https://api.razorpay.com/v1/fund_accounts"
	# auth=HTTPBasicAuth('rzp_test_BNRLROGFnxu3NQ', 'RjCCeIapanWPIgT95oUFQeJ8')
	# headers = {"Content-Type": "application/json"}
	# body = {
    #     "contact_id":contact_id,
    #     "account_type":customer.account_type,
    #     "bank_account":{
    #     "name":customer.name1,
    #     "ifsc":customer.ifsc,
    #     "account_number":customer.account_number
    #         }
    # }
	# req = requests.post(url, headers=headers , auth=auth ,  json=body)
	# request = req.json()
    # return request
	# fund_id = request['id']
	# fund = payout(fund_id,amount,customer)
    # return request
# @frappe.whitelist()
# def payout(fund_id,amount,customer):
# 	customer = frappe.get_doc("Customer" ,customer)
# 	url = 'https://api.razorpay.com/v1/payouts'
# 	auth=HTTPBasicAuth('rzp_test_BNRLROGFnxu3NQ', 'RjCCeIapanWPIgT95oUFQeJ8')
# 	headers = {"Content-Type": "application/json"}
# 	body = {
#         "account_number": customer.account_number,
#         "fund_account_id": fund_id,
#         "amount": amount * 100,
#         "currency": "INR",
#         "mode": "IMPS",
#         "purpose": "refund",
#         "queue_if_low_balance": True,
#         "reference_id": "Acme Transaction ID 12345",
#         "narration": "Acme Corp Fund Transfer",
#         "notes": {
#                 "notes_key_1":"Tea, Earl Grey, Hot",
#                 "notes_key_2":"Tea, Earl Grey… decaf."
#             }
#     }
# 	req = requests.post(url, headers=headers , auth=auth ,  json=body)
# 	request = req.json()
# 	cashback_ledger_new = frappe.new_doc("CashBack Ledger")
# 	cashback_ledger_new.customer = customer
# 	cashback_ledger_new.status = 'Redeemed'
# 	cashback_ledger_new.amount = amount
# 	cashback_ledger_new.fund_id = fund_id
# 	cashback_ledger_new.payment_id = request["id"]
# 	cashback_ledger_new.payment_status = request["status"]
# 	cashback_ledger_new.insert()
#     cashback_ledger_new.submit()

# {
#   "entity":"event",
#   "account_id":"acc_BfVUrG6tDiL7H0",
#   "event":"payout.processed",
#   "contains":[
#     "payout"
#   ],
#   "payload":{
#     "payout":{
#       "entity":{
#         "id":"pout_HD0nu9IeChvoHZ",
#         "entity":"payout",
#         "fund_account_id":"fa_1Aa00000000001",
#         "amount":100,
#         "currency":"INR",
#         "notes":{
#           "note_key 1":"Tea. Earl Gray. Hot.",
#           "note_key 2":"Tea. Earl Gray. Decaf."
#         },
#         "fees":3,
#         "tax":0,
#         "status":"processed",
#         "purpose":"payout",
#         "utr":"qwer1yuijaaasss",
#         "mode":"IMPS",
#         "reference_id":null,
#         "narration":"Acme Fund Transfer",
#         "batch_id":null,
#         "failure_reason":null,
#         "created_at":1579175640,
#         "fee_type": "",
#         "error": {
#           "description": null,
#           "source": null,
#           "reason": null
#         }
#       }
#     }
#   },
#   "created_at":1579175674
# }
