from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from marshmallow import Schema, fields, validate, ValidationError, validates


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

# Initializations
db = SQLAlchemy(app)  # Database
api = Api(app)  # API


# Database models
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300))

    def __repr__(self):
        return f'<Service - {self.name}>'


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id', ondelete='RESTRICT'), nullable=False)
    service = db.relationship("Service", backref=db.backref("service", uselist=False))

    def __repr__(self):
        return f'<Booking - {self.service}>'


# Schemas
class ServiceSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    description = fields.Str(required=True, validate=validate.Length(min=2, max=300))


service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)


class BookingSchema(Schema):
    id = fields.Int(dump_only=True)
    service_id = fields.Int(required=True)
    service = fields.Nested(ServiceSchema, dump_only=True)

    @validates("service_id")
    def validate_quantity(self, service_id):
        service = Service.query.get(service_id)
        if not service:
            raise ValidationError(f"Service wit id - {service_id} does not exist.")


booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)


# Views
class Main(Resource):
    def get(self):
        return {
            'Services': {
                'docs': 'Get / Add services',
                'url': '/services',
                'methods': {
                    'GET': 'Returns all services from database',
                    'POST': 'Adds service to the database'
                }
            },
            'Get service': {
                'docs': 'Get service from database',
                'url': 'services/get/<service_id>',
                'arguments': '<service_id> - Integer',
                'methods': {
                    'GET': 'Return service with <service_id> from database'
                }
            },
            'Edit service': {
                'docs': 'Edits service in database',
                'url': 'services/edit/<service_id>',
                'arguments': '<service_id> - Integer',
                'methods': {
                    'PUT': 'Returns edited service with <service_id> from database'
                }
            },
            'Delete service': {
                'docs': 'Deletes service from database',
                'url': 'services/delete/<service_id>',
                'arguments': '<service_id> - Integer',
                'methods': {
                    'DELETE': 'Deletes service with <service_id> from database'
                }
            },
            'Bookings': {
                'docs': 'Get / Add bookings',
                'url': '/bookings',
                'methods': {
                    'GET': 'Returns all bookings from database',
                    'POST': 'Adds booking to the database'
                }
            },
            'Get booking': {
                'docs': 'Get booking from database',
                'url': 'bookings/get/<booking_id>',
                'arguments': '<booking_id> - Integer',
                'methods': {
                    'GET': 'Return service with <booking_id> from database'
                }
            },
            'Edit booking': {
                'docs': 'Edits booking in database',
                'url': 'services/edit/<booking_id>',
                'arguments': '<booking_id> - Integer',
                'methods': {
                    'PUT': 'Returns edited booking with <booking_id> from database'
                }
            },
            'Delete booking': {
                'docs': 'Deletes booking from database',
                'url': 'services/delete/<booking_id>',
                'arguments': '<booking_id> - Integer',
                'methods': {
                    'DELETE': 'Deletes booking with <booking_id> from database'
                }
            }
        }


# Service
class Services(Resource):
    def get(self):
        services = Service.query.all()
        return services_schema.dump(services)

    def post(self):
        try:
            new_service = Service(
                name=request.json['name'],
                description=request.json['description']
            )
        except KeyError as e:
            return {"message": f"KeyError, Missing key: <{e}>"}

        try:
            service_schema.load({"name": request.json['name'], "description": request.json['description']})
        except ValidationError as e:
            return e.messages

        db.session.add(new_service)
        db.session.commit()

        return service_schema.dump(new_service)


class GetService(Resource):
    def get(self, service_id):
        service = Service.query.get_or_404(service_id)
        return service_schema.dump(service)


class EditService(Resource):
    def put(self, service_id):
        service = Service.query.get_or_404(service_id)

        try:
            service_schema.load({"name": request.json['name'], "description": request.json['description']})
        except ValidationError as e:
            return e.messages

        try:
            if 'name' in request.json:
                service.name = request.json['name']

            if 'description' in request.json:
                service.description = request.json['description']
        except KeyError as e:
            return {"message": f"KeyError, Missing key: <{e}>"}

        db.session.commit()
        return service_schema.dump(service)


class DeleteService(Resource):
    def delete(self, service_id):
        service = Service.query.get_or_404(service_id)
        try:
            db.session.delete(service)
            db.session.commit()
        except exc.IntegrityError:
            return {"message": "Can not perform delete operation. This service has active bookings, delete them first"}

        return '', 204


# Booking
class GetServiceBookings(Resource):
    def get(self):
        bookings = Booking.query.all()
        return bookings_schema.dump(bookings)

    def post(self):
        try:
            new_booking = Booking(
                service_id=request.json['service_id'],
            )
        except KeyError as e:
            return {"message": f"KeyError, Missing key: <{e}>"}

        try:
            booking_schema.load({"service_id": request.json['service_id']})
        except ValidationError as e:
            return e.messages

        db.session.add(new_booking)
        db.session.commit()

        return booking_schema.dump(new_booking)


class GetServiceBooking(Resource):
    def get(self, booking_id):
        booking = Booking.query.get_or_404(booking_id)
        return booking_schema.dump(booking)


class EditServiceBooking(Resource):
    def put(self, booking_id):
        booking = Booking.query.get_or_404(booking_id)

        try:
            if 'service_id' in request.json:
                booking.service_id = request.json['service_id']
        except KeyError as e:
            return {"message": f"KeyError, Missing key: <{e}>"}

        try:
            booking_schema.load({"service_id": request.json['service_id']})
        except ValidationError as e:
            return e.messages

        db.session.commit()
        return booking_schema.dump(booking)


class DeleteServiceBooking(Resource):
    def delete(self, booking_id):
        booking = Booking.query.get_or_404(booking_id)
        db.session.delete(booking)
        db.session.commit()
        return '', 204


api.add_resource(Main, '/')
api.add_resource(Services, '/services')
api.add_resource(GetService, '/services/get/<int:service_id>')
api.add_resource(EditService, '/services/edit/<int:service_id>')
api.add_resource(DeleteService, '/services/delete/<int:service_id>')
api.add_resource(GetServiceBookings, '/bookings')
api.add_resource(GetServiceBooking, '/bookings/get/<int:booking_id>')
api.add_resource(EditServiceBooking, '/bookings/edit/<int:booking_id>/')
api.add_resource(DeleteServiceBooking, '/bookings/delete/<int:booking_id>')

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
