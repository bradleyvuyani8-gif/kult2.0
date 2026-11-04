import requests
import json
import uuid

class OrderService:
    PRINTIFY_API_URL = "https://api.printify.com/v1"

    @staticmethod
    def send_to_printify(cart_items, shipping_address, api_token, shop_id):
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

        line_items = []
        for item in cart_items:
            line_items.append({
                "product_id": item['printify_product_id'],
                "variant_id": item['variant_id'],
                "quantity": item['quantity']
            })

        payload = {
            "external_id": f"KULT-ORD-{uuid.uuid4()}",
            "line_items": line_items,
            "shipping_method": 1,
            "address_to": shipping_address
        }

        response = requests.post(
            f"{OrderService.PRINTIFY_API_URL}/shops/{shop_id}/orders.json",
            headers=headers,
            data=json.dumps(payload)
        )
        return response.json()
