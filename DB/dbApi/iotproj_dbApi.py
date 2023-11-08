import cherrypy
import psycopg2
import os
from psycopg2.extras import Json

# PostgreSQL database configuration
db_config = {
    'dbname': 'proj-p4iot',
    'user': 'postgres',
    'password': '8A%gcW@@p0h6',
    'host': 'adlab.m2madgenera.com',
    'port': '54321',
}


class dbAPI(object):

    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def index(self):
        """
        Method used to test the correct communication with internet. In production this should not be visible
        """
        return 'All working de dio!'

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    def add_user(self):
        # Get JSON data from the request
        user_data = cherrypy.request.json

        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_config)

        try:
            # Create a cursor
            cur = conn.cursor()

            # Retrieve the index of the user role
            cur.execute("""SELECT id FROM roles WHERE name = %s""",
                        (user_data['role'],))

            # Fetch the index of the user role
            role_index = cur.fetchone()[0]

            # Retrieve the index of the medic role
            cur.execute("""SELECT id FROM roles WHERE name = 'medic'""")

            # Medic role
            medic_role = cur.fetchone()[0]

            # Insert the new user into the user table
            cur.execute("""
                INSERT INTO users (name, surname, role, thingspeak_channel, cf, passkey) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            """, (user_data['name'], user_data['surname'], role_index, user_data['thingspeak_channel'], user_data['cf'], user_data['passkey']))

            id_of_new_row = cur.fetchone()[0]

            if user_data['medic_cf'] != '':
                # It is a patient, so:
                # Retrieve the index of the medic related to the new patient from medic cf
                cur.execute("""SELECT id FROM users WHERE cf = %s and role = %s""",
                            (user_data['medic_cf'], medic_role,))
                id_medic = cur.fetchone()[0]

                # Insert the related medic of the newly inserted user
                cur.execute("""
                    INSERT INTO patient_medic_relation (patient, medic) VALUES (%s, %s)""", (id_of_new_row, id_medic))

                # insert an empty list of caregivers for the patient
                cur.execute("""
                    INSERT INTO caregivers (patient_id, caregivers) VALUES (%s, %s)""", (id_of_new_row, Json({"phone": []})))

            # Commit the transaction
            conn.commit()
        except psycopg2.Error as e:
            # Handle any database errors
            cherrypy.response.status = 500
            return {'error': str(e)}
        finally:
            # Close the cursor and database connection
            cur.close()
            conn.close()

        # Return a success message
        return {'data': f'User {user_data["name"]} {user_data["surname"]} added successfully'}

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['PUT'])
    def upd_passkey(self):
        # Get JSON data from the request
        user_data = cherrypy.request.json

        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_config)

        try:
            # Create a cursor
            cur = conn.cursor()

            # Write the new passkey
            cur.execute("""UPDATE users SET users.passkey = %s FROM roles WHERE roles.id = users.roles_id and cf = %s and roles.name = 'patient'""",
                        (user_data['passkey'], user_data['cf'],))

            # Fetch the index of the user role
            role_index = cur.fetchone()[0]

            # Commit the transaction
            conn.commit()
        except psycopg2.Error as e:
            # Handle any database errors
            cherrypy.response.status = 500
            return {'error': str(e)}
        finally:
            # Close the cursor and database connection
            cur.close()
            conn.close()

        # Return a success message
        return {'data': f'Passwd for {user_data["name"]} {user_data["surname"]} changed successfully'}

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['PUT'])
    def upd_caregivers(self):
        # Get JSON data from the request
        user_data = cherrypy.request.json

        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_config)

        try:
            # Create a cursor
            cur = conn.cursor()

            # Retrieve the index of the patient role
            cur.execute("""SELECT id FROM roles WHERE name = 'patient'""")
            role_idx = cur.fetchone()[0]

            # Retrieve the index of the patient given his cf
            cur.execute("""SELECT id FROM users WHERE cf = %s and role = %s""",
                        (user_data['cf'], role_idx))
            patient_idx = cur.fetchone()[0]

            # Write the new caregivers
            caregivers = dict()
            caregivers['phone'] = user_data['numbers']
            cur.execute("""UPDATE caregivers SET caregivers = %s WHERE caregivers.patient_id = %s""", (Json(
                caregivers), patient_idx,))

            # Commit the transaction
            conn.commit()
        except psycopg2.Error as e:
            # Handle any database errors
            cherrypy.response.status = 500
            return {'error': str(e)}
        finally:
            # Close the cursor and database connection
            cur.close()
            conn.close()

        # Return a success message
        return {'data': f'Caregivers for {user_data["cf"]} changed successfully'}

    # Retrieve all users in a json format
    @cherrypy.tools.json_out()
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def get_users(self):
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_config)

        try:
            # Create a cursor
            cur = conn.cursor()

            # Retrieve all users
            cur.execute("""
                SELECT users.id, users.name, users.surname, roles.name AS role, users.thingspeak_channel, users.cf
                FROM users
                INNER JOIN roles ON users.role = roles.id
            """)

            # Fetch all users
            users = cur.fetchall()
        except psycopg2.Error as e:
            # Handle any database errors
            cherrypy.response.status = 500
            return {'error': str(e)}
        finally:
            # Close the cursor and database connection
            cur.close()
            conn.close()

        # Return all users
        return {'data': users}

    # Retrieve the thingspeak channel of a user
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def get_thingspeak_channel(self, cf, pwd):

        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_config)

        try:
            # Create a cursor
            cur = conn.cursor()

            # Retrieve the thingspeak channel of the user
            cur.execute("""
                SELECT users.thingspeak_channel FROM users
                INNER JOIN roles ON users.role = roles.id
                WHERE users.cf = %s AND users.passkey = %s AND roles.name = 'patient'
            """, (cf, pwd))

            # Fetch the thingspeak channel of the user
            thingspeak_channel = cur.fetchone()[0]
        except psycopg2.Error as e:
            # Handle any database errors
            cherrypy.response.status = 500
            return {'error': str(e)}
        finally:
            # Close the cursor and database connection
            cur.close()
            conn.close()

        # Return the thingspeak channel of the user
        return {'data': thingspeak_channel}

    # Retrieve the thingspeak channel of all the patients
    @cherrypy.tools.json_out()
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def get_all_thingspeak_channel(self):

        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_config)

        try:
            # Create a cursor
            cur = conn.cursor()

            # Retrieve the thingspeak channel of all the patients
            cur.execute("""
                SELECT users.id, users.thingspeak_channel, users.passkey FROM users
                INNER JOIN roles ON users.role = roles.id
                WHERE roles.name = 'patient'
            """)

            # Fetch the thingspeak channel of all the patients
            thingspeak_channel_list = cur.fetchall()
        except psycopg2.Error as e:
            # Handle any database errors
            cherrypy.response.status = 500
            return {'error': str(e)}
        finally:
            # Close the cursor and database connection
            cur.close()
            conn.close()

        # Return the thingspeak channel of all the patients
        return {'data': thingspeak_channel_list}

    # Retrieve the caregiver numbers of a patient
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    def get_caregivers(self, id):

        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_config)

        try:
            # Create a cursor
            cur = conn.cursor()

            # Retrieve the thingspeak channel of the user
            cur.execute("""
                SELECT users.name, users.surname, caregivers.caregivers
                FROM users
                INNER JOIN caregivers on caregivers.patient_id = users.id
                WHERE users.id = %s
            """, (id))

            # Fetch row of the user
            row = cur.fetchone()
            caregivers = {
                "name": row[0], "surname": row[1], "phones": row[2]["phone"]}
        except psycopg2.Error as e:
            # Handle any database errors
            cherrypy.response.status = 500
            return {'error': str(e)}
        finally:
            # Close the cursor and database connection
            cur.close()
            conn.close()

        # Return the caregivers of the user
        return {'data': caregivers}


if __name__ == '__main__':
    # Configure CherryPy
    conf = {'/': {'tools.sessions.on': True,
                  'tools.staticdir.root': os.path.abspath(os.getcwd())}}
    # Configure CherryPy to serve the API on a specific port
    cherrypy.config.update({'server.socket_host': '0.0.0.0',
                            'server.socket_port': 4367})

    # Mount the dbAPI as the root endpoint
    cherrypy.tree.mount(dbAPI(), '/p4iot/api', conf)

    # Start CherryPy web server
    cherrypy.engine.start()
    cherrypy.engine.block()
