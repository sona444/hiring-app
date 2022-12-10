from flask import Flask, render_template, request, redirect, url_for
from openpyxl import load_workbook
import sqlite3
import pandas as pd
from minio import Minio
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import update
load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://yashraj:yashraj@localhost:5432/hiringapp"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
from models import candidates, roles

client = Minio(
    "play.min.io",
    access_key = "Q3AM3UQ867SPQQA43P2F",
    secret_key = "zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
)
found = client.bucket_exists("resume")
if not found:
    client.make_bucket("resume")
else:
    print("Bucket 'resume' already exists")


def get_abstract_data():
    result = roles.query.all()
    nums = {}
    for i in result:
        nums[i.tsin_id.strip()] = {'stage1' : 0, 'stage2' : 0, 'stage3' : 0, 'stage4' : 0, 'stage5' : 0, 'stage6' : 0, 'stage7' : 0, 'stage8' : 0}
    result2 = candidates.query.all()
    list_of_phone = []
    for i in result2:
        list_of_phone.append(i.phone)
    d = {}
    for i in result2:
        if i.current_stage.strip() == 'Resume Screened for Interview':
            nums[i.tsin_id.strip()]['stage1'] += 1
        elif i.current_stage.strip() == 'L1 Interview Complete':
            nums[i.tsin_id.strip()]['stage2'] += 1
        elif i.current_stage.strip() == 'L2 Interview Complete':
            nums[i.tsin_id.strip()]['stage3'] += 1
        elif i.current_stage.strip() == 'L3 Interview Complete':
            nums[i.tsin_id.strip()]['stage4'] += 1
        elif i.current_stage.strip() == 'Offer RollOut':
            nums[i.tsin_id.strip()]['stage5'] += 1
        elif i.current_stage.strip() == 'Buddy Assignment':
            nums[i.tsin_id.strip()]['stage6'] += 1
        elif i.current_stage.strip() == 'Candidate Joined' or i.current_stage.strip() == 'Candidate Dropout':
            nums[i.tsin_id.strip()]['stage7'] += 1
        elif i.current_stage.strip() == 'Resume Rejected':
            nums[i.tsin_id.strip()]['stage8'] += 1
        if i.tsin_id in d:
            d[i.tsin_id].append({
                'id' : i.id,
                'candidate_name' : i.candidate_name, 
                'pan' : i.pan,
                'candidate_email' : i.candidate_email, 
                'current_stage' : i.current_stage,
                'request_raised_date' : i.request_raised_date, 
                'tsin_opened_date' : i.tsin_opened_date, 
                'resume_screened_date' : i.resume_screened_date, 
                'l1_interview_date' : i.l1_interview_date, 
                'l1_interviewer' : i.l1_interviewer, 
                'l2_interview_date' : i.l2_interview_date, 
                'l2_interviewer' : i.l2_interviewer, 
                'l3_interview_date' : i.l3_interview_date, 
                'l3_interviewer' : i.l3_interviewer, 
                'offer_rollout_date' : i.offer_rollout_date, 
                'joining_date' : i.joining_date, 
                'buddy_assignment_date' : i.buddy_assignment_date, 
                'buddy_name' : i.buddy_name, 
                'candidate_dropout_date' : i.candidate_dropout_date, 
                'candidate_dropout_reason' : i.candidate_dropout_reason, 
                'resume' : i.resume, 
                'phone' : i.phone, 
                'current_location' : i.current_location, 
                'current_company' : i.current_company, 
                'experience' : i.experience
            })
        else:
            d[i.tsin_id] = [{
                'id' : i.id,
                'candidate_name' : i.candidate_name, 
                'pan' : i.pan,
                'candidate_email' : i.candidate_email, 
                'current_stage' : i.current_stage,
                'request_raised_date' : i.request_raised_date, 
                'tsin_opened_date' : i.tsin_opened_date, 
                'resume_screened_date' : i.resume_screened_date, 
                'l1_interview_date' : i.l1_interview_date, 
                'l1_interviewer' : i.l1_interviewer, 
                'l2_interview_date' : i.l2_interview_date, 
                'l2_interviewer' : i.l2_interviewer, 
                'l3_interview_date' : i.l3_interview_date, 
                'l3_interviewer' : i.l3_interviewer, 
                'offer_rollout_date' : i.offer_rollout_date, 
                'joining_date' : i.joining_date, 
                'buddy_assignment_date' : i.buddy_assignment_date, 
                'buddy_name' : i.buddy_name, 
                'candidate_dropout_date' : i.candidate_dropout_date, 
                'candidate_dropout_reason' : i.candidate_dropout_reason, 
                'resume' : i.resume, 
                'phone' : i.phone, 
                'current_location' : i.current_location, 
                'current_company' : i.current_company, 
                'experience' : i.experience
            }]
    return result, d, nums, list_of_phone

