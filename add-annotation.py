import argparse
import os
import re

def has_annotation(filepath):
    # Open the file in read mode and check if one of the lines starts with the language annotation ('@Lang VBA or '@Lang("VBA") or '@Lang: VBA)
    with open(filepath, "r") as file:
        for i, line in enumerate(file):
            if i >= 50:
                break
            #TODO: include case where ' is followed by spaces
            if line.lower().startswith("'@lang") or line.lower().startswith("rem @lang"):
                return True
    return False

def get_line_ending(filepath):
    try:
        with open(filepath, 'rb') as file:
            content = file.read()
        
        # Initialize variables to track line endings
        lf_count = 0
        crlf_count = 0
        cr_count = 0
        mixed_ending = False
        
        i = 0
        while i < len(content):
            if content[i] == 0x0A:  # LF
                if i > 0 and content[i-1] == 0x0D:  # Check for CR before LF (CRLF)
                    crlf_count += 1
                else:
                    lf_count += 1
            elif content[i] == 0x0D:  # CR
                # Check if this is the last character or if the next is not LF (standalone CR)
                if i == len(content) - 1 or content[i+1] != 0x0A:
                    cr_count += 1
            i += 1
        
        # Determine the line ending type
        if (lf_count > 0 and crlf_count > 0) or (lf_count > 0 and cr_count > 0) or (crlf_count > 0 and cr_count > 0):
            mixed_ending = True
        
        if mixed_ending:
            raise ValueError("The file has mixed line endings.")
        elif crlf_count > 0:
            return "\\r\\n"
        elif lf_count > 0:
            return "\\n"
        elif cr_count > 0:
            return "\\r"
        else:
            raise ValueError("The file does not contain any recognizable line endings.")
    
    except Exception as e:
        raise e

def add_annotation(filepath, language):

    if language.lower().startswith("basic "):
        raise ValueError("Annotation for Classic BASIC isn't supported at the moment.")

    print(f"🟡 {filepath} is missing the {language} Language Annotation")
    eol = get_line_ending(filepath)
    # Convert escape sequences in eol to their respective characters
    eol = re.sub(r'\\n', '\n', eol)
    eol = re.sub(r'\\r', '\r', eol)
    with open(filepath, "r") as file:
        lines = file.readlines()
    inserted = False
    firstNonEmptyEncountered = False
    with open(filepath, "w", newline='') as file:
        for line in lines:
            # We skip empty lines and lines that start with "Attribute " since these are metadata for VB Classic and VBA.
            if line.startswith("Attribute ") and not firstNonEmptyEncountered:
                firstNonEmptyEncountered = True
                file.write(f"{line}")
            elif line.startswith("Attribute "):
                file.write(f"{line}")
            elif line.strip() == '' and not firstNonEmptyEncountered:
                file.write(f"{line}")
            elif line.strip() == '' and not inserted:
                file.write(f"'@Lang {language}{eol}")
                file.write(f"{line}")
                inserted = True
            elif not inserted:
                file.write(f"'@Lang {language}{eol}")
                file.write(f"{line}")
                inserted = True
            else:
                file.write(f"{line}")
    print(f"    🟢 {filepath} now has the {language} Language Annotation")

def main(language):
    repo_dir = "/home/runner/work/"
    files = [] 
    for root, _, filenames in os.walk(repo_dir):
        for filename in filenames:
            if filename.lower().endswith(".bas"):
                filepath = os.path.join(root, filename)
                files.append(filepath)

                annotation_result = has_annotation(filepath)
                if not annotation_result:
                    add_annotation(filepath, language)
                else:
                    print(f"🟢 {filepath} already has the {language} Langugage annotation.")

    if not files:
        print("No files with the specified extensions found in the repository.")
    else:
        print(f"Found {len(files)} file(s) with the specified extensions.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Add BASIC language annotation.")
    parser.add_argument('language', type=str, help='Name of the language in the BASIC family')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    main(args.language)
