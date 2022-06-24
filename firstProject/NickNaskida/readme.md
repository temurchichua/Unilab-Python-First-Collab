# Unilab assignment

## General Info
- Project Author - Nikoloz Naskidashvili
- Project description - service booking system with ability to create and book services.
- Project reference - further project modifications may include users authentication system and documentation of api.

## API Docs
```
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
```

 - Reference: API docs are also available at api / route