def get_detailed_data():
    # con=sqlite3.connect('db/data.db') #connecting to the database
    # cursor=con.cursor()
    # cursor.execute('SELECT tsin_id, role, chapter, squad, demand_type, Tribe, snow_id from roles;')
    # result = cursor.fetchall()
    # cursor.execute('SELECT tsin_id, candidate_name, pan, candidate_email, current_stage, request_raised_date, tsin_opened_date, 
    # resume_screened_date, l1_interview_date, l1_interviewer, l2_interview_date, l2_interviewer, l3_interview_date, l3_interviewer, 
    # offer_rollout_date, joining_date, buddy_assignment_date, buddy_name, candidate_dropout_date, candidate_dropout_reason, resume, id, 
    # phone, current_location, current_company, experience from candidates;')
    # result2 = cursor.fetchall()
    result = roles.query.all()
    result2 = candidates.query.all()
    roles = {}
    for i in result:
        roles[i.tsin_id.strip()] = {
            "role" : i.Role, 
            "chapter" : i.Chapter, 
            "squad" : i.Squad, 
            "demand_type" : i.demand_type, 
            "tribe" : i.Tribe, 
            "snow_id" : i.snow_id
        }
    d=[]
    for i in result2:
        d.append({
            'tsinid' : i.tsin_id,
            'chapter' : roles[i.tsin_id.strip()]['chapter'],
            'squad' : roles[i.tsin_id.strip()]['squad'],
            'demand_type' : roles[i.tsin_id.strip()]['demand_type'],
            'tribe' : roles[i.tsin_id.strip()]['tribe'],
            'snow_id' : roles[i.tsin_id.strip()]['snow_id'],
            'role' : roles[i.tsin_id.strip()]['role'],
            'id' : i.id,
            'candidate_name' : i.candidate_name, 
            'pan' : i.pan,
            'candidate_email' : i.candidate_email, 
            'current_stage' : i.current_stage,
            'request_raised_date' : i.request_raised_date, 
            'tsin_opened_date' : i.tsin_opened_date, 
            'resume_screened_date' : i.resume_screened_date, 
            'l1_interview_date' : i.l1_interview_date, 
            'l1_interviewer' : i.l1_interviewer, 
            'l2_interview_date' : i.l2_interview_date, 
            'l2_interviewer' : i.l2_interviewer, 
            'l3_interview_date' : i.l3_interview_date, 
            'l3_interviewer' : i.l3_interviewer, 
            'offer_rollout_date' : i.offer_rollout_date, 
            'joining_date' : i.joining_date, 
            'buddy_assignment_date' : i.buddy_assignment_date, 
            'buddy_name' : i.buddy_name, 
            'candidate_dropout_date' : i.candidate_dropout_date, 
            'candidate_dropout_reason' : i.candidate_dropout_reason, 
            'resume' : i.resume, 
            'phone' : i.phone, 
            'current_location' : i.current_location, 
            'current_company' : i.current_company, 
            'experience' : i.experience
        })
    return d

@app.route('/')
def main():
    result, d, nums, phones = get_abstract_data()
    return render_template('candidates.html', roles = result, candidates = d, nums = nums, phones = phones)


