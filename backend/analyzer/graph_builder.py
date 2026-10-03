import json


# Read project data
with open("backend/analyzer/project_data.json", "r") as file:
    project_data = json.load(file)


nodes = []
relationships = []

classes = set()
functions = set()
methods = set()


# ==========================================
# FIRST PASS - CREATE NODES
# ==========================================

for file_data in project_data:

    file_name = file_data["file"]

    # File node
    nodes.append({
        "type": "File",
        "name": file_name
    })

    # Class nodes
    for class_name in file_data["classes"]:

        classes.add(class_name)

        nodes.append({
            "type": "Class",
            "name": class_name,
            "file": file_name
        })

        relationships.append({
            "from": file_name,
            "relationship": "CONTAINS",
            "to": class_name
        })


    # Function nodes
    for function_name in file_data["functions"]:

        functions.add(function_name)

        # Don't create duplicate method nodes here
        is_method = False

        for method in file_data["methods"]:

            if method["method"] == function_name:
                is_method = True
                break

        if not is_method:

            nodes.append({
                "type": "Function",
                "name": function_name,
                "file": file_name
            })

            relationships.append({
                "from": file_name,
                "relationship": "CONTAINS",
                "to": function_name
            })


    # Method nodes
    for method in file_data["methods"]:

        class_name = method["class"]
        method_name = method["method"]

        full_method_name = class_name + "." + method_name

        methods.add(full_method_name)

        nodes.append({
            "type": "Method",
            "name": full_method_name,
            "file": file_name
        })

        relationships.append({
            "from": class_name,
            "relationship": "CONTAINS",
            "to": full_method_name
        })


# ==========================================
# SECOND PASS - IMPORTS, CALLS, DEPENDENCIES
# ==========================================

for file_data in project_data:

    file_name = file_data["file"]


    # --------------------------------------
    # IMPORTS
    # --------------------------------------

    for imported in file_data["imports"]:

        parts = imported.split()

        if len(parts) >= 4:

            imported_name = parts[-1]

            if imported_name in classes:

                relationships.append({
                    "from": file_name,
                    "relationship": "IMPORTS",
                    "to": imported_name
                })


    # --------------------------------------
    # CALLS
    # --------------------------------------

    for call in file_data["calls"]:

        caller = call["caller"]
        callee = call["callee"]

        if caller is None:
            continue


        # Class call
        if callee in classes:

            relationships.append({
                "from": caller,
                "relationship": "CALLS",
                "to": callee
            })

            continue


        # Object.method call
        if "." in callee:

            method_name = callee.split(".")[-1]

            matching_method = None

            for method in methods:

                if method.endswith("." + method_name):

                    matching_method = method
                    break

            if matching_method:

                relationships.append({
                    "from": caller,
                    "relationship": "CALLS",
                    "to": matching_method
                })

            continue


        # Normal function call
        if callee in functions:

            relationships.append({
                "from": caller,
                "relationship": "CALLS",
                "to": callee
            })


    # --------------------------------------
    # DEPENDENCIES
    # --------------------------------------

    for dependency in file_data["dependencies"]:

        relationships.append({
            "from": file_name,
            "relationship": "DEPENDS_ON",
            "to": dependency
        })


# ==========================================
# PRINT NODES
# ==========================================

print("\n========== NODES ==========\n")

for node in nodes:

    print(
        node["type"],
        "->",
        node["name"]
    )


# ==========================================
# PRINT RELATIONSHIPS
# ==========================================

print("\n========== RELATIONSHIPS ==========\n")

for relationship in relationships:

    print(
        relationship["from"],
        "--",
        relationship["relationship"],
        "-->",
        relationship["to"]
    )