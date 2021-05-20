
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
    cashback_ledger_new.amount = amount
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
                    customer.submit()
                    return 'sucess'


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
# {
#   "entity": "event",
#   "account_id": "acc_BFQ7uQEaa7j2z7",
#   "event": "order.paid",
#   "contains": [
#     "payment",
#     "order"
#   ],
#   "payload": {
#     "payment": {
#       "entity": {
#         "id": "pout_H8HFbirXApM9yZ",
#         "entity": "payment",
#         "amount": 100,
#         "currency": "INR",
#         "status": "captured",
#         "order_id": "order_DESlLckIVRkHWj",
#         "invoice_id": null,
#         "international": false,
#         "method": "netbanking",
#         "amount_refunded": 0,
#         "refund_status": null,
#         "captured": true,
#         "description": null,
#         "card_id": null,
#         "bank": "HDFC",
#         "wallet": null,
#         "vpa": null,
#         "email": "gaurav.kumar@example.com",
#         "contact": "+919876543210",
#         "notes": [],
#         "fee": 2,
#         "tax": 0,
#         "error_code": null,
#         "error_description": null,
#         "created_at": 1567674599
#       }
#     },
#     "order": {
#       "entity": {
#         "id": "order_DESlLckIVRkHWj",
#         "entity": "order",
#         "amount": 100,
#         "amount_paid": 100,
#         "amount_due": 0,
#         "currency": "INR",
#         "receipt": "rcptid #1",
#         "offer_id": null,
#         "status": "paid",
#         "attempts": 1,
#         "notes": [],
#         "created_at": 1567674581
#       }
#     }
#   },
#   "created_at": 1567674606
# }


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


