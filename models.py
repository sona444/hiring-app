from app import db

class candidates(db.Model):
    __tablename__="candidates"
    id=db.Column(db.Integer,primary_key=True)
    tsin_id=db.Column(db.String,nullable=False)
    candidate_name=db.Column(db.String,nullable=False)
    candidate_email=db.Column(db.String,nullable=False)
    current_stage=db.Column(db.String,nullable=False)
    pan=db.Column(db.String,nullable=True)
    request_raised_date=db.Column(db.String,nullable=True)
    tsin_opened_date=db.Column(db.String,nullable=True)
    resume_screened_date=db.Column(db.String,nullable=True)
    l1_interview_date=db.Column(db.String,nullable=True)
    l1_interviewer=db.Column(db.String,nullable=True)
    l1_interview_result=db.Column(db.String,nullable=True)
    l1_interview_remarks=db.Column(db.String,nullable=True)
    l2_interview_date=db.Column(db.String,nullable=True)
    l2_interviewer=db.Column(db.String,nullable=True)
    l2_interview_result=db.Column(db.String,nullable=True)
    l2_interview_remarks=db.Column(db.String,nullable=True)
    l3_interview_date=db.Column(db.String,nullable=True)
    l3_interviewer=db.Column(db.String,nullable=True)
    l3_interview_result=db.Column(db.String,nullable=True)
    l3_interview_remarks=db.Column(db.String,nullable=True)
    offer_rollout_date=db.Column(db.String,nullable=True)
    joining_date=db.Column(db.String,nullable=True)
    buddy_assignment_date=db.Column(db.String,nullable=True)
    buddy_name=db.Column(db.String,nullable=True)
    candidate_dropout_date=db.Column(db.String,nullable=True)
    candidate_dropout_reason=db.Column(db.String,nullable=True)
    resume=db.Column(db.String,nullable=True)
    phone=db.Column(db.String,nullable=True)
    current_location=db.Column(db.String,nullable=True)
    current_company=db.Column(db.String,nullable=True)
    experience=db.Column(db.String,nullable=True)
    candidate_joined_date=db.Column(db.String,nullable=True)
    
    def __init__(self,tsin_id, candidate_name, candidate_email, current_stage, pan, request_raised_date, tsin_opened_date, resume_screened_date, resume_screened_remarks, l1_interview_date, l1_interviewer, l1_interview_result, l1_interview_remarks, l2_interview_date, l2_interviewer, l2_interview_remarks, l2_interview_result, l3_interview_date, l3_interviewer, l3_interview_result, l3_interview_remarks, offer_rollout_date, joining_date, buddy_assignment_date, buddy_name, candidate_dropout_date, candidate_dropout_reason, resume, phone, current_location, current_company, experience, candidate_joined_date):
        self.tsin_id=tsin_id
        self.candidate_name=candidate_name
        self.candidate_email=candidate_email
        self.current_stage=current_stage
        self.pan=pan
        self.request_raised_date=request_raised_date
        self.tsin_opened_date=tsin_opened_date
        self.resume_screened_date=resume_screened_date
        self.resume_screened_remarks=resume_screened_remarks
        self.l1_interview_date=l1_interview_date
        self.l1_interviewer=l1_interviewer
        self.l1_interview_result=l1_interview_result
        self.l1_interview_remarks=l1_interview_remarks
        self.l2_interview_date=l2_interview_date
        self.l2_interviewer=l2_interviewer
        self.l2_interview_result=l2_interview_result
        self.l2_interview_remarks=l2_interview_remarks
        self.l3_interview_date=l3_interview_date
        self.l3_interviewer=l3_interviewer
        self.l3_interview_result=l3_interview_result
        self.l3_interview_remarks=l3_interview_remarks
        self.offer_rollout_date=offer_rollout_date
        self.joining_date=joining_date
        self.buddy_assignment_date=buddy_assignment_date
        self.buddy_name=buddy_name
        self.candidate_dropout_date=candidate_dropout_date
        self.candidate_dropout_reason=candidate_dropout_reason
        self.resume=resume
        self.phone=phone
        self.current_location=current_location
        self.current_company=current_company
        self.experience=experience
        self.candidate_joined_date=candidate_joined_date

class roles(db.Model):
    __tablename__="roles"
    tsin_id=db.Column(db.String, primary_key=True) 
    Role=db.Column(db.String, nullable=False)
    Chapter=db.Column(db.String, nullable=False)
    Squad=db.Column(db.String, nullable=False)
    demand_type=db.Column(db.String, nullable=True)
    Tribe=db.Column(db.String, nullable=True)
    snow_id=db.Column(db.String, nullable=True)
    

    def __init__(self, tsin_id, role, chapter, squad, demand_type, tribe, snow_id):
        self.tsin_id=tsin_id
        self.role=role
        self.chapter=chapter
        self.squad=squad
        self.demand_type=demand_type
        self.Tribe=tribe
        self.snow_id=snow_id