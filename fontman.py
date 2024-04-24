import json
import requests
import re
import shutil
import tarfile
import zipfile
import os
from sys import argv
from termcolor import colored

database = []

def binary_search(target, lo, hi):
	global database
	midpoint = (hi+lo)//2

	if lo > hi:
		return { "Error": "Font not found." }

	if database[midpoint]["font-id"] == target:
		return database[midpoint]
	elif database[midpoint]["font-id"] > target:
		return binary_search(target, lo, midpoint)
	else:
		return binary_search(target, midpoint, hi)
	
def get_filename(link: str):
	return link.split('/')[-1]

	
def print_font(font: dict):
	if "Error" in font.keys():
		print(f"{colored("Error:", "red", attrs=["bold"])} could not find font.")
		return
	print(f"{colored("Name:", "green", attrs=["bold"])} {font["name"]}")
	print(f"{colored("font-id:", "green", attrs=["bold"])} {font["font-id"]}")
	print(f"{colored("Author:", "green", attrs=["bold"])} {font["creator"]}")
	print(f"{colored("Twitter:", "green", attrs=["bold"])} {font["twitter"]}")
	print(f"{colored("Github:", "green", attrs=["bold"])} {font["github"]}")
	print(f"{colored("Website:", "green", attrs=["bold"])} {font["creator-link"]}")
	print(f"{colored("About:", "green", attrs=["bold"])} {font["about"]}")
	print(f"{colored("License:", "green", attrs=["bold"])} {font["license"]}")
	print(f"{colored("Download:", "green", attrs=["bold"])} {font["download"]}")

def is_error(font: dict) -> bool:
	if "Error" in font.keys():
		return True
	return False

def main():
	global database
	fonts = []
	with open("index.json", "r") as file:
		fonts = json.loads(file.read())
	database = sorted(fonts, key=lambda x: x["font-id"])
	parse()

def usage():
	print("The font package manager for MacOS.")
	print("usage: python3 fontman.py (install | download | remove | search | info) <font-id>")
	print("Additional commands:")
	print("init")
	print("list")

def install(package: str):
	print(f"{colored(":: Installing font", "green", attrs=["bold"])} {package}...")
	item = binary_search(package, 0, len(database)-1)
	if is_error(item):
		return
	print(f"{colored("Downloading from", "green", attrs=["bold"])} {item["download"]}")
	dwnld = requests.get(item["download"], allow_redirects=True)
	filename = get_filename(dwnld.url)
	print(f"{colored("Retrieved file", "green", attrs=["bold"])} {filename}")
	with open(f"./fonts/{filename}", 'wb') as file:
		file.write(dwnld.content)
	#shutil.move(f"./{filename}", f"Desktop")
	if filename.endswith(".zip"):
		print(f"{colored("Unpacking", "green", attrs=["bold"])} {filename}...")
		zipf = zipfile.ZipFile(f"./fonts/{filename}")
		for item in os.listdir("./fonts"):
			os.remove(f"./fonts/{filename}")
		zipf.extractall("./fonts")
	desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') 
	for item in os.listdir("./fonts"):
		shutil.move(f"./fonts/{item}", desktop)
	print(f"{colored(":: Sucessfully installed", "green", attrs=["bold"])} {package}!")
	
	
def remove(package: str):
	print(f"{colored(":: Removing font", "green", attrs=["bold"])} {package}...")

def init():
	print(colored(":: Initializing...", attrs=["bold"]))

def info(package: str):
	item = binary_search(package, 0, len(database)-1)
	print_font(item)

def search(query: str):
	print(f"{colored(":: Searching for font", "green", attrs=["bold"])} {colored(query, attrs=["bold"])}...")

def download(package):
	pass

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

		case "download":
			download(argv[2])

		case "info":
			info(argv[2])

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
	main()
