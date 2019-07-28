#!/usr/bin/env python
from RPi import GPIO
from time import sleep
from .utils import init_logger
import json
import sys
import os
import click

import logging
logger = logging.getLogger(__name__)

# Disable warnings
GPIO.setwarnings(False)
# Working with GPIO Numbers
GPIO.setmode(GPIO.BCM)


class SenseoClassicSimulator():
    """Define the setup and methods for the Senseo Classic Simulator.
    """

    def __init__(self, config_file: str):
        """Initialize the SenseoClassic simulator.

        Args:
            config_file (string): Path to the json config file.
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
        # Revert usage of PIN versus the SenseoClassic class
        GPIO.setup(self.power_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.one_mug_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.double_mug_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.led, GPIO.OUT)
        # Default state is off
        GPIO.output(self.led, GPIO.LOW)
        logger.info("Coffee machine setup is ready")


@click.group()
@click.pass_context
def cli(ctx={}):
    """Execute the Senseo Simulator.
    """
    ctx.ensure_object(dict)
    init_logger()
    ctx.obj['cms'] = SenseoClassicSimulator('~/.senseo-api/senseo_config.json')
    logger.info("Starting the Senseo Simulator...")


@cli.command()
@click.pass_context
def on(ctx):
    """Simulate a power on action.
    """
    logger.debug("Coffee Machine is ON and heating")
    while True:
        GPIO.output(ctx.obj['cms'].led, GPIO.HIGH)
        logger.debug(f"Current status for LED is: HIGH")
        sleep(0.5)
        GPIO.output(ctx.obj['cms'].led, GPIO.LOW)
        logger.debug(f"Current status for LED is: DOWN")
        sleep(0.5)


@cli.command()
@click.pass_context
def heat(ctx):
    """Simulate a ready coffee machine.
    """
    GPIO.output(ctx.obj['cms'].led, GPIO.HIGH)
    logger.debug("Coffee Machine is ON and Ready")
    while True:
        logger.debug(f"Current status for LED is: HIGH")
        sleep(1)


@cli.command()
@click.pass_context
def off(ctx):
    """Simulate a power off action.
    """
    GPIO.output(ctx.obj['cms'].led, GPIO.LOW)
    logger.debug("Coffee Machine is now OFF")


@cli.command()
@click.pass_context
def read(ctx):
    """Read the values on the buttons.
    """
    GPIO.output(ctx.obj['cms'].led, GPIO.HIGH)
    logger.debug("Coffee Machine is ON and Ready")
    sleep(0.5)
    logger.debug("Reading inputs for Coffee Machine buttons")
    while True:
        logger.info(f"Is [Power] pressed? " + str(GPIO.input(ctx.obj['cms'].power_button)))
        logger.info(f"Is [1 mug] pressed? " + str(GPIO.input(ctx.obj['cms'].one_mug_button)))
        logger.info(f"Is [2 mug] pressed? " + str(GPIO.input(ctx.obj['cms'].double_mug_button)))
        sleep(0.5)


def main():
    """Run the simulator.
    """
    try:
        cli(obj={})
    except(KeyboardInterrupt, click.Abort):
        #GPIO.output(cms.led, GPIO.LOW)
        GPIO.cleanup()
        logger.info("Stopping Coffee Machine Simulator")
        sys.exit(-1)


if __name__ == '__main__':
    main()