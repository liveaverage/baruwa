import email
from email.Header import decode_header

def parse_attachment(part):
  attachment = ""
  content_disposition = part.get("Content-Disposition", None)
  if content_disposition:
    dispositions = content_disposition.strip().split(";")
    if bool(content_disposition and dispositions[0].lower() == "attachment"):
      for param in dispositions[1:]:
        name,value = param.split("=")
        if name.lstrip() == "filename":
          attachment = value
      return attachment
  return None

def get_header(header_text, default="ascii"):
  headers = decode_header(header_text)
  header_sections = [unicode(text, charset or default) for text, charset in headers]
  return u"".join(header_sections)

def parse_email(msg):
  attachments = []
  body = None
  html = None
  has_html = False

  for part in msg.walk():
    attach = parse_attachment(part)
    if attach:
      attachments.append(attach)
    elif part.get_content_type() == "text/plain":
      if body is None:
        body = ""
      body += unicode(part.get_payload(decode=True),part.get_content_charset(),'replace').encode('utf8','replace')
    elif part.get_content_type() == "text/html":
      has_html = True
      if html is None:
        html = ""
      html += unicode(part.get_payload(decode=True),part.get_content_charset(),'replace').encode('utf8','replace')
  return {
      'subject' : get_header(msg.get('Subject')),
      'to' : get_header(msg.get('To')),
      'from' : get_header(msg.get('From')),
      'date' : get_header(msg.get('Date')),
      'has_html' : has_html,
      'body' : body,
      'html' : html,
      'attachments' : attachments,
  }

def get_message_path(qdir,date,message_id):
  import os
  qdirs = ["spam","nonspam","mcp"]
  for message_kind in qdirs:
    file_path = "%s/%s/%s/%s" % (qdir,date,message_kind,message_id)
    if os.path.exists(file_path):
      return file_path
  file_path = "%s/%s/%s/message" % (qdir, date, message_id)
  if os.path.exists(file_path):
    return file_path
  else:
    return None

def release_mail(mail_path, to_addr, from_addr):
  import smtplib,os
  msg = ""
  if os.path.exists(mail_path):
    file = open(mail_path)
    for line in file:
      msg = msg + line
    try:
      server = smtplib.SMTP('smtp01.sentechsa.net')
    except:
      return False
    try:
      server.sendmail(from_addr, to_addr, msg)
    except:
      server.quit()
      return False
    server.quit()
  else:
    return False
  return True

def sa_learn(mail_path, learn_as):
  import os
  from subprocess import Popen, PIPE
  SA_LEARN = '/usr/bin/sa-learn --%s --file %s' % (learn_as, mail_path)
  LEARN_OPTS = ('spam','ham','forget')

  if not learn_as in LEARN_OPTS:
    return {'success':False,'output':'','errormsg':'Incorrect learn option'}
  if os.path.exists(mail_path):
    p = Popen(SA_LEARN, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    if p.returncode == 0:
      return {'success':True,'output':stdout,'errormsg':''}
    else:
      return {'success':False,'output':stdout,'errormsg':stderr}
  else:
    return {'success':False,'output':'','errormsg':'mail file could not be read'}

