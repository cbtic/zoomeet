import jwt
import requests
import json
import frappe
from time import time


# send a request with headers including
# a token and meeting details


def createMeeting(doc, method):
    # Enter your API key and your API secret
    API_KEY = 'PrEmPojgTpCIixHbvhn2jQ'
    API_SEC = 'eqitAoW8C3t9baM53UqBqcBZpnYbYMaCinSy'

    # create a function to generate a token
    # using the pyjwt library

    def generateToken():
        token = jwt.encode(

            # Create a payload of the token containing
            # API Key & expiration time
            {'iss': API_KEY, 'exp': time() + 5000},

            # Secret used to generate token signature
            API_SEC,

            # Specify the hashing alg
            algorithm='HS256'
        )
        return token.decode('utf-8')

    def recipients():
        if doc.patient_email:
            return doc.patient_uid
        elif doc.patient_uid:
            return doc.patient_email
        else:
            return False
    def old_schedule():
        doc.old_prac = doc.practitioner
        doc.date_old = doc.appointment_date
        doc.time_old = doc.appointment_time

    def details():
        return {"topic": f"TELECONSULTA del {doc.practitioner_name} {doc.department}",
                "type": 2,
                "start_time": f"{doc.appointment_date}T{doc.appointment_time}",
                "duration": f"{doc.duration}",
                "timezone": "Europe/Madrid",
                "agenda": "test",
                "recurrence": {"type": 1,
                               "repeat_interval": 1
                               },
                "settings": {"host_video": "true",
                             "participant_video": "true",
                             "join_before_host": "False",
                             "mute_upon_entry": "False",
                             "watermark": "true",
                             "audio": "voip",
                             "auto_recording": "cloud",
                             "contact_email": "aarrimac@cbmedic.com",
                             "contact_name": "Alfredo Rimac",
                             "email_notification": "true"
                             }
                }

    def zoom_det():
        return f"""URL de reunión: {join_url}
                    <br><br>
                    Contraseña de reunión: {password}
                    <br><br>
                    Tema: {topic}
                    <br><br>
                    ID de reunión: {meeting_id}
                    <br><br>
                    Hora: {doc.appointment_date} --> {doc.appointment_time}
                    <hr>
                    <a href="{join_url}" target="_blank" style="padding:7px 15px; background:cyan; border-radius:5px; margin-top:15px;"> Inicar reunión </a>
                    """

    # create json data for post requests
    if not doc.z_link:
        if doc.patient and doc.practitioner and doc.department and doc.appointment_date and doc.appointment_time and doc.duration:
            if recipients() is False:
                frappe.throw("Email de paciente")
            meetingdetails = details()

            headers = {'authorization': 'Bearer ' + generateToken(),
                       'content-type': 'application/json'}

            r = requests.post(
                f'https://api.zoom.us/v2/users/me/meetings',
                headers=headers, data=json.dumps(meetingdetails))

            y = json.loads(r.text)
            join_url = y["join_url"]
            password = y["password"]
            topic = y["topic"]
            meeting_id = y["id"]

            doc.meeting_id = meeting_id
            doc.z_link = zoom_det()

            new_patient_encounter = frappe.new_doc("Patient Encounter")
            new_patient_encounter.patient = doc.patient
            new_patient_encounter.patient_name = doc.patient_name
            new_patient_encounter.patient_sex = doc.patient_sex
            new_patient_encounter.patient_age = doc.patient_age
            new_patient_encounter.practitioner = doc.practitioner
            new_patient_encounter.encounter_date = doc.appointment_date
            new_patient_encounter.encounter_time = doc.appointment_time
            new_patient_encounter.appointment = doc.name
            new_patient_encounter.zoom_meeting_info = doc.z_link


            new_patient_encounter.insert()

            subject = f"{doc.company}: cita del paciente {doc.patient_name}"
            message = doc.z_link
            frappe.sendmail(recipients=recipients(), subject=subject, message=message)

            old_schedule()
            frappe.msgprint("Email enviado")
            return frappe.msgprint("Reunión de Zoom se ha publicado con éxito")

    else:
        if doc.practitioner != doc.old_prac or doc.appointment_date != doc.date_old or doc.appointment_time != doc.time_old:
            meeting_details = details()

            headers = {
                'authorization': 'Bearer ' + generateToken(),
                'content-type': 'application/json'
            }

            requests.patch(
                f"https://api.zoom.us/v2/meetings/{doc.meeting_id}",
                headers=headers,
                data=json.dumps(meeting_details)
            )

            doc.z_link = doc.z_link.replace(f"{doc.date_old}", f"{doc.appointment_date}").replace(f"{doc.time_old}",
                                                                                             f"{doc.appointment_time}")

            new_patient_encounter = frappe.get_doc("Patient Encounter", {'title': doc.title})
            new_patient_encounter.patient = doc.patient
            new_patient_encounter.patient_name = doc.patient_name
            new_patient_encounter.patient_sex = doc.patient_sex
            new_patient_encounter.patient_age = doc.patient_age
            new_patient_encounter.practitioner = doc.practitioner
            new_patient_encounter.encounter_date = doc.appointment_date
            new_patient_encounter.encounter_time = doc.appointment_time
            new_patient_encounter.appointment = doc.name
            new_patient_encounter.zoom_meeting_info = doc.z_link

            new_patient_encounter.save()

            subject = f"{doc.company}: cita del paciente {doc.patient_name}"
            message = "<h2>Cita modificado</h2><br><br>" + doc.z_link
            frappe.sendmail(recipients=recipients(), subject=subject, message=message)

            old_schedule()
            frappe.msgprint("Email enviado")
            return frappe.msgprint("Reunión de Zoom se ha modificado con éxito")


def deleteMeeting(doc, method):
    # Enter your API key and your API secret
    API_KEY = 'PrEmPojgTpCIixHbvhn2jQ'
    API_SEC = 'eqitAoW8C3t9baM53UqBqcBZpnYbYMaCinSy'

    # create a function to generate a token
    # using the pyjwt library

    def generateToken():
        token = jwt.encode(

            # Create a payload of the token containing
            # API Key & expiration time
            {'iss': API_KEY, 'exp': time() + 5000},

            # Secret used to generate token signature
            API_SEC,

            # Specify the hashing alg
            algorithm='HS256'
        )
        return token.decode('utf-8')

    def recipients():
        if doc.patient_email:
            return doc.patient_uid
        elif doc.patient_uid:
            return doc.patient_email
        else:
            return False

    headers = {
        'authorization': 'Bearer ' + generateToken(),
        'content-type': 'application/json'
    }

    r = requests.delete(
        f'https://api.zoom.us/v2/meetings/{doc.meeting_id}',
        headers=headers
    )
    doc.z_link = f"""<h2>Cita cancelada</h2>
                    <br><br>
                    Tema: f"TELECONSULTA del {doc.practitioner_name} {doc.department}
                    <br><br>
                    ID de reunión: {doc.meeting_id}
                    <br><br>
                    Hora: {doc.appointment_date} --> {doc.appointment_time}
                    <hr> """
    frappe.get_doc("Patient Encounter", {'title': doc.title}).delete()
    subject = f"{doc.company}: cita del paciente {doc.patient_name}"
    message = doc.z_link
    frappe.sendmail(recipients=recipients(), subject=subject, message=message)

    frappe.msgprint("Email enviado")
    return frappe.msgprint("La cita ha sido cancelada con exito")
