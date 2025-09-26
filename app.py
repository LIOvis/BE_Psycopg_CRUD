from flask import Flask, jsonify, request

import psycopg2
import os

database_name = os.environ.get("DATABASE_NAME")
app_host = os.environ.get("APP_HOST")
app_port = os.environ.get("APP_PORT")

conn = psycopg2.connect(f"dbname={database_name}")
cursor = conn.cursor()

def create_all():
    print("Creating tables...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Companies (
        company_id SERIAL PRIMARY KEY,
        company_name VARCHAR NOT NULL UNIQUE,
        active BOOLEAN DEFAULT true
        );

        CREATE TABLE IF NOT EXISTS Products (
        product_id SERIAL PRIMARY KEY,
        product_name VARCHAR NOT NULL UNIQUE,
        company_id INTEGER,
        description VARCHAR,
        price DECIMAL,
        active BOOLEAN DEFAULT true,
        FOREIGN KEY (company_id) REFERENCES Companies(company_id)
        );

        CREATE TABLE IF NOT EXISTS Categories (
        category_id SERIAL PRIMARY KEY,
        category_name VARCHAR NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS ProductsCategoriesXref (
        product_id INTEGER,
        category_id INTEGER,
        PRIMARY KEY (product_id, category_id),
        FOREIGN KEY (product_id) REFERENCES Products(product_id),
        FOREIGN KEY (category_id) REFERENCES Categories(category_id)
        );

        CREATE TABLE IF NOT EXISTS Warranties (
        warranty_id SERIAL PRIMARY KEY,
        warranty_months INTEGER NOT NULL,
        product_id INTEGER,
        FOREIGN KEY (product_id) REFERENCES Products(product_id)
        );
    """)
    conn.commit()
    print("Tables Created!")

app = Flask(__name__)

# CREATE

@app.route('/company', methods=['POST'])
def add_company():
    post_data = request.form if request.form else request.get_json()
    
    company_name = post_data.get('company_name')

    if not company_name:
        return jsonify({"message": "company_name is a required field"}), 400
    
    result = cursor.execute("""
        SELECT * FROM Companies
            WHERE company_name=%s;
        """,
        (company_name,)
    )

    result = cursor.fetchone()

    if result:
        return jsonify({"message": "Company already exists"}), 400
    
    try:
        cursor.execute("""
            INSERT INTO Companies
            (company_name)
            VALUES (%s);""",
        (company_name,)
        )
        conn.commit()
      
    except Exception as e:
        cursor.rollback()
        return jsonify({"message": "Company could not be added", "Error": str(e)}), 400

    return jsonify({"message": f"Company {company_name} added to DB"}), 201

@app.route('/category', methods=['POST'])
def add_category():
    post_data = request.form if request.form else request.get_json()
    
    category_name = post_data.get('category_name')

    if not category_name:
        return jsonify({"message": "category_name is a required field"}), 400
    
    result = cursor.execute("""
        SELECT * FROM Categories
            WHERE category_name=%s;
        """,
        (category_name,)
    )

    result = cursor.fetchone()

    if result:
        return jsonify({"message": "Category already exists"}), 400
    
    try:
        cursor.execute("""
            INSERT INTO Categories
            (category_name)
            VALUES (%s);""",
        (category_name,)
        )
        conn.commit()
      
    except Exception as e:
        cursor.rollback()
        return jsonify({"message": "Category could not be added", "Error": str(e)}), 400

    return jsonify({"message": f"Category {category_name} added to DB"}), 201

@app.route('/product', methods=['POST'])
def add_product():
    post_data = request.form if request.form else request.get_json()

    product_name = post_data.get('product_name')
    company_id = post_data.get('company_id')
    description = post_data.get('description')
    price = post_data.get('price')

    if not product_name:
        return jsonify({"message": "product_name is a required field"}), 400
    
    if not company_id:
        return jsonify({"message": "company_id is a required field"}), 400
    
    result = cursor.execute("""
        SELECT * FROM Products
            WHERE product_name=%s;
        """,
        (product_name,)
    )

    result = cursor.fetchone()

    if result:
        return jsonify({"message": "Product already exists"}), 400
    
    try:
        cursor.execute("""
            INSERT INTO Products
            (product_name, company_id, description, price)
            VALUES (%s, %s, %s, %s);
            """,
            (product_name, company_id, description, price,)
        )
        conn.commit()
      
    except Exception as e:
        cursor.rollback()
        return jsonify({"message": "Product could not be added", "Error": str(e)}), 400

    return jsonify({"message": f"Product {product_name} added to DB"}), 201

@app.route('/warranty', methods=['POST'])
def add_warranty():
    post_data = request.form if request.form else request.get_json()

    warranty_months = post_data.get('warranty_months')
    product_id = post_data.get('product_id')

    if not warranty_months:
        return jsonify({"message": "warranty_months is a required field"}), 400
    
    if not product_id:
        return jsonify({"message": "product_id is a required field"}), 400
    
    result = cursor.execute("""
        SELECT * FROM Warranties
        WHERE warranty_months = %s
        AND product_id = %s;
        """, 
        (warranty_months, product_id,)
    )

    if result:
        return jsonify({"message": "Warranty already exists"}), 400
    
    try:
        cursor.execute("""
            INSERT INTO Warranties
            (product_id, warranty_months)
            VALUES (%s, %s);
            """,
            (product_id, warranty_months,)
        )
        conn.commit()

    except Exception as e:
        cursor.rollback()
        return jsonify({"message": "Warranty could not be added", "Error": str(e)}), 400
    
    return jsonify({"message": f"Warranty added to DB"}), 201

@app.route('/product/category', methods=['POST'])
def create_xref():
    post_data = request.form if request.form else request.get_json()

    category_id = post_data.get('category_id')
    product_id = post_data.get('product_id')

    if not category_id:
        return jsonify({"message": "category_id is a required field"}), 400
    
    if not product_id:
        return jsonify({"message": "product_id is a required field"}), 400
    
    result = cursor.execute("""
        SELECT * FROM ProductsCategoriesXref
        WHERE category_id = %s
        AND product_id = %s;
        """, 
        (category_id, product_id,)
    )

    if result:
        return jsonify({"message": "Product-Category association already exists"}), 400
    
    try:
        cursor.execute("""
            INSERT INTO ProductsCategoriesXref
            (product_id, category_id)
            VALUES (%s, %s);
            """,
            (product_id, category_id,)
        )
        conn.commit()

    except Exception as e:
        cursor.rollback()
        return jsonify({"message": "Product-Category association could not be added", "Error": str(e)}), 400
    
    return jsonify({"message": f"Product-Category association added to DB"}), 201

# READ

@app.route('/companies', methods=['GET'])
def get_companies():
    result = cursor.execute("""
        SELECT * FROM Companies;
    """)
    
    result = cursor.fetchall()

    record_list = []

    for record in result:
        record = {
            'company_id': record[0],
            'company_name': record[1],
            'active': record[2]
        }
        
        record_list.append(record)

    if record_list == []:
        return jsonify({"message": "companies not found"}), 404
    else:
        return jsonify({"message": "companies found", "results": record_list}), 200
    
@app.route('/company/<company_id>', methods=['GET'])
def get_company_by_id(company_id):
    result = cursor.execute("""
        SELECT * FROM Companies
        WHERE company_id = %s;
    """, (company_id,))
    
    result = cursor.fetchone()
        
    if result == None:
        return jsonify({"message": "company not found"}), 404
    else:

        record = {
            'company_id': result[0],
            'company_name': result[1],
            'active': result[2]
        }
        return jsonify({"message": "company found", "result": record}), 200
    
@app.route('/categories', methods=['GET'])
def get_categories():
    result = cursor.execute("""
        SELECT * FROM Categories;
    """)
    
    result = cursor.fetchall()

    record_list = []

    for record in result:
        record = {
            'category_id': record[0],
            'category_name': record[1]
        }
        
        record_list.append(record)

    if record_list == []:
        return jsonify({"message": "categories not found"}), 404
    else:
        return jsonify({"message": "categories found", "results": record_list}), 200
    
@app.route('/category/<category_id>', methods=['GET'])
def get_category_by_id(category_id):
    result = cursor.execute("""
        SELECT * FROM Categories
        WHERE category_id = %s;
    """, (category_id,))
    
    result = cursor.fetchone()
  
    if result == None:
        return jsonify({"message": "category not found"}), 404
    else:
        record = {
            'category_id': result[0],
            'category_name': result[1]
        }

        return jsonify({"message": "category found", "result": record}), 200
    
@app.route('/products', methods=['GET'])
def get_products():
    result = cursor.execute("""
        SELECT * FROM Products;
    """)
    
    result = cursor.fetchall()

    record_list = []

    for record in result:
        record = {
            'product_id': record[0],
            'product_name': record[1],
            'company_id': record[2],
            'description': record[3],
            'price': record[4],
            'active': record[5]
        }
        
        record_list.append(record)

    if record_list == []:
        return jsonify({"message": "products not found"}), 404
    else:
        return jsonify({"message": "products found", "results": record_list}), 200
    
@app.route('/products/active', methods=['GET'])
def get_products_by_active():
    post_data = request.form if request.form else request.get_json()

    active = post_data.get('active')

    result = cursor.execute("""
        SELECT * FROM Products
        WHERE active = %s;
    """, (bool(active),))
    
    result = cursor.fetchall()

    record_list = []

    for record in result:
        record = {
            'product_id': record[0],
            'product_name': record[1],
            'company_id': record[2],
            'description': record[3],
            'price': record[4],
            'active': record[5]
        }
        
        record_list.append(record)

    if record_list == []:
        return jsonify({"message": "products not found"}), 404
    else:
        return jsonify({"message": "products found", "results": record_list}), 200
    
@app.route('/product/company/<company_id>', methods=['GET'])
def get_products_by_company_id(company_id):

    result = cursor.execute("""
        SELECT * FROM Products
        WHERE company_id = %s;
    """, (company_id,))
    
    result = cursor.fetchall()

    record_list = []

    for record in result:
        record = {
            'product_id': record[0],
            'product_name': record[1],
            'company_id': record[2],
            'description': record[3],
            'price': record[4],
            'active': record[5]
        }
        
        record_list.append(record)

    if record_list == []:
        return jsonify({"message": "products not found"}), 404
    else:
        return jsonify({"message": "products found", "results": record_list}), 200
    
@app.route('/product/<product_id>', methods=['GET'])
def get_product_by_id(product_id):

    result = cursor.execute("""
        SELECT * FROM Products
        WHERE product_id = %s;
    """, (product_id,))
    
    result = cursor.fetchone()

    if result == None:
        return jsonify({"message": "product not found"}), 404
    else:

        record = {
            "product_id": result[0],
            "product_name": result[1],
            "company_id": result[2],
            "description": result[3],
            "price": result[4],
            "active": result[5]
        }
        return jsonify({"message": "product found", "result": record}), 200
    
@app.route('/warranty/<warranty_id>', methods=['GET'])
def get_warranty_by_id(warranty_id):

    result = cursor.execute("""
        SELECT * FROM Warranties
        WHERE warranty_id = %s;
    """, (warranty_id,))
    
    result = cursor.fetchone()

    if result == None:
        return jsonify({"message": "product not found"}), 404
    else:

        record = {
            "warranty_id": result[0],
            "warranty_months": result[1],
            "product_id": result[2]
        }
        return jsonify({"message": "product found", "result": record}), 200
    
# UPDATE

@app.route('/company/<company_id>', methods=['PUT'])
def update_company_by_id(company_id):
    post_data = request.form if request.form else request.get_json()

    result = cursor.execute("""
        SELECT * FROM Companies
        WHERE company_id = %s;
        """, (company_id,)
    )

    result = cursor.fetchone()

    if result == None:
        return jsonify({"message": "company not found"}), 404
    
    allowed_fields = ["company_name", "active"]

    fields_to_update = {
        "company_name": post_data.get('company_name'),
        "active": post_data.get('active')
    }

    set_list = []
    set_value_tuple = ()

    for field in allowed_fields:
        if fields_to_update[field] != None and fields_to_update[field] != '' and str(fields_to_update[field]).isspace() != True:
            set_list.append(f"{field} = %s")
            set_value_tuple += (fields_to_update[field],)

    if set_list == []:
        return jsonify({"message": "nothing to update"}), 400
    else:
        set_str = ', '.join(set_list)
        set_value_tuple += (company_id,)
        
    try:
        cursor.execute(f"""        
            UPDATE Companies
            SET {set_str}
            WHERE company_id = %s;
            """, set_value_tuple
        )
        conn.commit()

    except Exception as e:
        cursor.rollback()
        return jsonify({"message": "Company could not be updated", "Error": str(e)}), 400
    
    result = cursor.execute("""
        SELECT * FROM Companies
        WHERE company_id = %s
        """, (company_id,)
    )
    
    result = cursor.fetchone()

    record = {
        "company_id": result[0],
        "company_name": result[1],
        "active": result[2]
    }

    return jsonify({"message": "company updated", "result": record}), 200


@app.route('/category/<category_id>', methods=['PUT'])
def update_category_by_id(category_id):
    post_data = request.form if request.form else request.get_json()

    result = cursor.execute("""
        SELECT * FROM Categories
        WHERE category_id = %s;
        """, (category_id,)
    )

    result = cursor.fetchone()

    if result == None:
        return jsonify({"message": "category not found"}), 404
    
    allowed_fields = ["category_name"]

    fields_to_update = {
        "category_name": post_data.get('category_name'),
    }

    set_list = []
    set_value_tuple = ()

    for field in allowed_fields:
        if fields_to_update[field] != None and fields_to_update[field] != '' and str(fields_to_update[field]).isspace() != True:
            set_list.append(f"{field} = %s")
            set_value_tuple += (fields_to_update[field],)

    if set_list == []:
        return jsonify({"message": "nothing to update"}), 400
    else:
        set_str = ', '.join(set_list)
        set_value_tuple += (category_id,)
        
    try:
        cursor.execute(f"""        
            UPDATE Categories
            SET {set_str}
            WHERE category_id = %s;
            """, set_value_tuple
        )
        conn.commit()

    except Exception as e:
        cursor.rollback()
        return jsonify({"message": "Category could not be updated", "Error": str(e)}), 400
    
    result = cursor.execute("""
        SELECT * FROM Categories
        WHERE category_id = %s
        """, (category_id,)
    )
    
    result = cursor.fetchone()

    record = {
        "category_id": result[0],
        "category_name": result[1],
    }

    return jsonify({"message": "company updated", "result": record}), 200

@app.route('/product/<product_id>', methods=['PUT'])
def update_product_by_id(product_id):
    post_data = request.form if request.form else request.get_json()

    result = cursor.execute("""
        SELECT * FROM Products
        WHERE product_id = %s;
        """, (product_id,)
    )

    result = cursor.fetchone()

    if result == None:
        return jsonify({"message": "product not found"}), 404

    allowed_fields = ["product_name", "company_id", "description", "price", "active"]

    fields_to_update = {
        "product_name": post_data.get('product_name'),
        "company_id": post_data.get('company_id'),
        "description": post_data.get('description'),
        "price": post_data.get('price'),
        "active": post_data.get('active')
    }

    set_list = []
    set_value_tuple = ()

    for field in allowed_fields:
        if fields_to_update[field] != None and fields_to_update[field] != '' and str(fields_to_update[field]).isspace() != True:
            set_list.append(f"{field} = %s")
            set_value_tuple += (fields_to_update[field],)

    if set_list == []:
        return jsonify({"message": "nothing to update"}), 400
    else:
        set_str = ', '.join(set_list)
        set_value_tuple += (product_id,)
        
    try:
        cursor.execute(f"""        
            UPDATE Products
            SET {set_str}
            WHERE product_id = %s;
            """, set_value_tuple
        )
        conn.commit()

    except Exception as e:
        cursor.rollback()
        return jsonify({"message": "Product could not be updated", "Error": str(e)}), 400
    
    result = cursor.execute("""
        SELECT * FROM Products
        WHERE product_id = %s
        """, (product_id,)
    )
    
    result = cursor.fetchone()

    record = {
        "product_id": result[0],
        "product_name": result[1],
        "company_id": result[2],
        "description": result[3],
        "price": result[4],
        "active": result[5]
    }

    return jsonify({"message": "product updated", "result": record}), 200






@app.route('/warranty/<warranty_id>', methods=['PUT'])
def update_warranty_by_id(warranty_id):
    post_data = request.form if request.form else request.get_json()

    result = cursor.execute("""
        SELECT * FROM Warranties
        WHERE warranty_id = %s;
        """, (warranty_id,)
    )

    result = cursor.fetchone()

    if result == None:
        return jsonify({"message": "warranty not found"}), 404

    allowed_fields = ["warranty_months", "product_id"]

    fields_to_update = {
        "warranty_months": post_data.get('warranty_months'),
        "product_id": post_data.get('product_id')
    }

    set_list = []
    set_value_tuple = ()

    for field in allowed_fields:
        if fields_to_update[field] != None and fields_to_update[field] != '' and str(fields_to_update[field]).isspace() != True:
            set_list.append(f"{field} = %s")
            set_value_tuple += (fields_to_update[field],)

    if set_list == []:
        return jsonify({"message": "nothing to update"}), 400
    else:
        set_str = ', '.join(set_list)
        set_value_tuple += (warranty_id,)
        
    try:
        cursor.execute(f"""        
            UPDATE Warranties
            SET {set_str}
            WHERE warranty_id = %s;
            """, set_value_tuple
        )
        conn.commit()

    except Exception as e:
        cursor.rollback()
        return jsonify({"message": "Warranty could not be updated", "Error": str(e)}), 400
    
    result = cursor.execute("""
        SELECT * FROM Warranties
        WHERE warranty_id = %s
        """, (warranty_id,)
    )
    
    result = cursor.fetchone()

    record = {
        "warranty_months": result[0],
        "product_id": result[1]
    }

    return jsonify({"message": "warranty updated", "result": record}), 200


# DELETE



if __name__ == '__main__':
    create_all()
    app.run(host=app_host, port=app_port)