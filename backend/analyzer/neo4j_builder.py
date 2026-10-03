import json
from neo4j import GraphDatabase


URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "12345678"


driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


# Read project data
with open("backend/analyzer/project_data.json", "r") as file:
    project_data = json.load(file)


def create_graph(tx, data):

    # -----------------------------
    # FILE
    # -----------------------------

    tx.run(
        """
        MERGE (f:File {name: $file})
        """,
        file=data["file"]
    )


    # -----------------------------
    # CLASSES
    # -----------------------------

    for class_name in data["classes"]:

        tx.run(
            """
            MERGE (c:Class {name: $class_name})
            """,
            class_name=class_name
        )

        tx.run(
            """
            MATCH (f:File {name: $file})
            MATCH (c:Class {name: $class_name})
            MERGE (f)-[:CONTAINS]->(c)
            """,
            file=data["file"],
            class_name=class_name
        )


    # -----------------------------
    # FUNCTIONS
    # -----------------------------

    for function in data["functions"]:

        tx.run(
            """
            MERGE (fn:Function {name: $function})
            """,
            function=function
        )

        tx.run(
            """
            MATCH (f:File {name: $file})
            MATCH (fn:Function {name: $function})
            MERGE (f)-[:CONTAINS]->(fn)
            """,
            file=data["file"],
            function=function
        )


    # -----------------------------
    # METHODS
    # -----------------------------

    for method in data["methods"]:

        class_name = method["class"]
        method_name = method["method"]

        full_method_name = class_name + "." + method_name

        tx.run(
            """
            MERGE (m:Method {name: $method})
            """,
            method=full_method_name
        )

        tx.run(
            """
            MATCH (c:Class {name: $class_name})
            MATCH (m:Method {name: $method})
            MERGE (c)-[:CONTAINS]->(m)
            """,
            class_name=class_name,
            method=full_method_name
        )


    # -----------------------------
    # IMPORTS
    # -----------------------------

    for imported in data["imports"]:

        parts = imported.split()

        if len(parts) >= 4:

            imported_class = parts[-1]

            tx.run(
                """
                MATCH (f:File {name: $file})
                MATCH (c:Class {name: $class_name})
                MERGE (f)-[:IMPORTS]->(c)
                """,
                file=data["file"],
                class_name=imported_class
            )


    # -----------------------------
    # DEPENDENCIES
    # -----------------------------

    for dependency in data["dependencies"]:

        tx.run(
            """
            MATCH (f1:File {name: $file})
            MATCH (f2:File {name: $dependency})
            MERGE (f1)-[:DEPENDS_ON]->(f2)
            """,
            file=data["file"],
            dependency=dependency
        )


    # -----------------------------
    # FUNCTION / METHOD CALLS
    # -----------------------------

    for call in data["calls"]:

        caller = call["caller"]
        callee = call["callee"]

        # Ignore calls outside a function/method
        if caller is None:
            continue


        # --------------------------------
        # CALL TO A CLASS
        # Example:
        # main -> PaymentService
        # --------------------------------

        class_result = tx.run(
            """
            MATCH (c:Class {name: $callee})
            RETURN c
            """,
            callee=callee
        )

        if class_result.single():

            # Caller can be a Function or Method
            caller_result = tx.run(
                """
                MATCH (n)
                WHERE (n:Function OR n:Method)
                AND (
                    n.name = $caller
                    OR n.name ENDS WITH $method_suffix
                )
                RETURN n
                LIMIT 1
                """,
                caller=caller,
                method_suffix="." + caller
            )

            caller_node = caller_result.single()

            if caller_node:

                tx.run(
                    """
                    MATCH (caller)
                    WHERE elementId(caller) = $caller_id

                    MATCH (callee:Class {name: $callee})

                    MERGE (caller)-[:CALLS]->(callee)
                    """,
                    caller_id=caller_node["n"].element_id,
                    callee=callee
                )

            continue


        # --------------------------------
        # CALL TO A METHOD
        # Example:
        # main -> PaymentService.make_payment
        # --------------------------------

        if "." in callee:

            method_name = callee.split(".")[-1]

            method_result = tx.run(
                """
                MATCH (m:Method)
                WHERE m.name ENDS WITH $method
                RETURN m
                LIMIT 1
                """,
                method="." + method_name
            )

            method_node = method_result.single()

            if method_node:

                caller_result = tx.run(
                    """
                    MATCH (n)
                    WHERE (n:Function OR n:Method)
                    AND (
                        n.name = $caller
                        OR n.name ENDS WITH $method_suffix
                    )
                    RETURN n
                    LIMIT 1
                    """,
                    caller=caller,
                    method_suffix="." + caller
                )

                caller_node = caller_result.single()

                if caller_node:

                    tx.run(
                        """
                        MATCH (caller)
                        WHERE elementId(caller) = $caller_id

                        MATCH (callee:Method)
                        WHERE elementId(callee) = $callee_id

                        MERGE (caller)-[:CALLS]->(callee)
                        """,
                        caller_id=caller_node["n"].element_id,
                        callee_id=method_node["m"].element_id
                    )


def main():

    with driver.session(database="neo4j") as session:

        for data in project_data:
            session.execute_write(create_graph, data)

    print("Graph updated successfully!")


main()

driver.close()