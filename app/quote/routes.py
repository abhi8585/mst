# from flask_mail import Message
# from app.quote import blueprint
# from flask import render_template, request, jsonify
# from app.models import quote
# from .. import db
# from app.services.mail import MailService
# from app.services.S3 import FileUploadService
# from flask import current_app as app
# import tempfile,datetime
# @blueprint.route('/')
# def list():
#     quotes = quote.query.all()
#     return render_template('quote_list.html', quotes=quotes)

# @blueprint.route('/add/<quote_id>')
# @blueprint.route('/add/new')
# def create(quote_id=0):
#     quote_id = int(quote_id)
#     if quote_id>0:
#         quotes = quote.query.filter_by(id=quote_id).first()
#         return render_template('quote.html', quotes=quotes)
#     if request.args.get('usr_mail'):
#         user_mail=request.args.get('usr_mail')
#         return render_template('quote.html', user_mail=user_mail)
#     return render_template('quote.html')

# @blueprint.route("/docs-upload")
# def image_gallery():
#     return render_template('docs.html')

# def save_to_db(request):
#     quote_id=request.form.get('id',0)
#     quote_title=request.form.get('title','')
#     quote_review=request.form.get('review','')
#     quote_email=request.form.get('email','')
#     quote_attachments=request.form.get('attachment','')
#     quote_status=request.form.get('status','Draft')
#     quote_message=request.form.get('message','')
#     try:
#         quote_id = int(quote_id)
#         if quote_id>0:
#             quote_obj = quote.query.filter_by(id=quote_id).first()
#             quote_obj.title = quote_title
#             quote_obj.review = quote_review
#             quote_obj.email = quote_email
#             quote_obj.attachment = quote_attachments
#             quote_obj.status = quote_status
#             quote_obj.message = quote_message
#         else:
#             quote_obj = quote(title=quote_title, review=quote_review, email=quote_email, attachment=quote_attachments, status=quote_status, message=quote_message)
#             db.session.add(quote_obj)
#         db.session.commit()
#         print(quote_obj)
#         return  1
#     except Exception as e:
#         print(e)
#         return e



# @blueprint.route('/save', methods=['POST'])
# def add():
#     resp=save_to_db(request)
#     if resp==1:
#         return jsonify({'status':'success', 'message':'Quote saved successfully'}), 200
#     else:
#         return jsonify({'status':'failed', 'message':'Quote not saved'}), 400


# @blueprint.route('/delete/<quote_id>')
# def delete(quote_id):
#     quote_id = int(quote_id)
#     if quote_id>0:
#         quote_obj = quote.query.filter_by(id=quote_id).first()
#         db.session.delete(quote_obj)
#         db.session.commit()
#         return jsonify(status='success', message='Quote Deleted')
#     return jsonify(status='error', message='Quote Not Found'), 404

# @blueprint.route('/send', methods=['POST'])
# def send():
#     resp=save_to_db(request)
#     if resp!=1:
#         return jsonify({'status':'error', 'message':'Quote not saved'}), 400
#     if request.form.get('email') is None or request.form.get('email')=='':
#         return jsonify(status='error', message='Email is required'), 400
#     quote_obj = quote.query.filter_by(email=request.form.get('email')).first()
#     quote_obj.status = 'Sent'
#     quote_obj.last_sent=datetime.datetime.now()
#     db.session.commit()
#     try:
#         mail = MailService()
#         file = FileUploadService()
#         subject = quote_obj.title
#         html = "<html> <body> <h1> A Quote From Date Planner </h1> <p> " + quote_obj.message + " </p> </body> </html>" #needs to be changed
#         attach=None
#         print("attachment is here ",quote_obj.attachment)
#         if quote_obj.attachment:
#             print("Picking up attachment")
#             path=file.download(quote_obj.attachment.split('/')[-1],'dp-docs')
#             attach=path
#         mail.send_mail(subject,quote_obj.email,quote_obj.review,attach,html)
#         return jsonify(status='success', message='Quote Sent'), 200
#     except Exception as e:
#         print(e)
#         return jsonify(status='error', message=str(e)), 500
                   



