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

def has_attribute_vb_name(filepath):
    try:
        with open(filepath, "r") as file:
            lines = file.readlines()
            
            # Flag to indicate whether we've started processing attributes
            started_processing_attributes = False
            
            for line in lines:
                stripped_line = line.strip()
                
                if stripped_line != '':
                    # Check if the line starts with "Attributes "
                    if not started_processing_attributes:
                        if stripped_line.startswith("Attribute "):
                            started_processing_attributes = True
                            if "Attribute VB_Name" in stripped_line:
                                return True
                            # Otherwise continue to process attributes
                            continue
                        else:
                            # If the first non-empty line is not an "Attributes " line
                            return False
                        
                    # If we have started processing attributes, check for "Attribute VB_Name"
                    if started_processing_attributes:
                        if stripped_line.startswith("Attribute "):
                            if "Attribute VB_Name" in stripped_line:
                                return True
                        else:
                            # If we encounter a non-attribute line after starting attributes, stop searching
                            return False
            
            # If we finish the loop and haven't found "Attribute VB_Name"
            return False
    except IOError:
        # Handle file reading errors
        print(f"Error reading file: {filepath}")
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
            raise ValueError(f"The file {filepath} has mixed line endings. LF: {lf_count}; CRLF: {crlf_count}; CR: {cr_count} ")
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

def parse_language(language_str):
    # Dictionary to map lowercase language strings to their corresponding BASIC family languages
    language_map = {
        'basic': 'basic',
        'basica': 'basic',
        'qb': 'quickbasic',
        'qbasic': 'quickbasic',
        'quickbasic': 'quickbasic',
        'fb': 'freebasic',
        'freebasic': 'freebasic'
    }

    # Normalize input by stripping whitespace and converting to lowercase
    normalized_str = language_str.strip().lower()

    # Check for matches with the language_map
    for key in language_map:
        if re.match(rf'^{re.escape(key)}\b', normalized_str):
            return language_map[key]
    
    # Handle patterns for VBA versions (e.g., vba, vba7, vba10, etc.)
    if re.match(r'^vba\d*', normalized_str):
        return 'vba'
    
    # Handle patterns for VB versions (e.g., vb, vb1, vb2, etc.)
    if re.match(r'^(vb|visual basic )\d*', normalized_str):
        return 'vb6'
    
    # Handle patterns for QB versions (e.g., qb, qb1, etc.)
    if re.match(r'^qb\d*', normalized_str):
        return 'quickbasic'
    
    # Return a default value or raise an exception if the input is unknown
    return 'unknown'

def add_annotation(filepath, language):

    if language.lower().startswith("basic "):
        raise ValueError("Annotation for Classic BASIC isn't supported at the moment.")

    print(f"🟡 {filepath} is missing the {language} Language Annotation")
    eol = get_line_ending(filepath)
    # Convert escape sequences in eol to their respective characters
    eol = re.sub(r'\\n', '\n', eol)
    eol = re.sub(r'\\r', '\r', eol)
    with open(filepath, "r", newline='') as file:
        lines = file.readlines()
    inserted = False
    first_nonEmpty_encountered = False
    with open(filepath, "w", newline='') as file:
        for line in lines:
            # We skip empty lines and lines that start with "Attribute " since these are metadata for VB Classic and VBA.
            if line.startswith("Attribute ") and not first_nonEmpty_encountered:
                first_nonEmpty_encountered = True
                file.write(f"{line}")
            elif line.startswith("Attribute "):
                file.write(f"{line}")
            elif line.strip() == '' and not first_nonEmpty_encountered:
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

# This is a special addition for VBA/VB6 files.
def add_attribute(filepath):

    print(f"🟡 {filepath} is missing the Visual Basic Name Attribute")
    eol = get_line_ending(filepath)
    # Convert escape sequences in eol to their respective characters
    eol = re.sub(r'\\n', '\n', eol)
    eol = re.sub(r'\\r', '\r', eol)
    with open(filepath, "r", newline='') as file:
        lines = file.readlines()
    module_name = os.path.basename(filepath).rsplit('.bas', 1)[0]
    first_line = True
    syntax_error = False
    with open(filepath, "w", newline='') as file:
        for line in lines:
            # We skip empty lines and lines that start with "Attribute " since these are metadata for VB Classic and VBA.
            if first_line:
                if line.lower().startswith("version "):
                    syntax_error = True
                else:
                    file.write(f"Attribute VB_Name = \"{module_name}\"{eol}")
                file.write(f"{line}")
                first_line = False
            else:
                file.write(f"{line}")
    if syntax_error:
        print(f"    🔴 {filepath} has syntax that doesn't correspond to a module. Aborting the addition of the Name Attribute.")
        return False
    else:
        print(f"    🟢 {filepath} now has the Visual Basic Name Attribute")
        return True

def main(language):
    repo_dir = "/home/runner/work/"
    files = [] 
    parsed_lang = parse_language(language)
    for root, _, filenames in os.walk(repo_dir):
        for filename in filenames:
            if filename.lower().endswith(".bas"):
                filepath = os.path.join(root, filename)
                files.append(filepath)

                if parsed_lang == "vba" or parsed_lang == "vb6":
                    has_attribute = has_attribute_vb_name(filepath)
                    if not has_attribute:
                        if not add_attribute(filepath):
                            print("======================================")
                            continue

                annotation_result = has_annotation(filepath)
                if not annotation_result:
                    add_annotation(filepath, language)
                else:
                    print(f"🟢 {filepath} already has the {language} Langugage annotation.")

                print("======================================")

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
