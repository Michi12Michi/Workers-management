from myapp import db
from datetime import date

class Worker(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), nullable = False)
    surname = db.Column(db.String(64), nullable = False)
    role = db.Column(db.String(32), nullable = True)
    phone = db.Column(db.String(32), nullable = True)
    email = db.Column(db.String(64), nullable = True)
    credit = db.Column(db.Float)
    profile_image = db.Column(db.String(64), default = "default_profile.png")
    plan = db.relationship('DailyPlan', backref = 'worker', cascade = "all,delete", lazy = True)
    schedule_payments = db.relationship('SchedulePayment', backref = 'worker', cascade = "all,delete", lazy = True)
    payments = db.relationship('Payments', backref = 'worker', cascade = "all,delete", lazy = True)

    def __init__(self, name, surname, **kwargs):
        self.name = name
        self.surname = surname
        self.role = kwargs.get("role")
        self.phone = kwargs.get("phone")
        self.email = kwargs.get("email")
        self.credit = 0.0
        self.picture = kwargs.get("picture")

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32), unique = True)
    hours = db.Column(db.Integer, default = 0)
    plan = db.relationship('DailyPlan', backref = 'schedule', cascade = "all,delete", lazy = True)
    schedule_payments = db.relationship('SchedulePayment', backref = 'schedule', cascade = "all,delete", lazy = True)

    def __init__(self, name, **kwargs):
        self.name = name
        self.hours = kwargs.get("hours")

class Date(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    fulldate = db.Column(db.Date, unique = True, nullable = False)
    year = db.Column(db.Integer)
    day_of_week = db.Column(db.String(32))
    is_red = db.Column(db.Boolean)
    month_number = db.Column(db.Integer)
    month_name = db.Column(db.String(32))
    plan = db.relationship('DailyPlan', backref='date', cascade = "all,delete", lazy = True)
    payments = db.relationship('Payments', backref = 'date', cascade = "all,delete", lazy = True)

    def __init__(self, fulldate):
        self.fulldate = fulldate
        self.year = fulldate.year
        self.day_of_week = fulldate.strftime("%A")
        self.month_number = fulldate.month
        self.month_name = fulldate.strftime("%B")
        self.is_red = self.is_red_day(fulldate)

    def is_red_day(self, fulldate):
        ''' Sadly, Italy has many, sparse (HARDCODED) non-working days. '''
        days_list = [date(fulldate.year, 1, 1),
                    date(fulldate.year, 1, 6),
                    date(fulldate.year, 4, 25),
                    date(fulldate.year, 5, 1),
                    date(fulldate.year, 6, 2),
                    date(fulldate.year, 8, 15),
                    date(fulldate.year, 11, 1),
                    date(fulldate.year, 12, 8),
                    date(fulldate.year, 12, 25),
                    date(fulldate.year, 12, 26)]
        easter = self.calc_easter(fulldate.year)
        days_list.append(easter)
        post_easter = date.fromordinal(date.toordinal(easter) + 1)
        days_list.append(post_easter)
        red = False
        if fulldate in days_list or fulldate.weekday() == 6:
            red = True
        return red

    def calc_easter(self, year):
        '''Returns Easter as a date object.'''
        a = year % 19
        b = year // 100
        c = year % 100
        d = (19 * a + b - b // 4 - ((b - (b + 8) // 25 + 1) // 3) + 15) % 30
        e = (32 + 2 * (b % 4) + 2 * (c // 4) - d - (c % 4)) % 7
        f = d + e - 7 * ((a + 11 * d + 22 * e) // 451) + 114
        month = f // 31
        day = f % 31 + 1
        return date(year, month, day)

class DailyPlan(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    has_been_paid = db.Column(db.Boolean, default = False)
    date_id = db.Column(db.Integer, db.ForeignKey('date.id'), nullable = False)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker.id'), nullable = False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable = False)

    def __init__(self, date_id, worker_id, schedule_id):
        self.date_id = date_id
        self.worker_id = worker_id
        self.schedule_id = schedule_id

class SchedulePayment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable = False)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker.id'), nullable = False)
    pay = db.Column(db.Integer, nullable = True)

    def __init__(self, schedule_id, worker_id, pay):
        self.schedule_id = schedule_id
        self.worker_id = worker_id
        self.pay = pay

class Payments(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.String(32), nullable = False)
    quantity = db.Column(db.Float, nullable = True)
    date_id = db.Column(db.Date, db.ForeignKey('date.id'), nullable = False)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker.id'), nullable = False)