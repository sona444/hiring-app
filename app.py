from flask import Flask, render_template, request
from openpyxl import load_workbook
import sqlite3
import pandas as pd
from minio import Minio

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

@app.route('/')
def hello_world():
    con=sqlite3.connect('db/data.db') #connecting to the database
    cursor=con.cursor()
    
    cursor.execute('SELECT tsin_id, role, chapter, squad from roles;')
    result = cursor.fetchall()
    nums={}
    for i in result:
        nums[i[0]]={'stage1':0,'stage2':0,'stage3':0,'stage4':0,'stage5':0,'stage6':0,'stage7':0}
    print(nums)
    print(result)
    cursor.execute('SELECT tsin_id, candidate_name, pan, candidate_email, current_stage, request_raised_date, tsin_opened_date, resume_screened_date, l1_interview_date, l1_interviewer, l2_interview_date, l2_interviewer, l3_interview_date, l3_interviewer, offer_rollout_date, joining_date, buddy_assignment_date, buddy_name, candidate_dropout_date, candidate_dropout_reason, resume, id, phone, current_location, current_company, experience from candidates;')
    result2=cursor.fetchall()
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
        if i[0] in d:
            d[i[0]].append({'id':i[21],'candidate_name':i[1], 'pan':i[2],'candidate_email':i[3], 'current_stage':i[4],'request_raised_date': i[5], 'tsin_opened_date':i[6], 'resume_screened_date':i[7], 'l1_interview_date':i[8], 'l1_interviewer':i[9], 'l2_interview_date':i[10], 'l2_interviewer':i[11], 'l3_interview_date':i[12], 'l3_interviewer':i[13], 'offer_rollout_date':i[14], 'joining_date':i[15], 'buddy_assignment_date':i[16], 'buddy_name':i[17], 'candidate_dropout_date':i[18], 'candidate_dropout_reason':i[19], 'resume':i[20], 'phone':i[22], 'current_location':i[23], 'current_company':i[24], 'experience':i[25]})
        else:
            d[i[0]]=[{'id':i[21],'candidate_name':i[1], 'pan':i[2],'candidate_email':i[3], 'current_stage':i[4],'request_raised_date': i[5], 'tsin_opened_date':i[6], 'resume_screened_date':i[7], 'l1_interview_date':i[8], 'l1_interviewer':i[9], 'l2_interview_date':i[10], 'l2_interviewer':i[11], 'l3_interview_date':i[12], 'l3_interviewer':i[13], 'offer_rollout_date':i[14], 'joining_date':i[15], 'buddy_assignment_date':i[16], 'buddy_name':i[17], 'candidate_dropout_date':i[18], 'candidate_dropout_reason':i[19], 'resume':i[20], 'phone':i[22], 'current_location':i[23], 'current_company':i[24], 'experience':i[25]}]
    print(d)
    print(nums)
    return render_template('candidates.html', roles=result, candidates=d, nums=nums)


@app.route('/upload-dataset', methods=['GET','POST'])
def main():
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
    cursor.execute('SELECT tsin_id, role, chapter, squad from roles;')
    result = cursor.fetchall()
    print(result)

    nums={}
    for i in result:
        nums[i[0]]={'stage1':0,'stage2':0,'stage3':0,'stage4':0,'stage5':0,'stage6':0,'stage7':0}
    cursor.execute('SELECT tsin_id, candidate_name, pan, candidate_email, current_stage, request_raised_date, tsin_opened_date, resume_screened_date, l1_interview_date, l1_interviewer, l2_interview_date, l2_interviewer, l3_interview_date, l3_interviewer, offer_rollout_date, joining_date, buddy_assignment_date, buddy_name, candidate_dropout_date, candidate_dropout_reason, resume, id, phone, current_location, current_company, experience from candidates;')
    result2=cursor.fetchall()
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
        if i[0] in d:
            d[i[0]].append({'id':i[21],'candidate_name':i[1], 'pan':i[2],'candidate_email':i[3], 'current_stage':i[4],'request_raised_date': i[5], 'tsin_opened_date':i[6], 'resume_screened_date':i[7], 'l1_interview_date':i[8], 'l1_interviewer':i[9], 'l2_interview_date':i[10], 'l2_interviewer':i[11], 'l3_interview_date':i[12], 'l3_interviewer':i[13], 'offer_rollout_date':i[14], 'joining_date':i[15], 'buddy_assignment_date':i[16], 'buddy_name':i[17], 'candidate_dropout_date':i[18], 'candidate_dropout_reason':i[19], 'resume':i[20], 'phone':i[22], 'current_location':i[23], 'current_company':i[24], 'experience':i[25]})
        else:
            d[i[0]]=[{'id':i[21],'candidate_name':i[1], 'pan':i[2],'candidate_email':i[3], 'current_stage':i[4],'request_raised_date': i[5], 'tsin_opened_date':i[6], 'resume_screened_date':i[7], 'l1_interview_date':i[8], 'l1_interviewer':i[9], 'l2_interview_date':i[10], 'l2_interviewer':i[11], 'l3_interview_date':i[12], 'l3_interviewer':i[13], 'offer_rollout_date':i[14], 'joining_date':i[15], 'buddy_assignment_date':i[16], 'buddy_name':i[17], 'candidate_dropout_date':i[18], 'candidate_dropout_reason':i[19], 'resume':i[20], 'phone':i[22], 'current_location':i[23], 'current_company':i[24], 'experience':i[25]}]
    print(d)
    return render_template('candidates.html', roles=result, candidates=d, nums=nums)

