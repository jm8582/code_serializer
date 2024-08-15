import os
import json5
import argparse


def is_file_allowed(file_name, allowed_files, excluded_files, allowed_extensions, excluded_extensions):
    if allowed_files and file_name in allowed_files:
        return True
    if excluded_files and file_name in excluded_files:
        return False

    _, ext = os.path.splitext(file_name)
    ext = ext.lstrip(".")

    if allowed_extensions and ext in allowed_extensions:
        return True
    if excluded_extensions and ext in excluded_extensions:
        return False

    return not (allowed_files or allowed_extensions)


def serialize_project(project_path, allowed_files, excluded_files, allowed_extensions, excluded_extensions):
    project_data = {}
    file_list = []

    for root, _, files in os.walk(project_path):
        for file in files:
            if is_file_allowed(file, allowed_files, excluded_files, allowed_extensions, excluded_extensions):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_path)
                normalized_path = relative_path.replace(os.sep, ".")
                file_list.append(normalized_path)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    if file.endswith(".json5"):
                        try:
                            content = json5.loads(content)
                            content = json5.dumps(content, indent=2)  # Convert back to string
                        except json5.decoder.Json5DecodeError:
                            print(f"Warning: Unable to parse JSON5 file: {relative_path}")

                    project_data[normalized_path] = content
                except Exception as e:
                    print(f"Error processing file {relative_path}: {str(e)}")

    return file_list, project_data


def format_output(file_list, project_data):
    output = "Directory structure:\n"
    for file in sorted(file_list):
        output += f"{file}\n"

    output += "\nFile contents:\n"
    for file in sorted(file_list):
        output += f"\n{file}\n"
        output += project_data[file] + "\n"

    return output


def main():
    parser = argparse.ArgumentParser(description="Serialize project files")
    parser.add_argument("--project_path", default=".")
    parser.add_argument("--allowed-files", nargs="*", default=[])
    parser.add_argument("--excluded-files", nargs="*", default=[])
    parser.add_argument("--allowed-extensions", nargs="*", default=["py", "json", "txt"])
    parser.add_argument("--excluded-extensions", nargs="*", default=[])
    parser.add_argument("--output", default="serialized_project.txt")

    args = parser.parse_args()

    file_list, project_data = serialize_project(
        args.project_path,
        set(args.allowed_files),
        set(args.excluded_files),
        set(args.allowed_extensions),
        set(args.excluded_extensions),
    )

    formatted_output = format_output(file_list, project_data)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(formatted_output)

    print(f"Project serialized and saved to {args.output}")


if __name__ == "__main__":
    main()
