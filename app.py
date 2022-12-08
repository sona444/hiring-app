from flask import Flask, render_template, request, redirect, url_for
from openpyxl import load_workbook
import sqlite3
import pandas as pd
from minio import Minio
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
load_dotenv()
app = Flask(__name__)
app["SQLALCHEMY_DATABASE_URI"]=""
db = SQLAlchemy(app)
migrate = Migrate(app, db)
from models import participants, team

client = Minio(
        "play.min.io",
        access_key="Q3AM3UQ867SPQQA43P2F",
        secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
    )
found = client.bucket_exists("resume")
if not found:
    client.make_bucket("resume")
else:
    print("Bucket 'resume' already exists")

app = Flask(__name__)

def get_abstract_data():
    con=sqlite3.connect('db/data.db') #connecting to the database
    cursor=con.cursor()
    
    cursor.execute('SELECT tsin_id, role, chapter, squad, demand_type, Tribe, snow_id from roles;')
    result = cursor.fetchall()
    nums={}
    for i in result:
        nums[i[0].strip()]={'stage1':0,'stage2':0,'stage3':0,'stage4':0,'stage5':0,'stage6':0,'stage7':0, 'stage8':0}
    print(nums)
    print(result)
    cursor.execute('SELECT tsin_id, candidate_name, pan, candidate_email, current_stage, request_raised_date, tsin_opened_date, resume_screened_date, l1_interview_date, l1_interviewer, l2_interview_date, l2_interviewer, l3_interview_date, l3_interviewer, offer_rollout_date, joining_date, buddy_assignment_date, buddy_name, candidate_dropout_date, candidate_dropout_reason, resume, id, phone, current_location, current_company, experience from candidates;')
    result2=cursor.fetchall()
    list_of_phone=[]
    for i in result2:
        list_of_phone.append(i[22])
    con.close()
    d={}
    for i in result2:
        if i[4].strip()=='Resume Screened for Interview':
            nums[i[0].strip()]['stage1']+=1
        elif i[4].strip()=='L1 Interview Complete':
            nums[i[0].strip()]['stage2']+=1
        elif i[4].strip()=='L2 Interview Complete':
            nums[i[0].strip()]['stage3']+=1
        elif i[4].strip()=='L3 Interview Complete':
            nums[i[0].strip()]['stage4']+=1
        elif i[4].strip()=='Offer RollOut':
            nums[i[0].strip()]['stage5']+=1
        elif i[4].strip()=='Buddy Assignment':
            nums[i[0].strip()]['stage6']+=1
        elif i[4].strip()=='Candidate Joined' or i[4].strip()=='Candidate Dropout':
            nums[i[0].strip()]['stage7']+=1
        elif i[4].strip()=='Resume Rejected':
            nums[i[0].strip()]['stage8']+=1
        if i[0] in d:
            d[i[0]].append({'id':i[21],'candidate_name':i[1], 'pan':i[2],'candidate_email':i[3], 'current_stage':i[4],'request_raised_date': i[5], 'tsin_opened_date':i[6], 'resume_screened_date':i[7], 'l1_interview_date':i[8], 'l1_interviewer':i[9], 'l2_interview_date':i[10], 'l2_interviewer':i[11], 'l3_interview_date':i[12], 'l3_interviewer':i[13], 'offer_rollout_date':i[14], 'joining_date':i[15], 'buddy_assignment_date':i[16], 'buddy_name':i[17], 'candidate_dropout_date':i[18], 'candidate_dropout_reason':i[19], 'resume':i[20], 'phone':i[22], 'current_location':i[23], 'current_company':i[24], 'experience':i[25]})
        else:
            d[i[0]]=[{'id':i[21],'candidate_name':i[1], 'pan':i[2],'candidate_email':i[3], 'current_stage':i[4],'request_raised_date': i[5], 'tsin_opened_date':i[6], 'resume_screened_date':i[7], 'l1_interview_date':i[8], 'l1_interviewer':i[9], 'l2_interview_date':i[10], 'l2_interviewer':i[11], 'l3_interview_date':i[12], 'l3_interviewer':i[13], 'offer_rollout_date':i[14], 'joining_date':i[15], 'buddy_assignment_date':i[16], 'buddy_name':i[17], 'candidate_dropout_date':i[18], 'candidate_dropout_reason':i[19], 'resume':i[20], 'phone':i[22], 'current_location':i[23], 'current_company':i[24], 'experience':i[25]}]
    print(d)
    print(nums)
    return result, d, nums, list_of_phone

