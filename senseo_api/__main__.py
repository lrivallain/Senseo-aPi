#!/usr/bin/env python
from flask import Flask, request
from flask_restplus import Api, Resource, fields, abort
from .pisenseo import SenseoClassic, SenseoPreconditionError, SenseoCoffeeSizeError
from .utils import init_logger

import logging
logger = logging.getLogger(__name__)


app = Flask(__name__)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
app.config.SWAGGER_UI_OPERATION_ID = True
app.config.SWAGGER_UI_REQUEST_DURATION = True
api = Api(
    app,
    version='1.0',
    title='Senseo APi',
    description='Manage Senseo coffee machine through Raspberry Pi GPIO',
)
ns_cm = api.namespace('senseo', description='Senseo coffee machine operations')
ns_coffee = api.namespace('coffee', description='Coffee operations')

# Will be used by a global
cm = None

# describe models
machine_status = api.model('Machine Status', {
    'is_powered_on': fields.Boolean(
        readOnly=True,
        description='Is the coffee machine powered on?'
    ),
    'is_ready': fields.Boolean(
        readOnly=True,
        description='Is the coffee machine ready to start a coffee?'
    )
})
machine_power_op = api.model(
    'Machine power operation', {
    'power_on': fields.Boolean(
        required=True,
        description='Start or stop coffee machine.'
    )
})
coffee_request = api.model('Start a coffee', {
    'size': fields.Integer(
        required=True,
        description='Size of the requested coffeee (1 or 2 mug)',
        min=1,
        max=2,
        example=1
    )
})
message_op = api.model('Response message regarding the current request', {
    'message': fields.String(
        description='Description of the response made to the request.'
    )
})

@ns_cm.route('/')
class CoffeeMachine(Resource):
    """Set and get power status for the coffee machine
    """

    @ns_cm.marshal_with(machine_status)
    def get(self):
        """Get the current status of the coffee machine
        """
        logger.info("Current status of coffee machine is requested")
        return {
            'is_powered_on': cm.is_powered_on(),
            'is_ready': cm.is_ready()
        }

    @ns_cm.marshal_with(message_op)
    @ns_cm.expect(machine_power_op)
    def post(self):
        """Update the power state of the coffee machine
        """
        req_status = request.json.get('power_on', True) # default is shutdown command
        cur_status = cm.is_powered_on()
        logger.info("Update of power status of the coffe machine is requested.")
        # Require powered on and currently powered off
        if req_status and not cur_status:
            logger.debug("Start requested")
            cm.start()
            return {"message": "Powering on..."}
        # Require powered off and currently powered on
        if not req_status and cur_status:
            logger.debug("Stop requested")
            cm.stop()
            return {"message": "Powering off..."}
        # Other cases: do nothing
        #if (req_status and cur_status) or (not req_status and not cur_status):
        logger.info("Nothing to do: already at requested state.")
        return {"message": "Nothing to do."}


@ns_coffee.route('/')
class CoffeeRun(Resource):
    """Start a coffee
    """

    @ns_cm.response(400, 'Invalid size')
    @ns_cm.response(412, 'Precondition failed')
    @ns_cm.response(500, 'Internal server error')
    @ns_cm.marshal_with(message_op)
    @ns_coffee.expect(coffee_request)
    def post(self):
        """Send command to start coffee according to the requested size.
        """
        size = request.json.get('size', 1)  # default size is 1 cup
        logger.info(f"{size} mug(s) coffee requested.")
        try:
            cm.coffee(size)
        except SenseoPreconditionError as e:
            abort(412, e.message)
        except SenseoCoffeeSizeError as e:
            abort(400, e.message)
        except Exception as e:
            abort(500, f"Unmanaged server error: {str(e)}")
        return {"message": f"Starting coffee with size: {size} mug(s)"}


def main():
    """Execute the API
    """
    global cm
    init_logger()
    cm = SenseoClassic('~/.senseo-api/senseo_config.json')
    logger.info("Starting the Senseo APi...")
    app.run(debug=False, host='0.0.0.0')


if __name__ == '__main__':
    main()