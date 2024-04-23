import json
import requests
import re
from sys import argv
from termcolor import colored

def usage():
	print("The font package manager for MacOS.")
	print("usage: python3 fontman.py (install | remove | search | info) <package>")
	print("Additional commands:")
	print("init")
	print("list")

def install(package: str):
	print(f"{colored(":: Installing", "green", attrs=["bold"])} font {package}...")
	

def remove(package: str):
	print(f"{colored(":: Removing", "green", attrs=["bold"])} font {package}...")

def init():
	print(colored(":: Initializing...", attrs=["bold"]))

def info(package: str):
	pass

def search(query: str):
	print(f"{colored(":: Searching for", "green", attrs=["bold"])} font {colored(query, attrs=["bold"])}...")

def parse():
	if len(argv) == 1:
		usage()
		return
	match argv[1]:
		case "install":
			install(argv[2])

		case "remove":
			remove(argv[2])

		case "search":
			search(argv[2])
			pass

		case "info":
			pass

		case "init":
			init()

		case "-h":
			usage()

		case "--help":
			usage()

		case _:
			print(f"Unknown option `{argv[1]}`")
			usage()
			return

if __name__ == '__main__':
	parse()
