# from __future__ import unicode_literals
# from frappe.model.document import Document
# from requests.auth import HTTPBasicAuth
# import requests
# import hmac
# import hashlib
# import sys
# import frappe

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
#                 return("Sucess")
#             else:
#                 return ("payout Id Not Found")
