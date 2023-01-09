from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from openpyxl import load_workbook
import sqlite3
import pandas as pd
import uuid
from minio import Minio
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import update, desc
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from jose import JWTError, jwt
from functools import wraps
import json
import numpy as np

load_dotenv()

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://abhi:TEST123@localhost:5432/hiringapp2"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['SECRET_KEY']='something'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
from models import *

minioClient = Minio(
        "play.min.io",
        access_key="Q3AM3UQ867SPQQA43P2F",
        secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
    )
found = minioClient.bucket_exists("resume")
if not found:
    minioClient.make_bucket("resume")
else:
    print("Bucket 'resume' already exists")

#------------------Auth and roles access implementation--------------
def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = request.cookies.get('token') #for python and js compatibilty
		if token:
			try:
				#print(token.split()[1])
				data = jwt.decode(token.split()[1], app.config['SECRET_KEY'], 'HS256')
				current_user = Users.query\
					.filter_by(id = data['id'])\
					.first()
			except:
				return jsonify({
					'message' : 'Token is invalid !!'
				}), 401
		if not token:
			return jsonify({'message' : 'Token is missing !!'}), 401


		return f(current_user, *args, **kwargs)

	return decorated

def token_forwarder(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = request.cookies.get('token') #for python and js compatibilty
		if token:#'Authorization' in request.headers:
			#token = #request.headers['Authorization']
			try:
				data = jwt.decode(token, app.config['SECRET_KEY'], 'HS256')
				current_user = Users.query\
    				.filter_by(id = data['id'])\
    				.first()
			except:
				return jsonify({
    				'message' : 'Token is invalid !!'
    			}), 401
		if not token:
			current_user=None


		return f(current_user, *args, **kwargs)

	return decorated

def pmoOnly(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = request.cookies.get('token') #for python and js compatibilty
		if token:
			try:
				#print(token.split()[1])
				data = jwt.decode(token.split()[1], app.config['SECRET_KEY'], 'HS256')
				current_user = Users.query\
					.filter_by(id = data['id'])\
					.first()
				if(current_user.role != 'pmo'):
					return jsonify({
						'message' : 'Unauthorised access to role PMO !!'
					}), 401
					current_user=None
			except:
				return jsonify({
					'message' : 'Token is invalid !!'
				}), 401
		if not token:
			return jsonify({'message' : 'Token is missing !!'}), 401

		return f(current_user, *args, **kwargs)

	return decorated

def tacOnly(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = request.cookies.get('token') #for python and js compatibilty
		if token:
			try:
				#print(token.split()[1])
				data = jwt.decode(token.split()[1], app.config['SECRET_KEY'], 'HS256')
				current_user = Users.query\
					.filter_by(id = data['id'])\
					.first()
				if(current_user.role != 'tac'):
					return jsonify({
						'message' : 'Unauthorised access to role TAC team !!'
					}), 401
					current_user=None
			except:
				return jsonify({
					'message' : 'Token is invalid !!'
				}), 401
		if not token:
			return jsonify({'message' : 'Token is missing !!'}), 401


		return f(current_user, *args, **kwargs)

	return decorated

def interviewerOnly(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = request.cookies.get('token') #for python and js compatibilty
		if token:
			try:
				#print(token.split()[1])
				data = jwt.decode(token.split()[1], app.config['SECRET_KEY'], 'HS256')
				current_user = Users.query\
					.filter_by(id = data['id'])\
					.first()
				if(current_user.role != 'tac'):
					return jsonify({
						'message' : 'Unauthorised access to role Interviewer !!'
					}), 401
					current_user=None
			except:
				return jsonify({
					'message' : 'Token is invalid !!'
				}), 401
		if not token:
			return jsonify({'message' : 'Token is missing !!'}), 401


		return f(current_user, *args, **kwargs)

	return decorated

def hrOnly(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = request.cookies.get('token') #for python and js compatibilty
		if token:
			try:
				#print(token.split()[1])
				data = jwt.decode(token.split()[1], app.config['SECRET_KEY'], 'HS256')
				current_user = Users.query\
					.filter_by(id = data['id'])\
					.first()
				if(current_user.role != 'hr'):
					return jsonify({
						'message' : 'Unauthorised access to role HR team !!'
					}), 401
					current_user=None
			except:
				return jsonify({
					'message' : 'Token is invalid !!'
				}), 401
		if not token:
			return jsonify({'message' : 'Token is missing !!'}), 401


		return f(current_user, *args, **kwargs)

	return decorated

#example of pmo role specific routing
@app.route('/test', methods=['GET'])
@pmoOnly
def getPMO(current_user):
	if(current_user):
		return jsonify({'users': current_user.name})
	else:
		return jsonify({'users': None})


# an example of logged in admin route to access all data
@app.route('/users', methods =['GET'])
@token_required
def get_all_users(current_user):
	users = Users.query.all()
	output = []
	for user in users:
		output.append({
			'id': user.id,
			'name' : user.name,
			'email' : user.email,
			'role': user.role
		})

	return jsonify({'users': output})

@app.route('/loginToken', methods =['POST'])
def loginToken():
	auth = request.form
	print(auth.get('email'), auth.get('password'))
	if not auth or not auth.get('email') or not auth.get('password'):
		return make_response(
			'Could not verify',
			401,
			{'WWW-Authenticate' : 'Basic realm ="Login required !!"'}
		)

	user = Users.query\
		.filter_by(email = auth.get('email'))\
		.first()

	if not user:
		return make_response(
			'Could not verify',
			401,
			{'WWW-Authenticate' : 'Basic realm ="User does not exist !!"'}
		)

	if check_password_hash(user.password, auth.get('password')):
		token = jwt.encode({
			'id': user.id,
			'exp' : datetime.utcnow() + timedelta(minutes = 30)
		}, app.config['SECRET_KEY'], 'HS256')
	resp = make_response(redirect(url_for("main")))#make_response(jsonify({'token' : token, 'user':user.role}), 201)
	resp.set_cookie('token', token)
	return resp

	return make_response(
		'Could not verify',
		403,
		{'WWW-Authenticate' : 'Basic realm ="Wrong Password !!"'}
	)

@app.route('/createUser', methods =['POST'])
def createUser():
	data = request.form
	name, email, role = data.get('name'), data.get('email'), data.get('role')
	password = data.get('password')
	user = Users.query\
		.filter_by(email = email)\
		.first()
	if not user:
		user = Users(
			id = str(uuid.uuid4()),
			name = name,
			email = email,
			password = generate_password_hash(password),
			role = role
		)
		db.session.add(user)
		db.session.commit()

		return make_response('Successfully registered.', 201)
	else:
		return make_response('User already exists', 202)


#--------------------------------------------------------------------


def get_abstract_data():
    result = roles.query.order_by(desc(roles.modified_at)).all()
    nums = {}
    col={
        "green":1,
        "yellow":2,
        "red":3,
        "gray":4
    }
    for i in result:
        nums[i.tsin_id.strip()] = {
            "stage1": 0,
            "stage2": 0,
            "stage3": 0,
            "stage4": 0,
            "stage5": 0,
            "stage6": 0,
            "stage7": 0,
            "stage8": 0,
            "stage9": 0,
        }
    result2 = candidates.query.all()
    list_of_phone = []
    for i in result2:
        list_of_phone.append(i.phone)
    d = {}
    final_color={}
    list_of_tsin=[]
    for i in result:
        list_of_tsin.append(i.tsin_id.strip())
    for i in result2:
        if i.tsin_id.strip() in list_of_tsin:
            if i.status=="inactive":
                color="gray"
            else:
                if i.request_raised_date:
                    difference=datetime.now()-i.request_raised_date
                elif i.resume_screened_date:
                    difference=datetime.now()-i.resume_screened_date
                else:
                    difference=timedelta(days=0)# logical error heree if both cases are false difference is not made at all
                if i.current_stage.strip() == "Resume Screened for Interview":
                    nums[i.tsin_id.strip()]["stage1"] += 1
                    if difference.days<=8:
                        color="green"
                    elif difference.days>8 and difference.days<10:
                        color="yellow"
                    else:
                        color="red"
                elif i.current_stage.strip() == "L1 Interview Complete":
                    nums[i.tsin_id.strip()]["stage2"] += 1
                    if difference.days<=13:
                        color="green"
                    elif difference.days>13 and difference.days<15:
                        color="yellow"
                    else:
                        color="red"
                elif i.current_stage.strip() == "L2 Interview Complete":
                    nums[i.tsin_id.strip()]["stage3"] += 1
                    if difference.days<=16:
                        color="green"
                    elif difference.days>16 and difference.days<18:
                        color="yellow"
                    else:
                        color="red"
                elif i.current_stage.strip() == "L3 Interview Complete":
                    nums[i.tsin_id.strip()]["stage4"] += 1
                    if difference.days<=21:
                        color="green"
                    elif difference.days>21 and difference.days<23:
                        color="yellow"
                    else:
                        color="red"
                elif i.current_stage.strip() == "Offer RollOut":
                    nums[i.tsin_id.strip()]["stage5"] += 1
                    if difference.days<=23:
                        color="green"
                    elif difference.days>23 and difference.days<25:
                        color="yellow"
                    else:
                        color="red"
                elif i.current_stage.strip() == "Buddy Assignment":
                    nums[i.tsin_id.strip()]["stage6"] += 1
                    if difference.days<=25:
                        color="green"
                    elif difference.days>25 and difference.days<27:
                        color="yellow"
                    else:
                        color="red"
                elif (
                    i.current_stage.strip() == "Candidate Joined"
                    or i.current_stage.strip() == "Candidate Dropout"
                ):
                    nums[i.tsin_id.strip()]["stage7"] += 1
                    color="gray"
                elif i.current_stage.strip() == "Resume Rejected":
                    nums[i.tsin_id.strip()]["stage8"] += 1
                    color="gray"
                elif i.current_stage.strip() == "Profile Upload":
                    nums[i.tsin_id.strip()]["stage9"] += 1
                    if difference.days<=5:
                        color="green"
                    elif difference.days>5 and difference.days<5:
                        color="yellow"
                    else:
                        color="red"
            if i.tsin_id.strip() in d:
                d[i.tsin_id.strip()].append(
                    {
                        "id": i.id,
                        "candidate_name": i.candidate_name,
                        "pan": i.pan,
                        "candidate_email": i.candidate_email,
                        "current_stage": i.current_stage,
                        "request_raised_date": i.request_raised_date,
                        "tsin_opened_date": i.tsin_opened_date,
                        "resume_screened_date": i.resume_screened_date,
                        "l1_interview_date": i.l1_interview_date,
                        "l1_interviewer": i.l1_interviewer,
                        "l2_interview_date": i.l2_interview_date,
                        "l2_interviewer": i.l2_interviewer,
                        "l3_interview_date": i.l3_interview_date,
                        "l3_interviewer": i.l3_interviewer,
                        "offer_rollout_date": i.offer_rollout_date,
                        "joining_date": i.joining_date,
                        "buddy_assignment_date": i.buddy_assignment_date,
                        "buddy_name": i.buddy_name,
                        "candidate_dropout_date": i.candidate_dropout_date,
                        "candidate_dropout_reason": i.candidate_dropout_reason,
                        "resume": i.resume,
                        "phone": i.phone,
                        "current_location": i.current_location,
                        "current_company": i.current_company,
                        "experience": i.experience,
                        "status": i.status,
                        "color":color
                    }
                )
            else:
                d[i.tsin_id.strip()] = [
                    {
                        "id": i.id,
                        "candidate_name": i.candidate_name,
                        "pan": i.pan,
                        "candidate_email": i.candidate_email,
                        "current_stage": i.current_stage,
                        "request_raised_date": i.request_raised_date,
                        "tsin_opened_date": i.tsin_opened_date,
                        "resume_screened_date": i.resume_screened_date,
                        "l1_interview_date": i.l1_interview_date,
                        "l1_interviewer": i.l1_interviewer,
                        "l2_interview_date": i.l2_interview_date,
                        "l2_interviewer": i.l2_interviewer,
                        "l3_interview_date": i.l3_interview_date,
                        "l3_interviewer": i.l3_interviewer,
                        "offer_rollout_date": i.offer_rollout_date,
                        "joining_date": i.joining_date,
                        "buddy_assignment_date": i.buddy_assignment_date,
                        "buddy_name": i.buddy_name,
                        "candidate_dropout_date": i.candidate_dropout_date,
                        "candidate_dropout_reason": i.candidate_dropout_reason,
                        "resume": i.resume,
                        "phone": i.phone,
                        "current_location": i.current_location,
                        "current_company": i.current_company,
                        "experience": i.experience,
                        "status":i.status,
                        "color":color
                    }
                ]
        if i.tsin_id in final_color.keys():
            if col[final_color[i.tsin_id]]>col[color]:
                final_color[i.tsin_id]=color
        else:
            final_color[i.tsin_id]=color

    return result, d, nums, list_of_phone, final_color


def total_offers():
    result = candidates.query.with_entities(
        candidates.tsin_id,
        candidates.offer_rollout_date,
        candidates.candidate_dropout_date,
    ).all()

    final = {}
    dropout_final = {}
    for i in result:
        j = roles.query.with_entities(roles.role).filter_by(tsin_id=i.tsin_id).all()
        print(j)
        if i.offer_rollout_date != None:
            time = i.offer_rollout_date
            now = datetime.now()
            difference = now - time
            if j[0][0] in final.keys():
                print(".....", final[j[0][0]])
                final[j[0][0]].append(difference.days)
            else:
                final[j[0][0]] = [difference.days]
        if i.candidate_dropout_date != None:
            time = i.candidate_dropout_date
            now = datetime.now()
            difference = now - time
            if j[0][0] in dropout_final.keys():
                dropout_final[j[0][0]].append(difference.days)
            else:
                dropout_final[j[0][0]] = [difference.days]
    print(final)

    return final, dropout_final


def get_new_profiles():
    result = candidates.query.with_entities(
        candidates.tsin_id, candidates.created_at
    ).all()
    final = {}
    for i in result:
        j = roles.query.with_entities(roles.role).filter_by(tsin_id=i.tsin_id).all()
        print(j)
        now = datetime.now()
        difference = now - i.created_at
        print(j[0][0])
        if j[0][0] in final.keys():
            final[j[0][0]].append(difference.days)
        else:
            final[j[0][0]] = [difference.days]
    return final


def get_role_wise_profiles():
    result = candidates.query.with_entities(
        candidates.tsin_id, candidates.current_stage
    ).all()
    final = {}
    for i in result:
        j = roles.query.with_entities(roles.role).filter_by(tsin_id=i.tsin_id).all()
        if j[0][0] not in final.keys():
            final[j[0][0]] = [0, 0, 0, 0, 0, 0, 0, 0]
        if i.current_stage == "Profile Upload":
            final[j[0][0]][0] += 1
        elif i.current_stage == "Resume Screened for Interview":
            final[j[0][0]][1] += 1
        elif i.current_stage == "L1 Interview Complete":
            final[j[0][0]][2] += 1
        elif i.current_stage == "L2 Interview Complete":
            final[j[0][0]][3] += 1
        elif i.current_stage == "L3 Interview Complete":
            final[j[0][0]][4] += 1
        elif i.current_stage == "Offer RollOut":
            final[j[0][0]][5] += 1
        elif i.current_stage == "Buddy Assignment":
            final[j[0][0]][6] += 1
        elif (
            i.current_stage == "Candidate Joined"
            or i.current_stage == "Candidate Dropout"
        ):
            final[j[0][0]][7] += 1
    final2 = []
    for i in final:
        final3 = [i] + final[i]
        final2.append(final3)
    print(final2)

    return final2


def get_detailed_data():
    result = roles.query.all()
    result2 = candidates.query.all()
    roless = {}
    for i in result:
        roless[i.tsin_id.strip()] = {
            "role": i.role,
            "chapter": i.chapter,
            "squad": i.squad,
            "demand_type": i.demand_type,
            "tribe": i.tribe,
            "snow_id": i.snow_id,
        }
    d = []
    for i in result2:
        d.append(
            {
                "tsinid": i.tsin_id,
                "chapter": roless[i.tsin_id.strip()]["chapter"],
                "squad": roless[i.tsin_id.strip()]["squad"],
                "demand_type": roless[i.tsin_id.strip()]["demand_type"],
                "tribe": roless[i.tsin_id.strip()]["tribe"],
                "snow_id": roless[i.tsin_id.strip()]["snow_id"],
                "role": roless[i.tsin_id.strip()]["role"],
                "id": i.id,
                "candidate_name": i.candidate_name,
                "pan": i.pan,
                "candidate_email": i.candidate_email,
                "current_stage": i.current_stage,
                "request_raised_date": i.request_raised_date,
                "tsin_opened_date": i.tsin_opened_date,
                "resume_screened_date": i.resume_screened_date,
                "l1_interview_date": i.l1_interview_date,
                "l1_interviewer": i.l1_interviewer,
                "l2_interview_date": i.l2_interview_date,
                "l2_interviewer": i.l2_interviewer,
                "l3_interview_date": i.l3_interview_date,
                "l3_interviewer": i.l3_interviewer,
                "offer_rollout_date": i.offer_rollout_date,
                "joining_date": i.joining_date,
                "buddy_assignment_date": i.buddy_assignment_date,
                "buddy_name": i.buddy_name,
                "candidate_dropout_date": i.candidate_dropout_date,
                "candidate_dropout_reason": i.candidate_dropout_reason,
                "resume": i.resume,
                "phone": i.phone,
                "current_location": i.current_location,
                "current_company": i.current_company,
                "experience": i.experience,
            }
        )
    return d


@app.route("/")
@token_forwarder
def main(user):
    #print(user)
    result, d, nums, phones, colors= get_abstract_data()
    roless=role.query.all()
    chapters=chapter.query.all()
    squads=squad.query.all()
    tribes=tribe.query.all()
    print(colors)
    return render_template(
        "candidates.html", roles=result, candidates=d, nums=nums, phones=phones, final_colors=colors, roless=roless, squads=squads, tribes=tribes, chapters=chapters, user=role
    )


@app.route("/upload-dataset", methods=["GET", "POST"])
def uploadDs():
    f = request.files["file"]  # File input
    if not f:
        return "No file attached"

    global filename
    filename = f.filename  # changing global value of filename

    path = "{}/{}".format("static", filename)
    f.save(path)
    x = path.split(".")[-1]

    # reading filedata start
    if x == "xlsx":
        new_wb = load_workbook(path)
        Dataframe = pd.read_excel(new_wb, engine="openpyxl")
    elif x == "csv":
        Dataframe = pd.read_csv(path, encoding="ISO-8859-1")
    else:
        return "Please upload the file in xlsx or csv only"
    # reading filedata end

    dict_of_records = Dataframe.to_dict(orient="record")

    for i in dict_of_records:
        current_stage="Empty"
        candidate_dropout_date = str(i["Candidate Dropout"])
        candidate_joined_date = str(i["Candidate Joined"])
        if candidate_dropout_date == "nan" or candidate_dropout_date == "NaT":
            candidate_dropout_date = None
        else:
            current_stage = "Candidate Dropout"

        if candidate_joined_date == "nan" or candidate_joined_date == "NaT":
            candidate_joined_date = None
        else:
            if current_stage=="Empty":
                current_stage = "Candidate Joined"

        buddy_assignment_date = str(i["Buddy Assignment "])
        if buddy_assignment_date == "nan" or buddy_assignment_date == "NaT":
            buddy_assignment_date = None
        else:
            if current_stage=="Empty":
                current_stage = "Buddy Assignment"

        joining_date = str(i["Joining Date"])
        if joining_date == "nan" or joining_date == "NaT":
            joining_date = None
        else:
            if current_stage=="Empty":
                current_stage = "Offer RollOut"

        offer_rollout_date = str(i["Offer RollOut "])
        if offer_rollout_date == "nan" or offer_rollout_date == "NaT":
            offer_rollout_date = None
        else:
            if current_stage=="Empty":
                current_stage = "Offer RollOut"

        l3_interview_date = str(i["L3 Interview Complete"])
        if l3_interview_date == "nan" or l3_interview_date == "NaT":

            l3_interview_date = None
        else:
            if current_stage=="Empty":
                current_stage = "L3 Interview Complete"

        l2_interview_date = str(i["L2 Interview Complete"])
        if l2_interview_date == "nan" or l2_interview_date == "NaT":
            l2_interview_date = None
        else:
            if current_stage=="Empty":
                current_stage = "L2 Interview Complete"

        l1_interview_date = str(i["L1 Interview Complete"])
        if l1_interview_date == "nan" or l1_interview_date == "NaT":
            current_stage = "Resume Screened for Interview"
            l1_interview_date = None
        else:
            if current_stage=="Empty":
                current_stage = "L1 Interview Complete"

        resume_screened_date = str(i["Resume Screened"])
        if resume_screened_date == "nan" or resume_screened_date == "NaT":
            resume_screened_date = None
        else:
            if current_stage=="Empty":
                current_stage = "Profile Upload"

        tsin_opened_date = str(i["TSIN Opened"])
        if tsin_opened_date == "nan" or tsin_opened_date == "NaT":
            tsin_opened_date = None
        else:
            if current_stage=="Empty":
                current_stage = "Profile Upload"

        request_raised_date = str(i["Resume Shared"])
        if request_raised_date == "nan" or request_raised_date == "NaT":
            request_raised_date = None
        else:
            if current_stage=="Empty":
                current_stage = "Profile Upload"

        existing_roles = roles.query.filter_by(tsin_id=i["TSIN ID"].strip()).all()
        existing_emails = candidates.query.with_entities(
            candidates.candidate_email, candidates.tsin_id
        ).all()
        print(existing_emails)
        if len(existing_roles)==0:
            db.session.add(
                roles(
                    tsin_id=str(i["TSIN ID"].strip()),
                    role=str(i["Role "]),
                    chapter=str(i["Chapter"]),
                    squad=str(i["Squad"]),
                    demand_type=str(i["Type of Demand"]),
                    tribe=str(i["Tribe"]),
                    snow_id=str(i["Snow ID"]),
                    aspd_date=str(i["APSD Date"]),
                    status="active",
                    created_at=datetime.now(),
                    modified_at=datetime.now(),
                )
            )
            db.session.commit()
        else:
            existing_roles[0].tsin_id=str(i["TSIN ID"].strip())
            existing_roles[0].role=str(i["Role "])
            existing_roles[0].chapter=str(i["Chapter"])
            existing_roles[0].squad=str(i["Squad"])
            existing_roles[0].demand_type=str(i["Type of Demand"])
            existing_roles[0].tribe=str(i["Tribe"])
            existing_roles[0].snow_id=str(i["Snow ID"])
            existing_roles[0].aspd_date=str(i["APSD Date"])
            existing_roles[0].status="active"
            db.session.commit()
        z = [str(i["Cadidate Email"]), str(i["TSIN ID"].strip())]
        if tuple(z) in existing_emails:
            print("yes")
            z = candidates.query.filter_by(
                candidate_email=str(i["Cadidate Email"]),
                tsin_id=str(i["TSIN ID"].strip()),
            ).update(
                {
                    "tsin_id": str(i["TSIN ID"].strip()),
                    "candidate_name": str(i["Candidate Name "]),
                    "pan": str(i["PAN Number"]),
                    "candidate_email": str(i["Cadidate Email"]),
                    "current_stage": current_stage,
                    "request_raised_date": request_raised_date,
                    "tsin_opened_date": tsin_opened_date,
                    "resume_screened_date": resume_screened_date,
                    "l1_interview_date": l1_interview_date,
                    "l1_interviewer": str(i["L1 Interviewer"]),
                    "l2_interview_date": l2_interview_date,
                    "l2_interviewer": str(i["L2 interviewer"]),
                    "l3_interview_date": l3_interview_date,
                    "l3_interviewer": str(i["L3 Interviewer"]),
                    "offer_rollout_date": offer_rollout_date,
                    "joining_date": joining_date,
                    "buddy_assignment_date": buddy_assignment_date,
                    "buddy_name": str(i["Buddy Name"]),
                    "candidate_dropout_date": candidate_dropout_date,
                    "candidate_dropout_reason": str(i["Dropout Reason"]),
                    "modified_at": datetime.now(),
                    "status": "active",
                }
            )
            # z.tsin_id = str(i["TSIN ID"].strip())
            # z.candidate_name = str(i["Candidate Name "])
            # z.pan = str(i["PAN Number"])
            # z.candidate_email = str(i["Cadidate Email"])
            # z.current_stage = current_stage
            # z.request_raised_date = request_raised_date
            # z.status="active"
            db.session.commit()

        else:
            db.session.add(
                candidates(
                    tsin_id=str(i["TSIN ID"].strip()),
                    candidate_name=str(i["Candidate Name "]),
                    pan=str(i["PAN Number"]),
                    candidate_email=str(i["Cadidate Email"]),
                    current_stage=current_stage,
                    request_raised_date=request_raised_date,
                    tsin_opened_date=tsin_opened_date,
                    resume_screened_date=resume_screened_date,
                    l1_interview_date=l1_interview_date,
                    l1_interviewer=str(i["L1 Interviewer"]),
                    l2_interview_date=l2_interview_date,
                    l2_interviewer=str(i["L2 interviewer"]),
                    l3_interview_date=l3_interview_date,
                    l3_interviewer=str(i["L3 Interviewer"]),
                    offer_rollout_date=offer_rollout_date,
                    joining_date=joining_date,
                    buddy_assignment_date=buddy_assignment_date,
                    buddy_name=str(i["Buddy Name"]),
                    candidate_dropout_date=candidate_dropout_date,
                    candidate_dropout_reason=str(i["Dropout Reason"]),
                    resume="",
                    resume_screened_remarks="",
                    l1_interview_result="",
                    l1_interview_remarks="",
                    l2_interview_remarks="",
                    l2_interview_result="",
                    l3_interview_result="",
                    l3_interview_remarks="",
                    phone="",
                    current_location="",
                    current_company="",
                    experience="",
                    candidate_joined_date=candidate_joined_date,
                    created_at=datetime.now(),
                    modified_at=datetime.now(),
                    resume_remarks="",
                    status="active",
                    l1_completion=None,
                    l2_completion=None,
                    l3_completion=None
                )
            )
            db.session.commit()
    print("added to db")
    return redirect(url_for("main"))


@app.route("/upload-profile", methods=["GET", "POST"])
def profileUpload():
    cand_id = request.form["candidate_id"]
    phone = request.form["phone"]
    company = request.form["company"]
    experience = request.form["experience"]
    location = request.form["location"]
    resume = request.files["resume"]
    result2 = (
        candidates.query.with_entities(candidates.candidate_name)
        .filter_by(id=cand_id)
        .all()
    )
    if resume:
        resume.save("static/resume")
        minioClient.fput_object(
            "resume",
            "resume" + str(result2[0][0]).strip(),
            "static/resume",
        )
        print(
            "resume is successfully uploaded as "
            "object 'resume" + str(result2[0][0]).strip() + "' to bucket 'resume'."
        )

    db.session.query(candidates).filter(candidates.id == cand_id).update(
        {
            "phone": phone,
            "current_location": location,
            "current_company": company,
            "experience": experience,
            "modified_at": datetime.now(),
        }
    )
    db.session.commit()
    return redirect(url_for("main"))


@app.route("/download-resume", methods=["GET", "POST"])
def downloadresume():
    id = request.form.get("id")
    res = (
        candidates.query.with_entities(candidates.candidate_name).filter_by(id=id).all()
    )
    z = minioClient.get_object("resume", "resume" + res[0][0])
    minioClient.fget_object("resume", "resume" + res[0][0], "static/resume.pdf")
    return z.data


@app.route("/upload-candidates", methods=["GET", "POST"])
@token_forwarder
def candidates1(user):
    #print(token)
	if(user):
		role=user.role
	else:
		role=None
	return render_template("index.html",user=role)


@app.route("/update-stage", methods=["GET", "POST"])
def updateStage():
    cand_id = request.form.get("candidate_id")
    stage = request.form.get("stage")
    resume_remarks = request.form.get("resume_remarks")
    update_time = request.form.get("stageupdatetime")
    result = request.form.get("result")
    l1_remarks = request.form.get("l1_remarks")
    l2_interviewer_name = request.form.get("l2_interviewer_name")
    l2_interview_date = request.form.get("l2_interview_date")
    l2_remarks = request.form.get("l2_remarks")
    l3_interviewer_name = request.form.get("l3_interviewer_name")
    l3_interview_date = request.form.get("l3_interview_date")
    l3_remarks = request.form.get("l3_remarks")
    joining_date = request.form.get("joining_date")
    buddy_name = request.form.get("buddy_name")
    joining_stage_time = request.form.get("joiningstageupdatetime")
    dropout_stage_time = request.form.get("dropoutstageupdatetime")
    dropout_reason = request.form.get("dropout_reason")
    candidate=candidates.query.filter_by(id = cand_id).first()
    if stage == "resumescreened":
        if result == "passed":
            db.session.query(candidates).filter(candidates.id == cand_id).update(
                {
                    "current_stage": "Resume Screened for Interview",
                    "resume_screened_date": update_time,
                    "resume_remarks": resume_remarks,
                    "modified_at": datetime.now(),
                }
            )
        else:
            db.session.query(candidates).filter(candidates.id == cand_id).update(
                {
                    "current_stage": "Resume Rejected",
                    "resume_screened_date": update_time,
                    "modified_at": datetime.now(),
                }
            )
    if stage == "l1complete":
        if result == "passed":
            if candidate.l1_interview_date!=None:
                db.session.query(candidates).filter(candidates.id == cand_id).update(
                    {
                        "current_stage": "L1 Interview Complete",
                        "l1_completion": update_time,
                        "l1_interview_result": result,
                        "l1_interview_remarks": l1_remarks,
                        "l2_interviewer": l2_interviewer_name,
                        "l2_interview_date": l2_interview_date,
                        "modified_at": datetime.now(),
                    }
                )
            else:
                db.session.query(candidates).filter(candidates.id == cand_id).update(
                    {
                        "current_stage": "L1 Interview Complete",
                        "l1_interview_date":update_time,
                        "l1_completion": update_time,
                        "l1_interview_result": result,
                        "l1_interview_remarks": l1_remarks,
                        "l2_interviewer": l2_interviewer_name,
                        "l2_interview_date": l2_interview_date,
                        "modified_at": datetime.now(),
                    }
                )
        else:
            db.session.query(candidates).filter(candidates.id == cand_id).update(
                {
                    "current_stage": "Resume Rejected",
                    "l1_completion": update_time,
                    "l1_interview_result": result,
                    "l1_interview_remarks": l1_remarks,
                    "modified_at": datetime.now(),
                }
            )
        db.session.commit()
    elif stage == "l2complete":
        if result == "passed":
            if candidate.l2_interview_date!=None:
                db.session.query(candidates).filter(candidates.id == cand_id).update(
                    {
                        "current_stage": "L2 Interview Complete",
                        "l2_completion": update_time,
                        "l2_interview_result": result,
                        "l2_interview_remarks": l2_remarks,
                        "l3_interviewer": l3_interviewer_name,
                        "l3_interview_date": l3_interview_date,
                    }
                )
            else:
                db.session.query(candidates).filter(candidates.id == cand_id).update(
                    {
                        "current_stage": "L2 Interview Complete",
                        "l2_completion": update_time,
                        "l2_interview_date":update_time,
                        "l2_interview_result": result,
                        "l2_interview_remarks": l2_remarks,
                        "l3_interviewer": l3_interviewer_name,
                        "l3_interview_date": l3_interview_date,
                    }
                )
        else:
            db.session.query(candidates).filter(candidates.id == cand_id).update(
                {
                    "current_stage": "Resume Rejected",
                    "l2_completion": update_time,
                    "l2_interview_result": result,
                    "l2_interview_remarks": l2_remarks,
                    "modified_at": datetime.now(),
                }
            )
        db.session.commit()
    elif stage == "l3complete":
        if result == "passed":
            if candidate.l3_interview_date!=None:
                db.session.query(candidates).filter(candidates.id == cand_id).update(
                    {
                        "current_stage": "L3 Interview Complete",
                        "l3_completion": update_time,
                        "l3_interview_result": result,
                        "l3_interview_remarks": l3_remarks,
                        "modified_at": datetime.now(),
                    }
                )
            else:
                db.session.query(candidates).filter(candidates.id == cand_id).update(
                    {
                        "current_stage": "L3 Interview Complete",
                        "l3_interview_date":update_time,
                        "l3_completion": update_time,
                        "l3_interview_result": result,
                        "l3_interview_remarks": l3_remarks,
                        "modified_at": datetime.now(),
                    }
                )
        else:
            db.session.query(candidates).filter(candidates.id == cand_id).update(
                {
                    "current_stage": "Resume Rejected",
                    "l3_completion": update_time,
                    "l3_interview_result": result,
                    "l3_interview_remarks": l3_remarks,
                    "modified_at": datetime.now(),
                }
            )
        db.session.commit()
    elif stage == "offer":
        db.session.query(candidates).filter(candidates.id == cand_id).update(
            {
                "current_stage": "Offer RollOut",
                "offer_rollout_date": update_time,
                "joining_date": joining_date,
                "modified_at": datetime.now(),
            }
        )
        db.session.commit()
    elif stage == "buddy":
        db.session.query(candidates).filter(candidates.id == cand_id).update(
            {
                "current_stage": "Buddy Assignment",
                "buddy_assignment_date": update_time,
                "buddy_name": buddy_name,
                "modified_at": datetime.now(),
            }
        )
        db.session.commit()
    elif stage == "finalcandidate":
        if joining_stage_time and dropout_stage_time:
            return "Please choose appropriate values - Joining and dropout cannot come together!"
        elif joining_stage_time:
            db.session.query(candidates).filter(candidates.id == cand_id).update(
                {
                    "current_stage": "Candidate Joined",
                    "candidate_joined_date": joining_stage_time,
                    "modified_at": datetime.now(),
                }
            )
        elif dropout_stage_time:
            db.session.query(candidates).filter(candidates.id == cand_id).update(
                {
                    "current_stage": "Candidate Dropout",
                    "candidate_dropout_date": dropout_stage_time,
                    "candidate_dropout_reason": dropout_reason,
                    "modified_at": datetime.now(),
                }
            )
        db.session.commit()
    return redirect(url_for("main"))


@app.route("/add-tsin", methods=["GET", "POST"])
@token_forwarder
def tsinform(user):
    #print(token)
    result = roles.query.with_entities(roles.tsin_id).all()
    roless=role.query.all()
    chapters=chapter.query.all()
    squads=squad.query.all()
    tribes=tribe.query.all()
    final = []
    for i in result:
        final.append(i[0])
    if(user):
        Userrole=user.role
    else:
        Userrole=None
    return render_template("tsin_form.html", final=final, roles=roless, chapters=chapters, squads=squads, tribes=tribes, user=Userrole)


@app.route("/detailed-view", methods=["GET", "POST"])
@token_forwarder
def detailed(user):
    #print(token)
    tsin = request.form.get("val1")
    role = request.form.get("val2")
    chapter = request.form.get("val3")
    squad = request.form.get("val4")
    cname = request.form.get("val5")
    z = get_detailed_data()
    final = []
    for i in z:
        if tsin:
            if i["tsinid"].strip() == tsin.strip():
                if i not in final:
                    final.append(i)
        if role:
            if i["role"].strip() == role.strip():
                if i not in final:
                    final.append(i)
        if chapter:
            if i["chapter"].strip() == chapter.strip():
                if i not in final:
                    final.append(i)
        if squad:
            if i["squad"].strip() == squad.strip():
                if i not in final:
                    final.append(i)
        if cname:
            if i["candidate_name"].strip() == cname.strip():
                if i not in final:
                    final.append(i)
    if(user):
        role=user.role
    else:
        role=None
    if final == []:
        return render_template("detailed.html", final=z, user=role)
    else:
        return render_template("detailed.html", final=final, user=role)

@app.route("/activate-role/<tsin>", methods=["GET", "POST"])
def activate_role(tsin):
    db.session.query(roles).filter(roles.tsin_id == tsin).update(
        {
            "status": "active",
            "modified_at": datetime.now(),
        }
    )
    db.session.commit()
    return redirect(url_for("main"))

@app.route("/delete-role/<tsin>", methods=["GET", "POST"])
def delete_role(tsin):
    db.session.query(roles).filter(roles.tsin_id == tsin).update(
        {
            "status": "inactive",
            "modified_at": datetime.now(),
        }
    )
    db.session.commit()
    return redirect(url_for("main"))

@app.route("/activate-profile/<id>", methods=["GET", "POST"])
def activate_profile(id):
    db.session.query(candidates).filter(candidates.id == id).update(
        {
            "status": "active",
            "modified_at": datetime.now(),
        }
    )
    db.session.commit()
    return redirect(url_for("main"))

@app.route("/delete-profile/<id>", methods=["GET", "POST"])
def delete_profile(id):
    db.session.query(candidates).filter(candidates.id == id).update(
        {
            "status": "inactive",
            "modified_at": datetime.now(),
        }
    )
    db.session.commit()
    return redirect(url_for("main"))


@app.route("/new-position", methods=["GET", "POST"])
def newposition():
    total=request.form.get("total")
    tsinid = []
    role = []
    chapter = []
    squad = []
    snow_id = []
    tribe = []
    demandtype = []
    for i in range(int(total)):
        tsinid.append(request.form.get("tsinid"+str(i)))
        role.append(request.form.get("role"+str(i)))
        chapter.append(request.form.get("chapter"+str(i)))
        squad.append(request.form.get("squad"+str(i)))
        snow_id.append(request.form.get("snowid"+str(i)))
        tribe.append(request.form.get("tribe"+str(i)))
        demandtype.append(request.form.get("demand"+str(i)))

    result = roles.query.with_entities(roles.tsin_id, roles.snow_id).all()
    for i in result:
        if i[0].strip() in tsinid:
            return "TSIN ID already exists"
        if snow_id!=[]:
            if i[1].strip() in snow_id:
                print(i[1])
                return "SNOW ID already exists"
    for i in range(len(tsinid)):
        db.session.add(
            roles(
                tsin_id=tsinid[i],
                role=role[i],
                chapter=chapter[i],
                squad=squad[i],
                demand_type=demandtype[i],
                tribe=tribe[i],
                snow_id=snow_id[i],
                aspd_date=None,
                status="active",
                created_at=datetime.now(),
                modified_at=datetime.now(),
            )
        )
    db.session.commit()
    return total+" New Roles Created"


@app.route("/add-new-profile", methods=["GET", "POST"])
def newprofile():
    tsin = request.form["tsin_id"]
    phone = request.form["phone"]
    name = request.form["name"]
    email = request.form["email"]
    pan = request.form["pan"]
    company = request.form["company"]
    experience = request.form["experience"]
    location = request.form["location"]
    resume = request.files["resume"]
    db.session.add(
        candidates(
            tsin_id=tsin,
            candidate_name=name,
            pan=pan,
            candidate_email=email,
            current_stage="Profile Upload",
            status="active",
            request_raised_date="",
            tsin_opened_date="",
            resume_screened_date="",
            l1_interview_date="",
            l1_interviewer="",
            l2_interview_date="",
            l2_interviewer="",
            l3_interview_date="",
            l3_interviewer="",
            offer_rollout_date="",
            joining_date="",
            buddy_assignment_date="",
            buddy_name="",
            candidate_dropout_date="",
            candidate_dropout_reason="",
            resume="",
            resume_screened_remarks="",
            l1_interview_result="",
            l1_interview_remarks="",
            l2_interview_remarks="",
            l2_interview_result="",
            l3_interview_result="",
            l3_interview_remarks="",
            phone=phone,
            current_location=location,
            current_company=company,
            experience=experience,
            candidate_joined_date="",
            created_at=datetime.now(),
            modified_at=datetime.now(),
        )
    )
    db.session.commit()

    if resume:
        resume.save("static/resume")
        minioClient.fput_object("resume", "resume" + str(name), "static/resume")
        print(
            "resume is successfully uploaded as "
            "object 'resume" + str(name) + "' to bucket 'resume'."
        )
    return redirect(url_for("main"))


@app.route("/apply-filter", methods=["GET", "POST"])
def apply_filter():
    tsin = request.form.get("val1")
    role = request.form.get("val2")
    chapter = request.form.get("val3")
    squad = request.form.get("val4")
    cname = request.form.get("val5")
    z = get_detailed_data()
    final = []
    for i in z:
        if tsin:
            if i["tsinid"].strip() == tsin.strip():
                if i not in final:
                    final.append(i)
        if role:
            if i["role"].strip() == role.strip():
                if i not in final:
                    final.append(i)
        if chapter:
            if i["chapter"].strip() == chapter.strip():
                if i not in final:
                    final.append(i)
        if squad:
            if i["squad"].strip() == squad.strip():
                if i not in final:
                    final.append(i)
        if cname:
            if i["candidate_name"].strip() == cname.strip():
                if i not in final:
                    final.append(i)
    return render_template("detailed.html", final=final)


@app.route("/edit-role", methods=["GET", "POST"])
def editrole():
    tsin = request.form.get("tsin_id")
    snow_id = request.form.get("snow_id")
    chapter = request.form.get("chapter")
    role = request.form.get("role")
    squad = request.form.get("squad")
    demandtype = request.form.get("demandtype")
    tribe = request.form.get("tribe")
    db.session.query(roles).filter(roles.tsin_id == tsin).update(
        {
            "snow_id": snow_id,
            "chapter": chapter,
            "role": role,
            "squad": squad,
            "demand_type": demandtype,
            "tribe": tribe,
            "modified_at": datetime.now(),
        }
    )
    db.session.commit()
    return redirect(url_for("main"))


@app.route("/dashboard", methods=["GET", "POST"])
@token_forwarder
def dashboard(user):
    #print(token)
    z, drop = total_offers()
    new_pos = get_new_profiles()
    print(z)
    weekly = 0
    montly = 0
    quarterly = 0
    for i in z.values():
        for j in i:
            if j <= 14:
                weekly += 1
            if j <= 30:
                montly += 1
            if j <= 90:
                quarterly += 1
    for i in z:
        z[i] = len(z[i])
    offers = [weekly, montly, quarterly]
    dropout_weekly = 0
    dropout_montly = 0
    dropout_quarterly = 0
    for i in drop.values():
        for j in i:
            if j <= 14:
                dropout_weekly += 1
            if j <= 30:
                dropout_montly += 1
            if j <= 30:
                dropout_quarterly += 1
    for i in drop:
        drop[i] = len(drop[i])
    new_weekly = 0
    new_monthly = 0
    new_quarterly = 0
    for i in new_pos.values():
        for j in i:
            if j <= 14:
                new_weekly += 1
            if j <= 30:
                new_monthly += 1
            if j <= 90:
                new_quarterly += 1
    new_pos_roles = get_role_wise_profiles()
    dropouts = [dropout_weekly, dropout_montly, dropout_quarterly]
    new_positions = [new_weekly, new_monthly, new_quarterly]
    # final_z=json.dumps(z)
    if(user):
        role=user.role
    else:
        role=None
    return render_template(
        "dashboard.html",
        role_wise_offers=z,
        role_wise_dropout=drop,
        role_wise_new=new_pos_roles,
        total_offer=offers,
        total_dropouts=dropouts,
        new_positions=new_positions,
		user=role
    )
@app.route('/getData', methods = ['GET', 'POST'])
def getData():
    tsin_id = request.args.get('tsin_id')
    role = request.args.get('role')
    chapter = request.args.get('chapter')
    squad = request.args.get('squad')
    con=sqlite3.connect('db/data2.db')
    df=pd.read_sql_query("SELECT * FROM candidates",con)#db.engine)
    #print(df.head())
    #print(df[df['resume_screened_remarks']=='selected']['id'].count()/df['id'].count())
    df=df.astype({'tsin_opened_date':'datetime64[ns]','resume_screened_date':'datetime64[ns]','l1_interview_date':'datetime64[ns]','l2_interview_date':'datetime64[ns]','l3_interview_date':'datetime64[ns]','offer_rollout_date':'datetime64[ns]','buddy_assignment_date':'datetime64[ns]','joining_date':'datetime64[ns]','candidate_dropout_date':'datetime64[ns]'})
    df['resume_sharing_time']=df['resume_screened_date']-df['tsin_opened_date']
    df['l1_completion_time']=df['l1_interview_date']-df['resume_screened_date']
    df['l2_completion_time']=df['l2_interview_date']-df['l1_interview_date']
    df['l3_completion_time']=df['l3_interview_date']-df['l2_interview_date']
    df['time_to_offer']=df['offer_rollout_date']-df['tsin_opened_date']
    df['time_to_fill']=df['joining_date']-df['tsin_opened_date']
    if tsin_id=='all':
        if(role):
            df=df[df['roles']==role]
        if(chapter):
            df=df[df['chapter']==chapter]
        if(squad):
            df=df[df['squads']==squad]
        if(df.empty):
            return {"KPIlabels":["Resume Selection Rate","L1 Selection Rate","L2 Selection Rate","L3 Selection Rate","Joining rate","Offer ratio"],
            "KPIdata":[],
            "SLAlabels":["Resume sharing","L1 completion","L2 completion","L3 completion","Buddy Assignment","Time to offer"],
            "SLAdata":[]}
        t=df[df['offer_rollout_date'].notnull()]
        d1=np.array([df[df['resume_sharing_time']<pd.Timedelta('5 days')]['id'].count(),df[df['l1_completion_time']<pd.Timedelta('3 days')]['id'].count(), df[df['l2_completion_time']<pd.Timedelta('3 days')]['id'].count(),df[df['l3_completion_time']<pd.Timedelta('3 days')]['id'].count(),df[df['time_to_offer']<pd.Timedelta('3 days')]['id'].count(),df[df['time_to_fill']<pd.Timedelta('3 days')]['id'].count()])
        d2=np.array([df[df['resume_sharing_time']<pd.Timedelta('7 days')]['id'].count(),df[df['l1_completion_time']<pd.Timedelta('5 days')]['id'].count(), df[df['l2_completion_time']<pd.Timedelta('5 days')]['id'].count(),df[df['l3_completion_time']<pd.Timedelta('5 days')]['id'].count(),df[df['time_to_offer']<pd.Timedelta('5 days')]['id'].count(),df[df['time_to_fill']<pd.Timedelta('5 days')]['id'].count()]) - d1
        d3=np.array([df[df['resume_sharing_time']>pd.Timedelta('7 days')]['id'].count(),df[df['l1_completion_time']>pd.Timedelta('5 days')]['id'].count(), df[df['l2_completion_time']>pd.Timedelta('5 days')]['id'].count(),df[df['l3_completion_time']>pd.Timedelta('5 days')]['id'].count(),df[df['time_to_offer']>pd.Timedelta('5 days')]['id'].count(),df[df['time_to_fill']>pd.Timedelta('5 days')]['id'].count()])
        return {"KPIlabels":["Resume Selection Rate","L1 Selection Rate","L2 Selection Rate","L3 Selection Rate","Joining rate","Offer ratio"],
        "KPIdata":(np.array([df[df['resume_screened_remarks']=='selected']['id'].count()/df['id'].count(),
        df[df['l1_interview_remarks']=='selected']['id'].count()/df[df['resume_screened_remarks'].notnull()]['id'].count(),
        df[df['l2_interview_remarks']=='selected']['id'].count()/df[df['resume_screened_remarks'].notnull()]['id'].count(),
        df[df['l3_interview_remarks']=='selected']['id'].count()/df[df['resume_screened_remarks'].notnull()]['id'].count(),
        (t['id'].count()-t[t['candidate_dropout_date'].notnull()]['id'].count())/t['id'].count() if len(t)>0 else 0,
        (t['id'].count()-t[t['candidate_dropout_date'].notnull()]['id'].count())/df[df['l1_interview_remarks']=='selected']['id'].count() if len(t)>0 else 0])*100).tolist(),
        "SLAlabels":["Resume sharing","L1 completion","L2 completion","L3 completion","Buddy Assignment","Time to offer"],
        "SLAdata":[d1.astype('int').tolist(),d2.astype('int').tolist(),d3.astype('int').tolist()]}
    else:
        df=df[df['tsin_id']==int(tsin_id)]
        print(role,squad,chapter)
        if(role):
            df=df[df['roles']==role]
        if(chapter):
            df=df[df['chapter']==chapter]
        if(squad):
            df=df[df['squads']==squad]
        if(df.empty):
            return {"KPIlabels":["Resume Selection Rate","L1 Selection Rate","L2 Selection Rate","L3 Selection Rate","Joining rate","Offer ratio"],
            "KPIdata":[],
            "SLAlabels":["Resume sharing","L1 completion","L2 completion","L3 completion","Buddy Assignment","Time to offer"],
            "SLAdata":[]}
        t=df[df['offer_rollout_date'].notnull()]
        #print(df[df['resume_screened_remarks']=='selected']['id'].count())
        d1=np.array([df[df['resume_sharing_time']<pd.Timedelta('5 days')]['id'].count(),df[df['l1_completion_time']<pd.Timedelta('3 days')]['id'].count(), df[df['l2_completion_time']<pd.Timedelta('3 days')]['id'].count(),df[df['l3_completion_time']<pd.Timedelta('3 days')]['id'].count(),df[df['time_to_offer']<pd.Timedelta('3 days')]['id'].count(),df[df['time_to_fill']<pd.Timedelta('3 days')]['id'].count()])
        d2=np.array([df[df['resume_sharing_time']<pd.Timedelta('7 days')]['id'].count(),df[df['l1_completion_time']<pd.Timedelta('5 days')]['id'].count(), df[df['l2_completion_time']<pd.Timedelta('5 days')]['id'].count(),df[df['l3_completion_time']<pd.Timedelta('5 days')]['id'].count(),df[df['time_to_offer']<pd.Timedelta('5 days')]['id'].count(),df[df['time_to_fill']<pd.Timedelta('5 days')]['id'].count()]) - d1
        d3=np.array([df[df['resume_sharing_time']>pd.Timedelta('7 days')]['id'].count(),df[df['l1_completion_time']>pd.Timedelta('5 days')]['id'].count(), df[df['l2_completion_time']>pd.Timedelta('5 days')]['id'].count(),df[df['l3_completion_time']>pd.Timedelta('5 days')]['id'].count(),df[df['time_to_offer']>pd.Timedelta('5 days')]['id'].count(),df[df['time_to_fill']>pd.Timedelta('5 days')]['id'].count()])

        d= {"KPIlabels":["Resume Selection Rate","L1 Selection Rate","L2 Selection Rate","L3 Selection Rate","Joining rate","Offer ratio"],
        "KPIdata":(np.array([df[df['resume_screened_remarks']=='selected']['id'].count()/df['id'].count(),
        df[df['l1_interview_remarks']=='selected']['id'].count()/df[df['resume_screened_remarks'].notnull()]['id'].count(),
        df[df['l2_interview_remarks']=='selected']['id'].count()/df[df['resume_screened_remarks'].notnull()]['id'].count(),
        df[df['l3_interview_remarks']=='selected']['id'].count()/df[df['resume_screened_remarks'].notnull()]['id'].count(),
        (t['id'].count()-t[t['candidate_dropout_date'].notnull()]['id'].count())/t['id'].count() if len(t)>0 else 0,
        (t['id'].count()-t[t['candidate_dropout_date'].notnull()]['id'].count())/df[df['l1_interview_remarks']=='selected']['id'].count() if len(t)>0 else 0])*100).tolist(),
        "SLAlabels":["Resume sharing","L1 completion","L2 completion","L3 completion","Buddy Assignment","Time to offer"],
        "SLAdata":[d1.astype('int').tolist(),d2.astype('int').tolist(),d3.astype('int').tolist()]}
        #print(d)
        return d

@app.route('/add-chapter', methods = ['GET', 'POST'])
def addchapter():
    Chapter=request.form.get("chapter")
    db.session.add(chapter(chapter_name=Chapter))
    db.session.commit()
    return "Chapter Added Succesfully"

@app.route('/add-role', methods = ['GET', 'POST'])
def addroler():
    Role=request.form.get("role")
    db.session.add(role(role_name=Role))
    db.session.commit()
    return "Role Added Succesfully"

@app.route('/add-squad', methods = ['GET', 'POST'])
def addsquad():
    Squad=request.form.get("squad")
    db.session.add(squad(squad_name=Squad))
    db.session.commit()
    return "Squad Added Succesfully"

@app.route('/add-tribe', methods = ['GET', 'POST'])
def addtribe():
    Tribe=request.form.get("tribe")
    db.session.add(tribe(tribe_name=Tribe))
    db.session.commit()
    return "Tribe Added Succesfully"

@app.route('/login', methods = ['GET', 'POST'])
def login():
    return render_template("login.html")
if __name__ == "__main__":
    app.run()
