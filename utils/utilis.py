import shortuuid

class Utilis:
    
    @staticmethod
    def genrate_otp():
        uniqe_key = shortuuid.uuid()
        otp_key = uniqe_key[ : 6]
        return otp_key
    
    
    @staticmethod
    def calculate_shipping(cart_item):
        return cart_item.shipping_amount
 
        
    @staticmethod
    def  calculate_total_service_fee(cart_item):
        return cart_item.service_fee
 
        
    @staticmethod
    def calculate_total_sub_total(cart_item):
        return cart_item.sub_total
 
 
    @staticmethod
    def calculate_total(cart_item):
        return cart_item.total
 
    @staticmethod
    def calculate_total_tax(cart_item):
        return cart_item.tax_fee   