@app.route('/upload-profile', methods=['GET','POST'])
def profileUpload():
    cand_id=request.form['candidate_id']
    phone=request.form['phone']
    company=request.form['company']
    experience=request.form['experience']
    location=request.form['location']
    resume=request.files['resume']
    if resume:
        resume.save('static/resume')
        client.fput_object(
            "resume", "resume"+str(cand_id), "static/resume",
        )
        print(
            "resume is successfully uploaded as "
            "object 'resume"+str(cand_id)+"' to bucket 'resume'."
        )
    con=sqlite3.connect('db/data.db') #connecting to the database
    cursor=con.cursor()
    cursor.execute("UPDATE candidates SET phone = '"+ phone +"', current_location = '"+ location +"', current_company='"+ company +"', experience = '"+ experience +"' WHERE id= '"+ cand_id+"';")
    con.commit()    

    cursor.execute('SELECT tsin_id, role, chapter, squad from roles;')
    result = cursor.fetchall()
    nums={}
    for i in result:
        nums[i[0]]={'stage1':0,'stage2':0,'stage3':0,'stage4':0,'stage5':0,'stage6':0,'stage7':0}
    print(nums)
    print(result)
    cursor.execute('SELECT tsin_id, candidate_name, pan, candidate_email, current_stage, request_raised_date, tsin_opened_date, resume_screened_date, l1_interview_date, l1_interviewer, l2_interview_date, l2_interviewer, l3_interview_date, l3_interviewer, offer_rollout_date, joining_date, buddy_assignment_date, buddy_name, candidate_dropout_date, candidate_dropout_reason, resume, id, phone, current_location, current_company, experience from candidates;')
    result2=cursor.fetchall()
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
        if i[0] in d:
            d[i[0]].append({'id':i[21],'candidate_name':i[1], 'pan':i[2],'candidate_email':i[3], 'current_stage':i[4],'request_raised_date': i[5], 'tsin_opened_date':i[6], 'resume_screened_date':i[7], 'l1_interview_date':i[8], 'l1_interviewer':i[9], 'l2_interview_date':i[10], 'l2_interviewer':i[11], 'l3_interview_date':i[12], 'l3_interviewer':i[13], 'offer_rollout_date':i[14], 'joining_date':i[15], 'buddy_assignment_date':i[16], 'buddy_name':i[17], 'candidate_dropout_date':i[18], 'candidate_dropout_reason':i[19], 'resume':i[20], 'phone':i[22], 'current_location':i[23], 'current_company':i[24], 'experience':i[25]})
        else:
            d[i[0]]=[{'id':i[21],'candidate_name':i[1], 'pan':i[2],'candidate_email':i[3], 'current_stage':i[4],'request_raised_date': i[5], 'tsin_opened_date':i[6], 'resume_screened_date':i[7], 'l1_interview_date':i[8], 'l1_interviewer':i[9], 'l2_interview_date':i[10], 'l2_interviewer':i[11], 'l3_interview_date':i[12], 'l3_interviewer':i[13], 'offer_rollout_date':i[14], 'joining_date':i[15], 'buddy_assignment_date':i[16], 'buddy_name':i[17], 'candidate_dropout_date':i[18], 'candidate_dropout_reason':i[19], 'resume':i[20], 'phone':i[22], 'current_location':i[23], 'current_company':i[24], 'experience':i[25]}]
    print(d)
    print(nums)
    return render_template('candidates.html', roles=result, candidates=d, nums=nums)

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
    con=sqlite3.connect('data.db') #connecting to the database
    cursor=con.cursor()
    cand_id=request.form['candidate_id']
    stage=request.form['stage']
    update_time=request.form['stageupdatetime']
    result=request.form['result']
    l1_remarks=request.form['l1_remarks']
    l2_interviewer_name=request.form['l2_interviewer_name']
    l2_interview_date=request.form['l2_interview_date']
    l2_remarks=request.form['l2_remarks']
    l3_interviewer_name=request.form['l3_interviewer_name']
    l3_interview_date=request.form['l3_interview_date']
    l3_remarks=request.form['l3_remarks']
    joining_date=request.form['joining_date']
    buddy_name=request.form['buddy_name']
    joining_stage_time=request.form['joiningstageupdatetime']
    dropout_stage_time=request.form['dropoutstageupdatetime']
    dropout_reason=request.form['dropout_reason']
    if stage == 'l1complete':
        cursor.execute("UPDATE candidates SET l1_interview_result = '"+ result +"', l1_interview_remarks = '"+ l1_remarks +"', l2_interviewer_name='"+ l2_interviewer_name +"', l2_interview_date = '"+ l2_interview_date +"' WHERE id= '"+ cand_id+"';")
        con.commit()    
    elif stage == 'l2complete':
        cursor.execute("UPDATE candidates SET l2_interview_result = '"+ result +"', l2_interview_remarks = '"+ l2_remarks +"', l3_interviewer_name='"+ l3_interviewer_name +"', l3_interview_date = '"+ l3_interview_date +"' WHERE id= '"+ cand_id+"';")
        con.commit() 

