from bottle import Bottle, request, response, run
from marshmallow import Schema, fields, ValidationError
import uuid

class ItemSchema(Schema):
    id = fields.String(dump_only=True)  # Auto-generated ID
    name = fields.String(required=True)

item_schema = ItemSchema()
app = Bottle()
items = []

@app.route('/items', method='GET')
def get_items():
    return {"success": True, "data": items}

@app.route('/items', method='POST')
def create_item():
    if request.content_type != 'application/json':
        response.status = 400
        return {"success": False, "error": "Content-Type must be application/json"}
    try:
        data = request.json or {}
        if not data:
            response.status = 400
            return {"success": False, "error": "Request body is required"}
        validated_data = item_schema.load(data)
        validated_data['id'] = str(uuid.uuid4())
        items.append(validated_data)
        return {"success": True, "message": "Item created", "data": validated_data}
    except ValidationError as err:
        response.status = 400
        return {"success": False, "errors": err.messages}

@app.route('/items/<item_id>', method='GET')
def get_item(item_id):
    item = next((item for item in items if item['id'] == item_id), None)
    if not item:
        response.status = 404
        return {"success": False, "error": "Item not found"}
    return {"success": True, "data": item}

@app.route('/items/<item_id>', method='PUT')
def update_item(item_id):
    if request.headers.get('Content-Type') != 'application/json':
        response.status = 400
        return {"success": False, "error": "Content-Type must be application/json"}
    item = next((item for item in items if item['id'] == item_id), None)
    if not item:
        response.status = 404
        return {"success": False, "error": "Item not found"}
    try:
        data = request.json
        if not data:
            response.status = 400
            return {"success": False, "error": "Request body is required"}
        validated_data = item_schema.load(data)
        item.update(validated_data)
        return {"success": True, "message": "Item updated", "data": item}
    except ValidationError as err:
        response.status = 400
        return {"success": False, "errors": err.messages}

@app.route('/items/<item_id>', method='DELETE')
def delete_item(item_id):
    global items
    item = next((item for item in items if item['id'] == item_id), None)
    if not item:
        response.status = 404
        return {"success": False, "error": "Item not found"}
    items = [i for i in items if i['id'] != item_id]
    return {"success": True, "message": "Item deleted", "data": item}

if __name__ == '__main__':
    run(app, host='localhost', port=8080)
