
from string import ascii_uppercase, digits
from random import SystemRandom


def generate_key(length=32):
	"""
	Generate a random alphanumeric key with '-' and '_' .

	Use length instead of special characters, to prevent possible problems with character encoding from external loggers.
	"""
	return ''.join(SystemRandom().choice(ascii_uppercase + digits + '0123456789--__') for _ in range(32))