def get_detailed_data():
    con=sqlite3.connect('db/data.db') #connecting to the database
    cursor=con.cursor()
    cursor.execute('SELECT tsin_id, role, chapter, squad, demand_type, Tribe, snow_id from roles;')
    result = cursor.fetchall()
    cursor.execute('SELECT tsin_id, candidate_name, pan, candidate_email, current_stage, request_raised_date, tsin_opened_date, resume_screened_date, l1_interview_date, l1_interviewer, l2_interview_date, l2_interviewer, l3_interview_date, l3_interviewer, offer_rollout_date, joining_date, buddy_assignment_date, buddy_name, candidate_dropout_date, candidate_dropout_reason, resume, id, phone, current_location, current_company, experience from candidates;')
    result2 = cursor.fetchall()
    roles={}
    for i in result:
        roles[i[0]]={"role":i[1], "chapter":i[2], "squad":i[3], "demand_type":i[4], "tribe":i[5], "snow_id":i[6]}
    d=[]
    for i in result2:
        d.append({'tsinid':i[0],'chapter':roles[i[0].strip()]['chapter'],'squad':roles[i[0].strip()]['squad'],'demand_type':roles[i[0].strip()]['demand_type'],'tribe':roles[i[0].strip()]['tribe'],'snow_id':roles[i[0].strip()]['snow_id'],'role':roles[i[0].strip()]['role'],'id':i[21],'candidate_name':i[1], 'pan':i[2],'candidate_email':i[3], 'current_stage':i[4],'request_raised_date': i[5], 'tsin_opened_date':i[6], 'resume_screened_date':i[7], 'l1_interview_date':i[8], 'l1_interviewer':i[9], 'l2_interview_date':i[10], 'l2_interviewer':i[11], 'l3_interview_date':i[12], 'l3_interviewer':i[13], 'offer_rollout_date':i[14], 'joining_date':i[15], 'buddy_assignment_date':i[16], 'buddy_name':i[17], 'candidate_dropout_date':i[18], 'candidate_dropout_reason':i[19], 'resume':i[20], 'phone':i[22], 'current_location':i[23], 'current_company':i[24], 'experience':i[25]})
        print(d)
    return d

@app.route('/')
def main():
    result, d,nums, phones=get_abstract_data()
    return render_template('candidates.html', roles=result, candidates=d, nums=nums, phones=phones)