@app.route('/upload-dataset', methods = ['GET', 'POST'])
def uploadDs():
    f = request.files['file'] #File input
    if not f:
        return "No file attached"

    global filename
    filename = f.filename #changing global value of filename

    path='{}/{}'.format('static', filename)
    f.save(path)
    x = path.split('.')[-1]

    #reading filedata start
    if x == 'xlsx':
        new_wb = load_workbook(path)
        Dataframe = pd.read_excel(new_wb,engine = 'openpyxl')
    elif x == 'csv':
        Dataframe = pd.read_csv(path, encoding = "ISO-8859-1")
    else:
        return('Please upload the file in xlsx or csv only')
    #reading filedata end

    dict_of_records = Dataframe.to_dict(orient = 'record')

    for i in dict_of_records:
        existing_roles = roles.query.filter_by(tsin_id = i['TSIN ID'].strip()).all()
        existing_emails = candidates.query.with_entities(candidates.candidate_email, candidates.tsin_id).all()
        if len(existing_roles) == 0:
            db.session.add(roles(
                tsin_id = str(i['TSIN ID'].strip()), 
                role = str(i['Role ']), 
                chapter = str(i['Chapter']), 
                squad = str(i['Squad']),
                demand_type = str(i['Type of Demand']), 
                tribe = str(i['Tribe']), 
                snow_id = str(i['Snow ID'])
            ))
            db.session.commit()

        z = [" " + str(i['Cadidate Email']) + " ", " " + str(i['TSIN ID'].strip()) + " "]
        if tuple(z) in existing_emails:
            print('yes')
            z = candidates.query.filter_by(candidate_email = str(i['Cadidate Email']), tsin_id = str(i['TSIN ID'].strip()))
            z.tsin_id = str(i['TSIN ID'].strip())
            z.candidate_name = str(i['Candidate Name '])
            z.pan = str(i['PAN Number'])
            z.candidate_email = str(i['Cadidate Email'])
            z.current_stage = str(i['Current Stage '])
            z.request_raised_date = str(i['APSD Date'])
            
        else:
            db.session.add(candidates(
                tsin_id = str(i['TSIN ID'].strip()), 
                candidate_name = str(i['Candidate Name ']), 
                pan = str(i['PAN Number']), 
                candidate_email = str(i['Cadidate Email']), 
                current_stage = str(i['Current Stage ']), 
                request_raised_date = str(i['APSD Date']), 
                tsin_opened_date = str(i['TSIN Opened']), 
                resume_screened_date = str(i['Resume Screened']), 
                l1_interview_date = str(i['L1 Interview Complete']), 
                l1_interviewer = str(i['L1 Interviewer ']), 
                l2_interview_date = str(i['L2 Interview Complete']), 
                l2_interviewer = str(i['L2 interviewer']), 
                l3_interview_date = str(i['L3 Interview Complete']), 
                l3_interviewer = str(i['L3 Interviewer']), 
                offer_rollout_date = str(i['Offer RollOut ']), 
                joining_date = str(i['Joining Date']), 
                buddy_assignment_date = str(i['Buddy Assignment ']), 
                buddy_name = str(i['Buddy Name']), 
                candidate_dropout_date = str(i['Candidate Joined']), 
                candidate_dropout_reason = str(i['Candidate Dropout']), 
                resume = str(i['Dropout Reason']),
                resume_screened_remarks = "",
                l1_interview_result = "",
                l1_interview_remarks = "",
                l2_interview_remarks = "",
                l2_interview_result = "",
                l3_interview_result = "",
                l3_interview_remarks = "",
                phone = "",
                current_location = "",
                current_company = "",
                experience = "",
                candidate_joined_date = ""
            ))
            db.session.commit()
    print('added to db')
    return redirect(url_for('main'))

