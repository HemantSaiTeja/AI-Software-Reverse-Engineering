from tree_sitter import Language, Parser
import tree_sitter_python
import os
import json


PY_LANGUAGE = Language(tree_sitter_python.language())

parser = Parser(PY_LANGUAGE)


def parse_file(file_path):

    with open(file_path, "r") as file:
        source_code = file.read()

    tree = parser.parse(bytes(source_code, "utf8"))

    return tree, source_code


def extract_information(
    node,
    source_code,
    current_function=None,
    current_class=None
):

    imports = []
    functions = []
    classes = []
    calls = []
    methods = []

    # --------------------------------
    # IMPORT
    # --------------------------------

    if node.type == "import_statement":

        imports.append(
            source_code[node.start_byte:node.end_byte]
        )

    elif node.type == "import_from_statement":

        imports.append(
            source_code[node.start_byte:node.end_byte]
        )

    # --------------------------------
    # CLASS
    # --------------------------------

    elif node.type == "class_definition":

        name_node = node.child_by_field_name("name")

        if name_node:

            class_name = source_code[
                name_node.start_byte:name_node.end_byte
            ]

            classes.append(class_name)

            current_class = class_name

    # --------------------------------
    # FUNCTION
    # --------------------------------

    elif node.type == "function_definition":

        name_node = node.child_by_field_name("name")

        if name_node:

            function_name = source_code[
                name_node.start_byte:name_node.end_byte
            ]

            functions.append(function_name)

            if current_class:

                methods.append({
                    "class": current_class,
                    "method": function_name
                })

            current_function = function_name

    # --------------------------------
    # CALL
    # --------------------------------

    elif node.type == "call":

        function_node = node.child_by_field_name("function")

        if function_node:

            call_name = source_code[
                function_node.start_byte:function_node.end_byte
            ]

            calls.append({
                "caller": current_function,
                "callee": call_name
            })

    # --------------------------------
    # CHILDREN
    # --------------------------------

    for child in node.children:

        child_imports, child_functions, child_classes, \
        child_calls, child_methods = extract_information(
            child,
            source_code,
            current_function,
            current_class
        )

        imports.extend(child_imports)
        functions.extend(child_functions)
        classes.extend(child_classes)
        calls.extend(child_calls)
        methods.extend(child_methods)

    return imports, functions, classes, calls, methods


def analyze_project(project_path):

    project_data = []

    for root, directories, files in os.walk(project_path):

        for file in files:

            if file.endswith(".py"):

                file_path = os.path.join(root, file)

                tree, source_code = parse_file(file_path)

                imports, functions, classes, calls, methods = \
                    extract_information(
                        tree.root_node,
                        source_code
                    )

                data = {
                    "file": file_path,
                    "imports": imports,
                    "classes": classes,
                    "functions": functions,
                    "methods": methods,
                    "calls": calls,
                    "dependencies": []
                }

                project_data.append(data)

    return project_data


def find_dependencies(project_data):

    for file_data in project_data:

        for imported in file_data["imports"]:

            if imported.startswith("from"):

                parts = imported.split()

                if len(parts) >= 2:

                    module_name = parts[1]

                    target_file = os.path.join(
                        "sample_project",
                        module_name + ".py"
                    )

                    if os.path.exists(target_file):

                        file_data["dependencies"].append(
                            target_file
                        )


project_data = analyze_project("sample_project")

find_dependencies(project_data)


with open(
    "backend/analyzer/project_data.json",
    "w"
) as file:

    json.dump(
        project_data,
        file,
        indent=4
    )


print("\nProject analysis completed.")

print("\nJSON file created:")
print("backend/analyzer/project_data.json")