@app.route('/upload-dataset', methods=['GET','POST'])
def uploadDs():
    f = request.files['file'] #File input
    if not f:
        return "No file attached"

    global filename
    filename=f.filename #changing global value of filename

    path='{}/{}'.format('static',filename)
    f.save(path)
    x=path.split('.')[-1]

    #reading filedata start
    if x=='xlsx':
        new_wb = load_workbook(path)
        Dataframe = pd.read_excel(new_wb,engine='openpyxl')
    elif x=='csv':
        Dataframe = pd.read_csv(path, encoding = "ISO-8859-1")
    else:
        return('Please upload the file in xlsx or csv only')
    #reading filedata end

    dict_of_records=Dataframe.to_dict(orient='record')
    
    con=sqlite3.connect('db/data.db') #connecting to the database
    cursor=con.cursor()
    for i in dict_of_records:
        cursor.execute("SELECT * from roles where tsin_id = '"+i['TSIN ID']+"';")
        existing_roles=cursor.fetchall()
        cursor.execute("SELECT candidate_email, tsin_id from candidates;")
        existing_emails=cursor.fetchall()
        if len(existing_roles)==0:
            cursor.execute("INSERT INTO roles(tsin_id, role, chapter, squad) VALUES ('"+i['TSIN ID']+"','"+i['Role ']+"','"+ i['Chapter']+"','"+ i['Squad']+"');")
            con.commit()
        z=[" "+i['Cadidate Email']+" ", " "+i['TSIN ID']+" "]
        if tuple(z) in existing_emails:
            print('yes')
            cursor.execute("UPDATE candidates SET tsin_id='"+i['TSIN ID']+"',candidate_name= '"+ i['Candidate Name ']+"',pan='" +i['PAN Number']+"',candidate_email='"+ i['Cadidate Email']+"',current_stage='"+ i['Current Stage ']+"',request_raised_date='" +str(i['Request Rasied '])+"' WHERE candidate_email = '"+i['Cadidate Email']+"' AND tsin_id= '"+ i['TSIN ID']+"';")
            con.commit()
        else:
            query='''INSERT INTO candidates (tsin_id, candidate_name, pan, candidate_email, current_stage, request_raised_date, tsin_opened_date, resume_screened_date, l1_interview_date, l1_interviewer, l2_interview_date, l2_interviewer, l3_interview_date, l3_interviewer, offer_rollout_date, joining_date, buddy_assignment_date, buddy_name, candidate_dropout_date, candidate_dropout_reason, resume) VALUES (' '''+i['TSIN ID']+''' ',' '''+ i['Candidate Name ']+''' ',' ''' +i['PAN Number']+''' ',' '''+ i['Cadidate Email']+''' ',' '''+ i['Current Stage ']+''' ',' ''' +str(i['Request Rasied '])+''' ',' '''+str(i['TSIN Opened'])+''' ',' '''+str(i['Resume Screened'])+''' ',' '''+str(i['L1 Interview Complete'])+''' ',' '''+str(i['L1 Interviewer'])+''' ',' '''+str(i['L2 Interview Complete'])+''' ',' '''+str(i['L2 interviewer'])+''' ',' '''+str(i['L3 Interview Complete'])+''' ',' '''+str(i['L3 Interviewer'])+''' ',' '''+str(i['Offer RollOut '])+''' ',' '''+str(i['Joining Date'])+''' ',' '''+str(i['Buddy Assignment '])+''' ',' '''+str(i['Buddy Name'])+''' ',' '''+str(i['Candidate Joined'])+''' ',' '''+str(i['Candidate Dropout'])+''' ',' '''+str(i['Dropout Reason'])+''' ');'''
            cursor.execute(query)
            con.commit()
    print('added to db')
    return redirect(url_for('main'))

@app.route('/upload-profile', methods=['GET','POST'])
def profileUpload():
    cand_id=request.form['candidate_id']
    phone=request.form['phone']
    company=request.form['company']
    experience=request.form['experience']
    location=request.form['location']
    resume=request.files['resume']
    con=sqlite3.connect('db/data.db') #connecting to the database
    cursor=con.cursor()
    cursor.execute("SELECT candidate_name from candidates where id = '"+ cand_id +"';")
    result2=cursor.fetchall()
    print(result2)
    if resume:
        resume.save('static/resume')
        client.fput_object(
            "resume", "resume"+str(result2[0][0]), "static/resume",
        )
        print(
            "resume is successfully uploaded as "
            "object 'resume"+str(result2[0][0])+"' to bucket 'resume'."
        )
    
    cursor.execute("UPDATE candidates SET phone = '"+ phone +"', current_location = '"+ location +"', current_company='"+ company +"', experience = '"+ experience +"' WHERE id= '"+ cand_id+"';")
    con.commit()    

    return redirect(url_for('main'))

@app.route('/download-resume', methods=['GET','POST'])
def downloadresume():
    id=request.form.get('id')
    z=client.get_object('resume', 'resume'+id)
    return z.data

@app.route('/upload-candidates', methods=['GET','POST'])
def candidates():
    return render_template('index.html')