@app.route('/add-tsin', methods=['GET','POST'])
def tsinform():
    return render_template('tsin_form.html')

@app.route('/new-position', methods=['GET','POST'])
def newposition():
    tsinid=request.form['tsinid']
    role=request.form['role']
    chapter=request.form['chapter']
    squad=request.form['squad']
    con=sqlite3.connect('db/data.db') #connecting to the database
    cursor=con.cursor()
    
    cursor.execute('SELECT tsin_id from roles;')
    result = cursor.fetchall()
    for i in result:
        if tsinid.strip()==i[0].strip():
            return "TSIN ID already exists"
    cursor.execute("INSERT INTO roles(tsin_id, role, chapter, squad) VALUES ('"+tsinid+"','"+role+"','"+ chapter+"','"+ squad+"');")
    con.commit()
    cursor.execute('SELECT tsin_id, role, chapter, squad from roles;')
    result = cursor.fetchall()
    nums={}
    for i in result:
        nums[i[0]]={'stage1':0,'stage2':0,'stage3':0,'stage4':0,'stage5':0,'stage6':0,'stage7':0}
    print(nums)
    print(result)
    cursor.execute('SELECT tsin_id, candidate_name, pan, candidate_email, current_stage, request_raised_date, tsin_opened_date, resume_screened_date, l1_interview_date, l1_interviewer, l2_interview_date, l2_interviewer, l3_interview_date, l3_interviewer, offer_rollout_date, joining_date, buddy_assignment_date, buddy_name, candidate_dropout_date, candidate_dropout_reason, resume, id, phone, current_location, current_company, experience from candidates;')
    result2=cursor.fetchall()
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
        if i[0] in d:
            d[i[0]].append({'id':i[21],'candidate_name':i[1], 'pan':i[2],'candidate_email':i[3], 'current_stage':i[4],'request_raised_date': i[5], 'tsin_opened_date':i[6], 'resume_screened_date':i[7], 'l1_interview_date':i[8], 'l1_interviewer':i[9], 'l2_interview_date':i[10], 'l2_interviewer':i[11], 'l3_interview_date':i[12], 'l3_interviewer':i[13], 'offer_rollout_date':i[14], 'joining_date':i[15], 'buddy_assignment_date':i[16], 'buddy_name':i[17], 'candidate_dropout_date':i[18], 'candidate_dropout_reason':i[19], 'resume':i[20], 'phone':i[22], 'current_location':i[23], 'current_company':i[24], 'experience':i[25]})
        else:
            d[i[0]]=[{'id':i[21],'candidate_name':i[1], 'pan':i[2],'candidate_email':i[3], 'current_stage':i[4],'request_raised_date': i[5], 'tsin_opened_date':i[6], 'resume_screened_date':i[7], 'l1_interview_date':i[8], 'l1_interviewer':i[9], 'l2_interview_date':i[10], 'l2_interviewer':i[11], 'l3_interview_date':i[12], 'l3_interviewer':i[13], 'offer_rollout_date':i[14], 'joining_date':i[15], 'buddy_assignment_date':i[16], 'buddy_name':i[17], 'candidate_dropout_date':i[18], 'candidate_dropout_reason':i[19], 'resume':i[20], 'phone':i[22], 'current_location':i[23], 'current_company':i[24], 'experience':i[25]}]
    print(d)
    print(nums)
    return render_template('candidates.html', roles=result, candidates=d, nums=nums)


if __name__ == '__main__':
    app.run()
