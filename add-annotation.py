import os

def has_annotation(filepath):
    # Open the file in read mode and check if one of the lines starts with the VBA annotation ('@Lang VBA or '@Lang("VBA") or '@Lang: VBA)
    with open(filepath, "r") as file:
        for i, line in enumerate(file):
            if i >= 50:
                break
            if line.lower().startswith("@lang vba") or line.lower().startswith("@lang(\"vba\")") or line.lower().startswith("@lang: vba"):
                return True
    return False

def add_annotation(filepath):

    print(f"🟡 {filepath} is missing the VBA Language Annotation")
    # Open the file in write mode and write the VBA annotation after the last line that starts with "Attribute "
    with open(filepath, "r") as file:
        lines = file.readlines()
    insterted = False
    with open(filepath, "w") as file:
        for line in lines:
            if insterted == False and (line.startswith("Attribute ") or line == "\n"):
                file.write(f"{line}")
                file.write("'@Lang VBA\r\n")
                insterted = True
            else:
                file.write(f"{line}")
    print(f"    🟢 {filepath} now has the VBA Language Annotation")

def main():
    repo_dir = "/home/runner/work/"
    files = [] 
    for root, _, filenames in os.walk(repo_dir):
        for filename in filenames:
            if filename.endswith(".bas"):
                filepath = os.path.join(root, filename)
                files.append(filepath)

                annotation_result = has_annotation(filepath)
                if not annotation_result:
                    add_annotation(filepath)
                else:
                    print(f"🟢 {filepath} already has the VBA Langugage annotation.")

    if not files:
        print("No files with the specified extensions found in the repository.")
    else:
        print(f"Found {len(files)} file(s) with the specified extensions.")

if __name__ == "__main__":
    main()
