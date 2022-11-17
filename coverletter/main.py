import argparse
import signal
import sys
import os
from datetime import datetime

from pymongo import MongoClient, errors
import pyperclip
import textwrap
from fpdf import FPDF

def create_cli_parser():
    parser = argparse.ArgumentParser(
                    prog = 'Cover Letter CLI',
                    description = 'Simple tool to generate custom cover letter from the command line',
                    )
    parser.add_argument('-p','--pdf', action='store_true', default=False, help="Save cover letter as a pdf to current directory.")
    parser.add_argument('-n','--name', default=None, help="Name of template document in mongoDB")
    parser.add_argument('--path',default=None, help="Path to template .txt file.")
    parser.add_argument('-a', '--add', default=None, help="Path of .txt to add to mongoDB")
    parser.add_argument('-d', '--delete', default=None, help="Path of .txt to add to mongoDB")
    return parser

def term_handler(signum, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, term_handler)

def get_template_from_file(path):
    if not isinstance(path, str) or not os.path.exists(os.path.join(os.getcwd(), path)):
        print("Invalite path to template: " + path)

    with open(os.path.join(os.getcwd(), path), 'r') as f:
        template = f.read()
    
    return template

def parse_variables(template):
    vars = {}
    prev = None
    escape = False
    name_chars = []
    for char in template:
        if char == '{' and prev == '$':
            escape = True
            continue
        if escape:
            if char == '}': 
                escape = False
                name =''.join(name_chars)
                if name not in vars: vars[name] = None
                name_chars = []
            else:
                name_chars.append(char)
        prev=char
    return vars

# https://stackoverflow.com/questions/10112244/convert-plain-text-to-pdf-in-python
def text_to_pdf(text, filename):
    text = text.encode('latin-1', 'replace').decode('latin-1')
    a4_width_mm = 210
    pt_to_mm = 0.35
    fontsize_pt = 10
    fontsize_mm = fontsize_pt * pt_to_mm
    margin_bottom_mm = 10
    character_width_mm = 7 * pt_to_mm
    width_text = a4_width_mm / character_width_mm

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    pdf.add_page()
    pdf.set_font(family='Arial', size=fontsize_pt)
    splitted = text.split('\n')

    for line in splitted:
        lines = textwrap.wrap(line, width_text)

        if len(lines) == 0:
            pdf.ln()

        for wrap in lines:
            pdf.cell(0, fontsize_mm, wrap, ln=1)

    pdf.output(filename, 'F')

def run():
    parser = create_cli_parser()
    args = parser.parse_args()

    if not args.name and not args.path and not args.add and not args.delete:
        print("Must specify either a mongoDB document name or a filepath to a template")
        sys.exit(1)

    if args.add or args.name or args.delete:
        client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=1000)
        db = client['cover-letter-cli']['templates']

    if args.delete:
        db.delete_one({'name': args.delete})
        sys.exit(0)

    template = None

    if args.add:
        template = get_template_from_file(args.add)
        try:
            docs = db.count_documents({})
        except errors.ServerSelectionTimeoutError:
            print("Timed out waiting for db connection. Please make sure mongo is running on 27017.")
            sys.exit(1)
        
        prompt_name = True
        while prompt_name:
            default_name = "template_"+str(docs+1)
            name = input('Name of template: (default: '+default_name+') ')
            if not name: name = default_name

            exists = docs = db.count_documents({'name':name})
            if exists:
                print("There is already a template with that name in the database. Please choose another.")
            else:
                db.insert_one({'name': name, 'template': template})
                prompt_name=False

        cont = None
        while cont != 'y' and cont != 'n':
            cont = input("Generate a cover letter from this template? (Y/n) ")
            cont = cont.lower()
        if cont == 'n': sys.exit(0)

        cont = None
        while cont != 'y' and cont != 'n':
            cont = input("Export a pdf? (Y/n) ")
            cont = cont.lower()
        if cont == 'y': args.pdf = True
    
    if not template:
        if args.name:
            doc = db.find_one({'name':args.name})
            if not doc:
                print("Could not find template with that name.")
                sys.exit(0)
            template = doc["template"]
        elif args.path:
            template = get_template_from_file(args.path)

    vars = parse_variables(template)
    
    for var in vars:
        content = input("Text for " + var + ": ")
        # This is not particularly performant given all the copying, but its easy and this is quick tool.
        template = template.replace("${"+var+"}", content)
    
    if args.pdf:
        default_filename = args.name if args.name else name
        filename = input('Enter pdf filename: (default: '+default_filename+') ')
        if not filename: 
            date_suffix = datetime.now().strftime("_%m_%d_%Y")
            filename = default_filename+date_suffix
        text_to_pdf(template, filename+".pdf")
        print("PDF Saved.")
    
    try:
        pyperclip.copy(template)
    except Exception:
        print("Could not save content to clipboard. If you're on Linux, you'll need to install xcel or xclip.")
    print("Content saved to clipboard.")


if __name__ == "__main__":
    run()