@app.route('/update-stage', methods=['GET','POST'])
def updateStage():
    con=sqlite3.connect('db/data.db') #connecting to the database
    cursor=con.cursor()
    cand_id=request.form.get('candidate_id')
    stage=request.form.get('stage')
    update_time=request.form.get('stageupdatetime')
    result=request.form.get('result')
    l1_remarks=request.form.get('l1_remarks')
    l2_interviewer_name=request.form.get('l2_interviewer_name')
    l2_interview_date=request.form.get('l2_interview_date')
    l2_remarks=request.form.get('l2_remarks')
    l3_interviewer_name=request.form.get('l3_interviewer_name')
    l3_interview_date=request.form.get('l3_interview_date')
    l3_remarks=request.form.get('l3_remarks')
    joining_date=request.form.get('joining_date')
    buddy_name=request.form.get('buddy_name')
    joining_stage_time=request.form.get('joiningstageupdatetime')
    dropout_stage_time=request.form.get('dropoutstageupdatetime')
    dropout_reason=request.form.get('dropout_reason')
    if stage == 'l1complete':
        if result=='passed':
            cursor.execute("UPDATE candidates SET current_stage = 'L1 Interview Complete', l1_completion = '"+ update_time +"', l1_interview_result = '"+ result +"', l1_interview_remarks = '"+ l1_remarks +"', l2_interviewer='"+ l2_interviewer_name +"', l2_interview_date = '"+ l2_interview_date +"' WHERE id= '"+ cand_id+"';")
        else:
            cursor.execute("UPDATE candidates SET current_stage = 'Resume Rejected', l1_completion = '"+ update_time +"', l1_interview_result = '"+ result +"', l1_interview_remarks = '"+ l1_remarks +"';")
        con.commit()    
    elif stage == 'l2complete':
        if result=='passed':
            cursor.execute("UPDATE candidates SET current_stage = 'L2 Interview Complete', l2_completion = '"+ update_time +"',l2_interview_result = '"+ result +"', l2_interview_remarks = '"+ l2_remarks +"', l3_interviewer='"+ l3_interviewer_name +"', l3_interview_date = '"+ l3_interview_date +"' WHERE id= '"+ cand_id+"';")
        else:
            cursor.execute("UPDATE candidates SET current_stage = 'Resume Rejected', l2_completion = '"+ update_time +"', l2_interview_result = '"+ result +"', l2_interview_remarks = '"+ l2_remarks +"';")
        con.commit() 
    elif stage == 'l3complete':
        if result=='passed':
            cursor.execute("UPDATE candidates SET current_stage = 'L3 Interview Complete', l3_completion = '"+ update_time +"', l3_interview_result = '"+ result +"', l3_interview_remarks = '"+ l3_remarks +"' WHERE id= '"+ cand_id+"';")
        else:
            cursor.execute("UPDATE candidates SET current_stage = 'Resume Rejected', l3_completion = '"+ update_time +"', l3_interview_result = '"+ result +"', l3_interview_remarks = '"+ l3_remarks +"';")
        con.commit()
    elif stage == 'offer':
        cursor.execute("UPDATE candidates SET current_stage = 'Offer RollOut', offer_rollout_date = '"+ update_time +"', joining_date = '"+ joining_date +"' WHERE id= '"+ cand_id+"';")
        con.commit()
    elif stage == 'buddy':
        cursor.execute("UPDATE candidates SET current_stage = 'Buddy Assignment', buddy_assignment_date = '"+ update_time +"', buddy_name = '"+ buddy_name +"' WHERE id= '"+ cand_id+"';")
        con.commit()
    elif stage == 'finalcandidate':
        if joining_stage_time and dropout_stage_time:
            return "Please choose appropriate values - Joining and dropout cannot come together!"
        elif joining_stage_time:
            cursor.execute("UPDATE candidates SET current_stage = 'Candidate Joined', candidate_joined_date = '"+ joining_stage_time +"' WHERE id= '"+ cand_id+"';")
        elif dropout_stage_time:
            cursor.execute("UPDATE candidates SET current_stage = 'Candidate Dropout', candidate_dropout_date = '"+ dropout_stage_time +"', candidate_dropout_reason = '"+ dropout_reason+"' WHERE id= '"+ cand_id+"';")
        con.commit()
    return redirect(url_for('main'))

@app.route('/add-tsin', methods=['GET','POST'])
def tsinform():
    con=sqlite3.connect('db/data.db') #connecting to the database
    cursor=con.cursor()
    
    cursor.execute('SELECT tsin_id from roles;')
    result = cursor.fetchall()
    final=[]
    for i in result:
        final.append(i[0])
    return render_template('tsin_form.html', final=final)

