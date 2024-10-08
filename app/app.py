from flask import Flask, request
from flask_restx import Api, Resource, fields  
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
api = Api(app, version='1.0', title='Gender CRUD API',
          description='A simple CRUD API for managing gender')

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

gender_model = api.model('Gender', {
    'Id': fields.Integer(readOnly=True, description='The gender unique identifier'),
    'Name': fields.String(required=True, description='The gender name'),
    'isActive': fields.Boolean(required=True, description='Is the gender active'),
})

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

@api.route('/genders')
class GenderList(Resource):
    @api.doc('list_genders')
    @api.marshal_list_with(gender_model)
    def get(self):
        """List all genders"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM gender Where isActive = %s',(True,))
        genders = cursor.fetchall()
        conn.close()
        return genders

    @api.doc('create_gender')
    @api.expect(gender_model)
    @api.marshal_with(gender_model, code=201)
    def post(self):
        """Create a new gender"""
        new_gender = request.json
        name = new_gender['Name']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO gender (name,isActive) VALUES (%s, %s)', (name,True))
        conn.commit()
        new_gender['id'] = cursor.lastrowid
        conn.close()
        return new_gender, 201

@api.route('/genders/<int:id>')
@api.response(404, 'Gender not found')
class Gender(Resource):
    @api.doc('get_gender')
    @api.marshal_with(gender_model)
    def get(self, id):
        """Fetch a gender given its identifier"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM gender WHERE id = %s', (id,))
        gender = cursor.fetchone()
        conn.close()
        if gender is None:
            api.abort(404)
        return gender

    @api.doc('update_gender')
    @api.expect(gender_model)
    @api.marshal_with(gender_model)
    def put(self, id):
        """Update a gender given its identifier"""
        conn = get_db_connection()
        cursor = conn.cursor()
        updated_gender = request.json
        cursor.execute('UPDATE gender SET Name = %s, isActive = %s WHERE id = %s',
                       (updated_gender['Name'], updated_gender['isActive'], id))
        conn.commit()
        conn.close()
        updated_gender['id'] = id
        return updated_gender

    @api.doc('delete_gender')
    @api.response(204, 'Gender deleted')
    def delete(self, id):
        """Delete a gender given its identifier"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE gender SET isActive = %s WHERE id = %s',
               (False, id))
        conn.commit()
        conn.close()
        return '', 204

if __name__ == "__main__":
    app.run(debug=True)