@app.route('/upload-profile', methods = ['GET', 'POST'])
def profileUpload():
    cand_id = request.form['candidate_id']
    phone = request.form['phone']
    company = request.form['company']
    experience = request.form['experience']
    location = request.form['location']
    resume = request.files['resume']
    # con=sqlite3.connect('db/data.db') #connecting to the database
    # cursor=con.cursor()
    # cursor.execute("SELECT candidate_name from candidates where id = '"+ cand_id +"';")
    # result2=cursor.fetchall()
    # print(result2[0][0])
    result2 = candidates.query.with_entities(candidates.candidate_name).filter_by(id = cand_id).all()
    if resume:
        resume.save('static/resume')
        client.fput_object("resume", "resume" + str(result2[0][0]).strip(), "static/resume",)
        print(
            "resume is successfully uploaded as "
            "object 'resume" + str(result2[0][0]).strip() + "' to bucket 'resume'."
        )
    
    db.session.query(candidates).filter(candidates.id == cand_id).update({
        'phone' : phone, 
        'current_location' : location, 
        'current_company' : company,
        'experience' : experience    
    })
    db.session.commit()
    # cursor.execute("UPDATE candidates SET phone = '"+ phone +"', current_location = '"+ location +"', current_company='"+ company +"', 
    # experience = '"+ experience +"' WHERE id= '"+ cand_id+"';")
    # con.commit()    
    return redirect(url_for('main'))

@app.route('/download-resume', methods = ['GET', 'POST'])
def downloadresume():
    id = request.form.get('id')
    # con=sqlite3.connect('db/data.db') #connecting to the database
    # cursor=con.cursor()
    # cursor.execute("SELECT candidate_name from candidates where id = '"+id+"'")
    # res = cursor.fetchall()
    res = candidates.query.with_entities(candidates.candidate_name).filter_by(id = id).all()
    z = client.get_object('resume', 'resume' + res[0][0])
    client.fget_object('resume', 'resume' + res[0][0], "static/resume.pdf")
    return z.data

@app.route('/upload-candidates', methods = ['GET', 'POST'])
def candidates1():
    return render_template('index.html')

