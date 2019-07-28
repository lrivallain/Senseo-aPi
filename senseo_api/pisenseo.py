#!/usr/bin/env python

import os
import json
from time import sleep
from RPi import GPIO


import logging
logger = logging.getLogger(__name__)

MAX_READY_RETRY = 60
PRESS_DELAY = 1
WAIT_RETRY = 0.5
# Disable warnings
GPIO.setwarnings(False)
# Working with GPIO Numbers
GPIO.setmode(GPIO.BCM)


class SenseoPreconditionError(Exception):
    """Define a specific error for non-readyness coffee machine.
    """

    def __init__(self, message: str):
        """Initialize the execption.

        Args:
            message (str): Message to raise with error.
        """
        self.message = message
        # Call the base class constructor with the parameters it needs
        super(SenseoPreconditionError, self).__init__(message)
        logger.error(f"[{self.__class__.__name__}] {message}")


class SenseoCoffeeSizeError(Exception):
    """Define a specific error for invalid coffee size.
    """

    def __init__(self, size):
        """Initialize the execption.

        Args:
            message (str): Message to raise with error.
        """
        self.message = f"Invalid coffee size requested: {size}. Only 1 or 2 are accepted."
        # Call the base class constructor with the parameters it needs
        super(SenseoCoffeeSizeError, self).__init__(self.message)
        logger.error(f"[{self.__class__.__name__}] {self.message}")


class SenseoClassic():
    """Define the setup and methods for the Senseo Classic.

    May works on other kind of Senseo machine but not tested.
    """

    def __init__(self, config_file: str):
        """Initialize the SenseoClassic object.

        Args:
            config_file (str): Path to the json config file.
        """
        with open(os.path.expanduser(config_file), "r", encoding="utf-8") as fd:
            self.gpio_setup = json.load(fd)
        # Map GPIO pin configuration for in/out
        self.power_button = self.gpio_setup.get('power_button')
        logger.trivia(f"power_button pin is n°{self.power_button}")
        self.one_mug_button = self.gpio_setup.get('1_mug_button')
        logger.trivia(f"one_mug_button pin is n°{self.one_mug_button}")
        self.double_mug_button = self.gpio_setup.get('2_mug_button')
        logger.trivia(f"double_mug_button pin is n°{self.double_mug_button}")
        self.led = self.gpio_setup.get('led')
        logger.trivia(f"led pin is n°{self.led}")
        # PIN setup
        GPIO.setup(self.power_button, GPIO.OUT)
        GPIO.setup(self.one_mug_button, GPIO.OUT)
        GPIO.setup(self.double_mug_button, GPIO.OUT)
        GPIO.setup(self.led, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # Default state is off everywhere
        GPIO.output(self.power_button, GPIO.LOW)
        GPIO.output(self.one_mug_button, GPIO.LOW)
        GPIO.output(self.double_mug_button, GPIO.LOW)
        logger.info("Coffee machine setup is ready")

    def is_led_on(self):
        """Return a boolean according to the current led status.

        Returns:
            Boolean: led powered status
        """
        return bool(GPIO.input(self.led))


    def is_powered_on(self):
        """Is the Senseo up?

        Returns:
            Boolean: Power status of the Senseo
        """
        logger.debug("Checking power status of coffee machine")
        for i in range(0,10): # retest few times
            is_on = self.is_led_on()
            logger.debug(f"Current value for LED is: {is_on}")
            if is_on:
                logger.info("Coffee machine is powered on")
                return True
            logger.debug("Need to retry the power status check")
            sleep(WAIT_RETRY)  # wait between two retries
        # LED is not powered on since a few seconds, let consider coffee machine is down
        logger.info("Coffee machine is powered off")
        return False


    def is_ready(self):
        """Is the Senseo heat enough?

        Returns:
            Boolean: Heat status of the Senseo
        """
        logger.debug("Checking readyness of coffee machine")
        for i in range(0,10): # retest few times
            is_on = self.is_led_on()
            logger.debug(f"Current value for LED is: {is_on}")
            if is_on:
                logger.debug("Need to retry check for readyness")
            else:
                # At lest the coffee machine is still heating
                logger.info("Coffee machine is not ready.")
                return False
            sleep(WAIT_RETRY)  # wait a second before next try
        # LED is powered on since a few seconds, let consider ready.
        logger.info("Coffee machine is ready")
        return True


    def single_press(self, button: int):
        """Press a specific button for a short period.

        Args:
            button (int): Button to press
        """
        logger.info(f"Pressing a button for {PRESS_DELAY}s.")
        GPIO.output(button, GPIO.HIGH) # press button
        sleep(PRESS_DELAY)
        GPIO.output(button, GPIO.LOW) # unpress
        logger.debug(f"Button was successfully pressed.")


    def start(self):
        """Power on the Senseo.
        """
        logger.debug("Powering on is requested")
        if not self.is_powered_on():
            logger.info("Pressing power button to startup.")
            self.single_press(self.power_button)
        return


    def stop(self):
        """Power off the Senseo.
        """
        logger.debug("Powering off is requested")
        if self.is_powered_on():
            logger.info("Pressing power button to shutdown.")
            self.single_press(self.power_button)
        return


    def coffee(self, size: int):
        """Start a coffee run according the selected number of mugs.

        Args:
            size (integer): Number of mug selected. 1 or 2.
        """
        if size not in [1,2]:
            raise SenseoCoffeeSizeError(size)
        if size == 1:
            logger.debug("1 mugs coffee size requested")
            coffee_button = self.one_mug_button
        if size == 2:
            logger.debug("2 mug coffee size requested")
            coffee_button = self.double_mug_button
        # Test if coffee machine is ready
        if not self.is_powered_on():
            logger.error("Coffee machine is not on: aborting.")
            raise SenseoPreconditionError("Coffe machine is not on: aborting.")
        if not self.is_ready():
            logger.error("Coffe machine is not ready: aborting.")
            raise SenseoPreconditionError("Coffe machine is not ready: aborting.")
        # Press appropriate button for a short time
        logger.info("Requesting coffee run.")
        self.single_press(coffee_button)
        return
