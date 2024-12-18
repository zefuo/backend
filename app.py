import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from models import StartEndPoint, Vehicle, WastePoint, db

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///waste_management2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Veritabanını oluştur
with app.app_context():
    db.create_all()

# Hata yakalama fonksiyonu
def handle_error(e, status_code=500):
    return jsonify({"error": str(e)}), status_code

# Vehicle endpoints
@app.route('/vehicles', methods=['GET'])
def get_vehicles():
    try:
        vehicles = Vehicle.query.all()
        return jsonify([{
            'id': v.id,
            'plate': v.plate,
            'brand': v.brand,
            'model': v.model
        } for v in vehicles]), 200
    except Exception as e:
        return handle_error(e)

@app.route('/vehicles', methods=['POST'])
def create_vehicle():
    try:
        data = request.get_json()
        vehicle = Vehicle(
            plate=data['plate'],
            brand=data.get('brand'),
            model=data.get('model')
        )
        db.session.add(vehicle)
        db.session.commit()
        return jsonify({
            'id': vehicle.id,
            'plate': vehicle.plate,
            'brand': vehicle.brand,
            'model': vehicle.model
        }), 201
    except Exception as e:
        return handle_error(e, 400)

@app.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({"error": "Araç bulunamadı"}), 404
            
        db.session.delete(vehicle)
        db.session.commit()
        return '', 204
    except Exception as e:
        return handle_error(e)

# WastePoint endpoints
@app.route('/waste-points', methods=['GET'])
def get_waste_points():
    try:
        points = WastePoint.query.all()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'latitude': p.latitude,
            'longitude': p.longitude
        } for p in points]), 200
    except Exception as e:
        return handle_error(e)

@app.route('/waste-points', methods=['POST'])
def create_waste_point():
    try:
        data = request.get_json()
        point = WastePoint(
            name=data['name'],
            latitude=data['latitude'],
            longitude=data['longitude']
        )
        db.session.add(point)
        db.session.commit()
        return jsonify({
            'id': point.id,
            'name': point.name,
            'latitude': point.latitude,
            'longitude': point.longitude
        }), 201
    except Exception as e:
        return handle_error(e, 400)

@app.route('/waste-points/<int:point_id>', methods=['DELETE'])
def delete_waste_point(point_id):
    try:
        point = WastePoint.query.get(point_id)
        if not point:
            return jsonify({"error": "Atık noktası bulunamadı"}), 404
            
        db.session.delete(point)
        db.session.commit()
        return '', 204
    except Exception as e:
        return handle_error(e)

# StartEndPoint endpoints - özel endpoint'ler
@app.route('/start-end-points/start', methods=['GET'])
def get_start_point():
    try:
        point = StartEndPoint.query.filter_by(point_type='start').first()
        if not point:
            return jsonify(None), 200
            
        return jsonify({
            'id': point.id,
            'latitude': point.latitude,
            'longitude': point.longitude,
            'point_type': 'start'
        }), 200
    except Exception as e:
        return handle_error(e)

@app.route('/start-end-points/dump', methods=['GET'])
def get_dump_point():
    try:
        point = StartEndPoint.query.filter_by(point_type='end').first()
        if not point:
            return jsonify(None), 200
            
        return jsonify({
            'id': point.id,
            'latitude': point.latitude,
            'longitude': point.longitude,
            'point_type': 'end'
        }), 200
    except Exception as e:
        return handle_error(e)

@app.route('/start-end-points/start', methods=['POST'])
def save_start_point():
    try:
        data = request.get_json()
        
        # Mevcut başlangıç noktasını kontrol et
        existing_point = StartEndPoint.query.filter_by(point_type='start').first()
        
        if existing_point:
            # Mevcut noktayı güncelle
            existing_point.latitude = data['latitude']
            existing_point.longitude = data['longitude']
            point = existing_point
        else:
            # Yeni nokta oluştur
            point = StartEndPoint(
                point_type='start',
                latitude=data['latitude'],
                longitude=data['longitude']
            )
            db.session.add(point)
            
        db.session.commit()
        return jsonify({
            'id': point.id,
            'latitude': point.latitude,
            'longitude': point.longitude,
            'point_type': 'start'
        }), 201
    except Exception as e:
        return handle_error(e, 400)

@app.route('/start-end-points/dump', methods=['POST'])
def save_dump_point():
    try:
        data = request.get_json()
        
        # Mevcut döküm noktasını kontrol et
        existing_point = StartEndPoint.query.filter_by(point_type='end').first()
        
        if existing_point:
            # Mevcut noktayı güncelle
            existing_point.latitude = data['latitude']
            existing_point.longitude = data['longitude']
            point = existing_point
        else:
            # Yeni nokta oluştur
            point = StartEndPoint(
                point_type='end',
                latitude=data['latitude'],
                longitude=data['longitude']
            )
            db.session.add(point)
            
        db.session.commit()
        return jsonify({
            'id': point.id,
            'latitude': point.latitude,
            'longitude': point.longitude,
            'point_type': 'end'
        }), 201
    except Exception as e:
        return handle_error(e, 400)

# Count endpoints
@app.route('/counts', methods=['GET'])
def get_counts():
    try:
        vehicle_count = Vehicle.query.count()
        waste_point_count = WastePoint.query.count()
        
        # Şu an için routes tablosu olmadığı için 0 döndürüyoruz
        # İleride route tablosu eklenirse burası güncellenebilir
        route_count = 0
        
        return jsonify({
            'vehicles': vehicle_count,
            'wastePoints': waste_point_count,
            'routes': route_count
        }), 200
    except Exception as e:
        return handle_error(e)

if __name__ == '__main__':
    app.run(debug=True) 