@app.route('/update-stage', methods = ['GET', 'POST'])
def updateStage():
    # con=sqlite3.connect('db/data.db') #connecting to the database
    # cursor=con.cursor()
    cand_id = request.form.get('candidate_id')
    stage = request.form.get('stage')
    update_time = request.form.get('stageupdatetime')
    result = request.form.get('result')
    l1_remarks = request.form.get('l1_remarks')
    l2_interviewer_name = request.form.get('l2_interviewer_name')
    l2_interview_date = request.form.get('l2_interview_date')
    l2_remarks = request.form.get('l2_remarks')
    l3_interviewer_name = request.form.get('l3_interviewer_name')
    l3_interview_date = request.form.get('l3_interview_date')
    l3_remarks = request.form.get('l3_remarks')
    joining_date = request.form.get('joining_date')
    buddy_name = request.form.get('buddy_name')
    joining_stage_time = request.form.get('joiningstageupdatetime')
    dropout_stage_time = request.form.get('dropoutstageupdatetime')
    dropout_reason = request.form.get('dropout_reason')
    if stage == 'l1complete':
        if result == 'passed':
            db.session.query(candidates).filter(candidates.id == cand_id).update({
                'current_stage' : 'L1 Interview Complete', 
                'l1_completion' : update_time, 
                'l1_interview_result' : result,
                'l1_interview_remarks' : l1_remarks,
                'l2_interviewer' : l2_interviewer_name,
                'l2_interview_date' : l2_interview_date
            })
            # cursor.execute("UPDATE candidates SET current_stage = 'L1 Interview Complete', l1_completion = '"+ update_time +"', 
            # l1_interview_result = '"+ result +"', l1_interview_remarks = '"+ l1_remarks +"', l2_interviewer='"+ l2_interviewer_name +"', 
            # l2_interview_date = '"+ l2_interview_date +"' WHERE id= '"+ cand_id+"';")
        else:
            db.session.query(candidates).filter(candidates.id == cand_id).update({
                'current_stage' : 'Resume Rejected', 
                'l1_completion' : update_time, 
                'l1_interview_result' : result,
                'l1_interview_remarks' : l1_remarks
            })
            # cursor.execute("UPDATE candidates SET current_stage = 'Resume Rejected', l1_completion = '"+ update_time +"', 
            # l1_interview_result = '"+ result +"', l1_interview_remarks = '"+ l1_remarks +"';")
        # con.commit()
        db.session.commit()  
    elif stage == 'l2complete':
        if result=='passed':
            db.session.query(candidates).filter(candidates.id == cand_id).update({
                'current_stage' : 'L2 Interview Complete', 
                'l2_completion' : update_time, 
                'l2_interview_result' : result,
                'l2_interview_remarks' : l2_remarks,
                'l3_interviewer' : l3_interviewer_name,
                'l3_interview_date' : l3_interview_date
            })
            # cursor.execute("UPDATE candidates SET current_stage = 'L2 Interview Complete', l2_completion = '"+ update_time +"',
            # l2_interview_result = '"+ result +"', l2_interview_remarks = '"+ l2_remarks +"', l3_interviewer='"+ l3_interviewer_name +"',
            # l3_interview_date = '"+ l3_interview_date +"' WHERE id= '"+ cand_id+"';")
        else:
            db.session.query(candidates).filter(candidates.id == cand_id).update({
                'current_stage' : 'Resume Rejected', 
                'l2_completion' : update_time, 
                'l2_interview_result' : result,
                'l2_interview_remarks' : l2_remarks
            })
            # cursor.execute("UPDATE candidates SET current_stage = 'Resume Rejected', l2_completion = '"+ update_time +"', 
            # l2_interview_result = '"+ result +"', l2_interview_remarks = '"+ l2_remarks +"';")
        # con.commit()
        db.session.commit()
    elif stage == 'l3complete':
        if result=='passed':
            db.session.query(candidates).filter(candidates.id == cand_id).update({
                'current_stage' : 'L3 Interview Complete', 
                'l3_completion' : update_time, 
                'l3_interview_result' : result,
                'l3_interview_remarks' : l3_remarks,
            })
            # cursor.execute("UPDATE candidates SET current_stage = 'L3 Interview Complete', l3_completion = '"+ update_time +"', 
            # l3_interview_result = '"+ result +"', l3_interview_remarks = '"+ l3_remarks +"' WHERE id= '"+ cand_id+"';")
        else:
            db.session.query(candidates).filter(candidates.id == cand_id).update({
                'current_stage' : 'Resume Rejected', 
                'l3_completion' : update_time, 
                'l3_interview_result' : result,
                'l3_interview_remarks' : l3_remarks
            })
            # cursor.execute("UPDATE candidates SET current_stage = 'Resume Rejected', l3_completion = '"+ update_time +"', 
            # l3_interview_result = '"+ result +"', l3_interview_remarks = '"+ l3_remarks +"';")
        # con.commit()
        db.session.commit()
    elif stage == 'offer':
        db.session.query(candidates).filter(candidates.id == cand_id).update({
            'current_stage' : 'Offer RollOut', 
            'offer_rollout_date' : update_time, 
            'joining_date' : joining_date,
        })
        db.session.commit()
        # cursor.execute("UPDATE candidates SET current_stage = 'Offer RollOut', offer_rollout_date = '"+ update_time +"', 
        # joining_date = '"+ joining_date +"' WHERE id= '"+ cand_id+"';")
        # con.commit()
    elif stage == 'buddy':
        db.session.query(candidates).filter(candidates.id == cand_id).update({
            'current_stage' : 'Buddy Assignment', 
            'buddy_assignment_date' : update_time, 
            'buddy_name' : buddy_name,
        })
        db.session.commit()
        # cursor.execute("UPDATE candidates SET current_stage = 'Buddy Assignment', buddy_assignment_date = '"+ update_time +"', 
        # buddy_name = '"+ buddy_name +"' WHERE id= '"+ cand_id+"';")
        # con.commit()
    elif stage == 'finalcandidate':
        if joining_stage_time and dropout_stage_time:
            return "Please choose appropriate values - Joining and dropout cannot come together!"
        elif joining_stage_time:
            db.session.query(candidates).filter(candidates.id == cand_id).update({
                'current_stage' : 'Candidate Joined', 
                'candidate_joined_date' : joining_stage_time, 
            })
            # cursor.execute("UPDATE candidates SET current_stage = 'Candidate Joined', candidate_joined_date = '"+ joining_stage_time +"' WHERE id= '"+ cand_id+"';")
        elif dropout_stage_time:
            db.session.query(candidates).filter(candidates.id == cand_id).update({
                'current_stage' : 'Candidate Dropout', 
                'candidate_dropout_date' : dropout_stage_time, 
                'candidate_dropout_reason' : dropout_reason,
            })
            # cursor.execute("UPDATE candidates SET current_stage = 'Candidate Dropout', candidate_dropout_date = '"+ dropout_stage_time +"',
            #  candidate_dropout_reason = '"+ dropout_reason+"' WHERE id= '"+ cand_id+"';")
        # con.commit()
        db.session.commit()
    return redirect(url_for('main'))

