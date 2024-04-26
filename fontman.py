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

def binary_search(array, target, lo, hi):
	midpoint = (hi+lo)//2

	if lo > hi:
		return { "Error": "Font not found." }
	
	try:
		if array[midpoint]["font-id"] == target:
			return array[midpoint]
		elif array[midpoint]["font-id"] > target:
			return binary_search(array, target, lo, midpoint)
		else:
			return binary_search(array, target, midpoint, hi)
	except:
		return { "Error": "Font not found." }
	
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
	database = fonts
	parse()

def usage():
	print("The font package manager for MacOS.")
	print("usage: python3 fontman.py (install | download | remove | search | info) <font-id>")
	print("Additional commands:")
	print("list")

def unzip(filename):
	print(f"{colored("Unpacking", "green", attrs=["bold"])} {filename}...")
	zipf = zipfile.ZipFile(f"./fonts/{filename}")
	clear_font_dir()
	zipf.extractall("./fonts")

def error(string):
	print(f"{colored("Error:", "red", attrs=["bold"])} {string}")

def clear_font_dir():
	for item in os.listdir("./fonts"):
		os.remove(f"./fonts/{item}")

def list_installed_fonts():
	with open("installed.json", "r+") as file:
		x = file.read()

		if x == "":
			return
		
		installed = json.loads(x)
		
		for font in installed:
			print(font["font-id"])

def add_to_installed(filename, package):
	installed = load_installed()

	if is_installed(package):
		pack = binary_search(installed, package, 0, len(installed))
		pack["files"].append({"file": f"{filename}"})
	else:
		font = {}
		font["font-id"] = package
		font["files"] = []
		font["files"].append({"file": f"{filename}"})
		installed.append(font)
	write_installed(sorted(installed, key=lambda x: x["font-id"]))

		
def extract_tar(filename):
	print(f"{colored("Unpacking", "green", attrs=["bold"])} {filename}...")
	tarf = tarfile.TarFile(f"./fonts/{filename}")
	clear_font_dir()
	tarf.extractall("./fonts")

def printgab(special, rem):
	print(f"{colored(special, "green", attrs=["bold"])} {rem}")

def install(package: str):

	if is_installed(package):
		print(f"{package} is already installed.")
		return

	printgab(":: Installing font", f"{package}...")
	item = binary_search(database, package, 0, len(database))

	if is_error(item):
		error(f"Could not find font '{item}'")
		return
	
	print(f"{colored("Downloading from", "green", attrs=["bold"])} {item["download"]}")

	try:
		dwnld = requests.get(item["download"], allow_redirects=True)
	except:
		error("An error occured downloading the font. Aborting")
		return
	
	filename = get_filename(item["download"])
	print(f"{colored("Retrieved file", "green", attrs=["bold"])} {filename}")

	with open(f"./fonts/{filename}", 'wb') as file:
		file.write(dwnld.content)

	if filename.endswith(".zip"):
		try:
			unzip(filename)
		except zipfile.BadZipFile:
			error("Retrieved file is a bad zip file, or not a zip file at all. Aborting.")
			clear_font_dir()
			return
	elif filename.endswith(".tar.gz"):
		try:
			extract_tar(filename)
		except:
			error("Retrieved file is a bad tar file, or not a tar file at all. Aborting.")
			clear_font_dir()
			return
		
	try:
		fontdir = os.path.join(os.path.join(os.path.expanduser('~')), 'Library/Fonts') 
		for item in os.listdir("./fonts"):
			shutil.move(f"./fonts/{item}", fontdir)
			add_to_installed(item, package)
	except:
		error("An error occurred while moving font files. Aborting.")
		return

	print(f"{colored("Moving font assets to", "green", attrs=["bold"])} {fontdir}")
	print(f"{colored(":: Sucessfully installed", "green", attrs=["bold"])} {package}!")
	
	
def remove(package: str):

	if not is_installed(package):
		print(f"{package} is not installed.")
		return
	
	printgab(":: Removing font", f"{package}...")
	
	installed = load_installed()
	font = binary_search(installed, package, 0, len(installed))

	fontdir = os.path.join(os.path.join(os.path.expanduser('~')), 'Library/Fonts')

	for item in font["files"]:
		if os.path.isdir(f"{fontdir}/{item["file"]}"):
			shutil.rmtree(f"{fontdir}/{item["file"]}")
		else:
			os.remove(f"{fontdir}/{item["file"]}")

	remove_from_installed(package)

	printgab(":: Successfully removed font", package)

def write_installed(new_json):
	with open("installed.json", "r+") as file:
		file.seek(0)
		file.truncate()
		file.write(json.dumps(new_json, indent=4))


def remove_from_installed(font_id):
	if not is_installed(font_id):
		return
	installed: list = load_installed()
	to_remove = 0
	for idx, item in enumerate(installed):
		if item["font-id"] == font_id:
			to_remove = idx
			break
	del installed[to_remove]
	write_installed(installed)

def info(package: str):
	item = binary_search(database, package, 0, len(database))
	print_font(item)

def search(query: str):
	print(f"{colored(":: Searching for font", "green", attrs=["bold"])} {colored(query, attrs=["bold"])}...")
	matched = []
	for font in database:
		try:
			if re.match(query, font["font-id"]):
				matched.append(font)
		except:
			error("Invalid query entered.")
			return
	printgab("Found", f"{colored(len(matched), "white", attrs=["bold"])} matches.")
	for match in matched:
		print(match["font-id"])

def download(package):
	printgab(":: Downloading font", package)
	pack = binary_search(database, package, 0, len(database))
	if is_error(pack):
		error(f"Could not find font {pack}")
		return
	try:
		x = requests.get(pack["download"])
		filename = get_filename(pack["download"])
		with open(f"./fonts/{filename}", "wb") as file:
			file.write(x.content)
	except:
		error("An error occured downloading this font.")
		return
	downloadpath = os.path.join(os.path.join(os.path.expanduser("~")), "Downloads")
	shutil.move(f"./fonts/{filename}", downloadpath)
	printgab(":: Sucessfully downloaded font", f"{package}!")

def load_installed() -> list:
	with open("installed.json", "r+") as file:
		x = file.read()
		if x == "":
			return []
		return json.loads(x)

def is_installed(font_id) -> bool:
	x: list = load_installed()
	if len(x) == 0:
		return False
	ids = [font["font-id"] for font in x]
	return font_id in ids

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

		case "download":
			download(argv[2])

		case "list":
			list_installed_fonts()

		case "info":
			info(argv[2])

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