@app.route('/detailed-view', methods=['GET','POST'])
def detailed():
    tsin=request.form.get('val1')
    role=request.form.get('val2')
    chapter=request.form.get('val3')
    squad=request.form.get('val4')
    cname=request.form.get('val5')
    z=get_detailed_data()
    final=[]
    for i in z:
        if tsin:
            if i['tsinid'].strip()==tsin.strip():
                if i not in final:
                    final.append(i)
        if role:
            if i['role'].strip()==role.strip():
                if i not in final:
                    final.append(i)
        if chapter:
            if i['chapter'].strip()==chapter.strip():
                if i not in final:
                    final.append(i)
        if squad:
            if i['squad'].strip()==squad.strip():
                if i not in final:
                    final.append(i)
        if cname:
            print(cname, i['candidate_name'])
            if i['candidate_name'].strip()==cname.strip():
                if i not in final:
                    final.append(i)
    if final==[]:
        return render_template('detailed.html', final=z)
    else:
        return render_template('detailed.html', final=final)

@app.route('/delete-role/<tsin>', methods=['GET','POST'])
def delete_role(tsin):
    con=sqlite3.connect('db/data.db') #connecting to the database
    cursor=con.cursor()
    cursor.execute("DELETE from roles where tsin_id= '"+tsin+"' ;")
    con.commit()
    return redirect(url_for('main'))

@app.route('/new-position', methods=['GET','POST'])
def newposition():
    tsinid=request.form.get('tsinid')
    role=request.form.get('role')
    chapter=request.form.get('chapter')
    squad=request.form.get('squad')
    snow_id=request.form.get('snow_id')
    tribe=request.form.get('tribe')
    demandtype=request.form.get('demandtype')
    con=sqlite3.connect('db/data.db') #connecting to the database
    cursor=con.cursor()
    
    cursor.execute('SELECT tsin_id, snow_id from roles;')
    result = cursor.fetchall()
    for i in result:
        print(i[0])
        if tsinid.strip()==i[0].strip():
            return "TSIN ID already exists"
        if snow_id:
            if snow_id.strip()==i[1].strip():
                return "SNOW ID already exists"
    cursor.execute("INSERT INTO roles(tsin_id, role, chapter, squad, demand_type, Tribe, snow_id) VALUES ('"+tsinid+"','"+role+"','"+ chapter+"','"+ squad+"','"+ demandtype+"','"+ tribe+"','"+ snow_id+"');")
    con.commit()
    return redirect(url_for('main'))

@app.route('/add-new-profile',methods=['GET','POST'])
def newprofile():
    tsin=request.form['tsin_id']
    phone=request.form['phone']
    name=request.form['name']
    email=request.form['email']
    pan=request.form['pan']
    company=request.form['company']
    experience=request.form['experience']
    location=request.form['location']
    resume=request.files['resume']
    con=sqlite3.connect('db/data.db') #connecting to the database
    cursor=con.cursor()
    query='''INSERT INTO candidates (tsin_id, candidate_name, pan, candidate_email, current_stage, phone, current_location, current_company, experience) VALUES (' '''+tsin+''' ',' '''+ name+''' ',' ''' +pan+''' ',' '''+ email+''' ','Profile Added ',' '''+ phone+''' ',' '''+ location+''' ',' '''+ company+''' ',' '''+ experience+''' ');'''
    print(query)
    cursor.execute(query)
    con.commit()
    
    if resume:
        resume.save('static/resume')
        client.fput_object(
            "resume", "resume"+str(name), "static/resume",
        )
        print(
            "resume is successfully uploaded as "
            "object 'resume"+str(name)+"' to bucket 'resume'."
        )
    return redirect(url_for('main'))   

@app.route('/apply-filter', methods=['GET','POST'])
def apply_filter():
    tsin=request.form.get('val1')
    role=request.form.get('val2')
    chapter=request.form.get('val3')
    squad=request.form.get('val4')
    cname=request.form.get('val5')
    z=get_detailed_data()
    final=[]
    for i in z:
        if tsin:
            if i['tsinid'].strip()==tsin.strip():
                if i not in final:
                    final.append(i)
        if role:
            if i['role'].strip()==role.strip():
                if i not in final:
                    final.append(i)
        if chapter:
            if i['chapter'].strip()==chapter.strip():
                if i not in final:
                    final.append(i)
        if squad:
            if i['squad'].strip()==squad.strip():
                if i not in final:
                    final.append(i)
        if cname:
            if i['candidate_name'].strip()==cname.strip():
                if i not in final:
                    final.append(i)
    return render_template('detailed.html', final=final)
if __name__ == '__main__':
    app.run()