@app.route('/add-tsin', methods = ['GET', 'POST'])
def tsinform():
    # con=sqlite3.connect('db/data.db') #connecting to the database
    # cursor=con.cursor()   
    # cursor.execute('SELECT tsin_id from roles;')
    # result = cursor.fetchall()
    result = roles.query.with_entities(roles.tsin_id).all()
    final = []
    for i in result:
        final.append(i[0])
    return render_template('tsin_form.html', final = final)

@app.route('/detailed-view', methods = ['GET', 'POST'])
def detailed():
    tsin = request.form.get('val1')
    role = request.form.get('val2')
    chapter = request.form.get('val3')
    squad = request.form.get('val4')
    cname = request.form.get('val5')
    z = get_detailed_data()
    final = []
    for i in z:
        if tsin:
            if i['tsinid'].strip() == tsin.strip():
                if i not in final:
                    final.append(i)
        if role:
            if i['role'].strip() == role.strip():
                if i not in final:
                    final.append(i)
        if chapter:
            if i['chapter'].strip() == chapter.strip():
                if i not in final:
                    final.append(i)
        if squad:
            if i['squad'].strip() == squad.strip():
                if i not in final:
                    final.append(i)
        if cname:
            if i['candidate_name'].strip() == cname.strip():
                if i not in final:
                    final.append(i)
    if final == []:
        return render_template('detailed.html', final = z)
    else:
        return render_template('detailed.html', final = final)

@app.route('/delete-role/<tsin>', methods = ['GET', 'POST'])
def delete_role(tsin):
    # con=sqlite3.connect('db/data.db') #connecting to the database
    # cursor=con.cursor()
    # cursor.execute("DELETE from roles where tsin_id= '"+tsin+"' ;")
    # con.commit()
    db.sessionquery(roles).filter(roles.tsin_id == tsin).delete(synchronize_session = False)
    db.session.commit()
    return redirect(url_for('main'))

@app.route('/new-position', methods = ['GET', 'POST'])
def newposition():
    tsinid = request.form.get('tsinid')
    role = request.form.get('role')
    chapter = request.form.get('chapter')
    squad = request.form.get('squad')
    snow_id = request.form.get('snow_id')
    tribe = request.form.get('tribe')
    demandtype = request.form.get('demandtype')
    # con=sqlite3.connect('db/data.db') #connecting to the database
    # cursor=con.cursor()
    # cursor.execute('SELECT tsin_id, snow_id from roles;')
    # result = cursor.fetchall()
    result = roles.query.with_entities(roles.tsin_id, roles.snow_id).all()
    for i in result:
        if tsinid.strip() == i[0].strip():
            return "TSIN ID already exists"
        if snow_id:
            if snow_id.strip() == i[1].strip():
                return "SNOW ID already exists"
    
    # cursor.execute("INSERT INTO roles(tsin_id, role, chapter, squad, demand_type, Tribe, snow_id) VALUES ('"+tsinid+"','"+role+"','"+ 
    # chapter+"','"+ squad+"','"+ demandtype+"','"+ tribe+"','"+ snow_id+"');")
    # con.commit()
    db.session.add(roles(
        tsin_id = tsinid, 
        role = role, 
        chapter = chapter, 
        squad = squad,
        demand_type = demandtype, 
        tribe = tribe, 
        snow_id = snow_id
    ))
    db.session.commit()
    return redirect(url_for('main'))

