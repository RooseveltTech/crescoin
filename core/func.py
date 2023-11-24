import os
from string import Template
import requests
from django.conf import settings

def send_email(recipient: str, subject: str, template_dir: str, use_template=True, body=None, **substitute):
    if use_template:
        TEMPLATE_DIR = os.path.join("templates", f"{template_dir}")
        html_temp = os.path.abspath(TEMPLATE_DIR)

        with open(html_temp) as temp_file:
            template = temp_file.read()

        template = Template(template).safe_substitute(substitute)
    else:
        template = None
    try:
        requests.post(
            f"{settings.MAILGUN_URL}",
            auth=("api", f"{settings.MAILGUN_APIKEY}"),
            data={
                "from": "CRESCOIN <mailgun@sandbox82073125eae342f5b3684ac2bce8afb7.mailgun.org>",
                "to": f"<{recipient}>",
                "subject": f"{subject}",
                "html": f"""{template}""" if use_template else None,
                "text": body if not use_template else None
            },
        )

        return "EMAIL SENT"
    except Exception as e:
        print("failed to send email", e)
        return "EMAIL FAILED"