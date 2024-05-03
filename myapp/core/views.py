from flask import render_template, redirect, url_for, Blueprint, flash, request
from myapp import db
from myapp.models import DailyPlan, Worker, Schedule, Date, SchedulePayment, Payments
from .forms import PaymentsF
import datetime as dt

core = Blueprint("core", __name__)

@core.route("/", methods = ["GET", "POST"])
def index():
    ''' Current date evaluation '''
    current_date = dt.date.today()
    # date = current_date.strftime("%A, %d %B %Y"), 
    ''' Workers, schedules, dates number and last item's date evaluation '''
    workers = db.session.execute(db.Select(Worker).order_by(Worker.id)).scalars().all()
    # worker_id_list = [worker.id for worker in workers]
    schedules = db.session.execute(db.Select(Schedule).order_by(Schedule.id)).scalars().all()
    # schedules_id_list = [schedule.id for schedule in schedules]
    any_worker = len(workers)
    any_schedule = len(schedules)
    form = PaymentsF(any_worker, any_schedule)
    if request.method == "GET":
        if (any_schedule and any_worker):
            for i in range(any_worker):
                for j in range(any_schedule):
                    pay = db.session.execute(db.Select(SchedulePayment.pay).where(db.and_(SchedulePayment.worker == workers[i], SchedulePayment.schedule == schedules[j]))).scalar()
                    if pay:
                        form.field[i].payment[j].payment.data = pay
                    else:
                        form.field[i].payment[j].payment.data = 0
        else:
            form = None
        schedule_count = []
        for worker in workers:
            schedule_count_list = []
            for schedule in schedules:
                cnt = DailyPlan.query.filter(db.and_(DailyPlan.worker == worker, DailyPlan.schedule == schedule)).count()
                schedule_count_list.append(cnt)
            schedule_count.append({worker.name: schedule_count_list})
        any_date = len(db.session.execute(db.Select(Date).order_by(Date.id)).scalars().all())
        last_year = db.session.execute(db.Select(Date).order_by(Date.id.desc())).scalar()
        ''' Dates controls '''
        ''' Is any date present in DB? Which year the date refers to? '''
        if (not any_date):
            flash("Maybe this is your first run... There aren't any defined dates. Please, wait.", category = "red")
            return redirect(url_for("dates.create_dates", date = current_date.year))
        elif (any_date and current_date.year > last_year.year):
            flash("A year has passed... Please, wait for the adjournment of the database.", category = "red")
            return redirect(url_for("dates.create_dates", date = current_date.year))
        if (not any_worker):
            flash("Hmm... It seems you have no workers to manage...", category = "yellow")
        if (not any_schedule):
            flash("Hmm... It seems you have not defined any schedule...", category = "yellow")
        return render_template("index.html", num_worker = any_worker, schedules = schedules, any_schedule = any_schedule, schedule_count = schedule_count, form = form)   
    
    if request.method == "POST":
        # workers_post = db.session.execute(db.Select(Worker).order_by(Worker.id)).scalars().all()
        # schedules_post = db.session.execute(db.Select(Schedule).order_by(Schedule.id)).scalars().all()
        for i in range(len(workers)):
            workers[i].credit = 0.0
            for j in range(len(schedules)):
                pay = form.field[i].payment[j].payment.data
                #verifica se ci sono turni per questo lavoratore ancora da pagare e quanti
                turni_da_riaggiornare = DailyPlan.query.filter(db.and_(DailyPlan.worker == workers[i], DailyPlan.schedule == schedules[j], DailyPlan.has_been_paid == False)).count()
                already = db.session.execute(db.Select(SchedulePayment).where(db.and_(SchedulePayment.worker == workers[i], SchedulePayment.schedule == schedules[j]))).scalar()
                if already and already == pay:
                    pass
                elif already and not (already == pay):
                    already.pay = pay
                else:
                    new_pay = SchedulePayment(schedule_id = schedules[j].id, worker_id = workers[i].id, pay = pay)
                    db.session.add(new_pay)
                workers[i].credit = workers[i].credit + turni_da_riaggiornare*pay
            db.session.commit()
        return redirect(url_for("core.index"))       

@core.route("/payments-list")
def payments_list():
    payments = db.session.execute(db.Select(Payments).order_by(Payments.id.desc())).scalars().all()
    return render_template("payments_list.html", list = payments)

@core.route("/info")
def info():
    ''' Info page '''
    return render_template("info.html")