@app.route('/add-new-profile', methods = ['GET', 'POST'])
def newprofile():
    tsin = request.form['tsin_id']
    phone = request.form['phone']
    name = request.form['name']
    email = request.form['email']
    pan = request.form['pan']
    company = request.form['company']
    experience = request.form['experience']
    location = request.form['location']
    resume = request.files['resume']
    # con=sqlite3.connect('db/data.db') #connecting to the database
    # cursor=con.cursor()
    # query='''INSERT INTO candidates (tsin_id, candidate_name, pan, candidate_email, current_stage, phone, current_location, 
    # current_company, experience) VALUES (' '''+tsin+''' ',' '''+ name+''' ',' ''' +pan+''' ',' '''+ email+''' ','Profile Added ',
    # ' '''+ phone+''' ',' '''+ location+''' ',' '''+ company+''' ',' '''+ experience+''' ');'''
    #print(query)
    # cursor.execute(query)
    # con.commit()
    db.session.add(candidates(
        tsin_id = tsin, 
        candidate_name = name, 
        pan = pan, 
        candidate_email = email, 
        current_stage = 'Profile Added ', 
        request_raised_date = "", 
        tsin_opened_date = "", 
        resume_screened_date = "", 
        l1_interview_date = "", 
        l1_interviewer = "", 
        l2_interview_date = "", 
        l2_interviewer = "", 
        l3_interview_date = "", 
        l3_interviewer = "", 
        offer_rollout_date = "", 
        joining_date = "", 
        buddy_assignment_date = "", 
        buddy_name = "", 
        candidate_dropout_date = "", 
        candidate_dropout_reason = "", 
        resume = "",
        resume_screened_remarks = "",
        l1_interview_result = "",
        l1_interview_remarks = "",
        l2_interview_remarks = "",
        l2_interview_result = "",
        l3_interview_result = "",
        l3_interview_remarks = "",
        phone = phone,
        current_location = location,
        current_company = company,
        experience = experience,
        candidate_joined_date = ""
    ))
    db.session.commit()

    if resume:
        resume.save('static/resume')
        client.fput_object("resume", "resume" + str(name), "static/resume")
        print(
            "resume is successfully uploaded as "
            "object 'resume" + str(name) + "' to bucket 'resume'."
        )
    return redirect(url_for('main'))   

@app.route('/apply-filter', methods = ['GET', 'POST'])
def apply_filter():
    tsin = request.form.get('val1')
    role = request.form.get('val2')
    chapter = request.form.get('val3')
    squad = request.form.get('val4')
    cname = request.form.get('val5')
    z = get_detailed_data()
    final = []
    for i in z:
        if tsin:
            if i['tsinid'].strip() == tsin.strip():
                if i not in final:
                    final.append(i)
        if role:
            if i['role'].strip() == role.strip():
                if i not in final:
                    final.append(i)
        if chapter:
            if i['chapter'].strip() == chapter.strip():
                if i not in final:
                    final.append(i)
        if squad:
            if i['squad'].strip() == squad.strip():
                if i not in final:
                    final.append(i)
        if cname:
            if i['candidate_name'].strip() == cname.strip():
                if i not in final:
                    final.append(i)
    return render_template('detailed.html', final = final)
if __name__ == '__main__':
    app.run()
