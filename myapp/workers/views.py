from myapp import db
from sqlalchemy import func
from datetime import date
from myapp.models import Worker, DailyPlan, SchedulePayment, Date, Payments
from myapp.workers.forms import AddWorker, UpdateWorker, PaymentFunc
from myapp.workers.picture_handler import add_profile_pic
from flask import render_template, redirect, url_for, Blueprint, flash, request

users = Blueprint("users", __name__)

@users.route("/worker/register", methods = ["GET", "POST"])
def register():
    '''Allows the registration of a new worker'''
    form = AddWorker()
    if form.validate_on_submit():
        new_worker = Worker(name = form.name.data,
                            surname = form.surname.data,
                            role = form.role.data,
                            phone = form.phone.data,
                            email = form.email.data)
        db.session.add(new_worker)
        db.session.commit()
        flash(f"Worker {new_worker.name} has been successfully registered!", category = "green")
        return redirect(url_for("core.index"))
    return render_template("register.html", form = form)

@users.route("/worker/<int:id>", methods = ["GET", "POST"])
def account(id):
    '''Updates the selected worker'''
    worker = Worker.query.get_or_404(id)
    form = UpdateWorker()
    if form.validate_on_submit():
        if form.picture.data:
            worker_name = worker.name
            pic = add_profile_pic(form.picture.data, worker_name)
            worker.profile_image = pic
        worker.name = form.name.data
        worker.surname = form.surname.data
        worker.role = form.role.data
        worker.phone = form.phone.data
        worker.email = form.email.data
        db.session.commit()
        flash(f"Worker {worker.name} has been successfully updated!", category = "green")
        return redirect(url_for("core.index"))
    elif request.method == "GET":
        form.name.data = worker.name
        form.surname.data = worker.surname
        form.role.data = worker.role
        form.phone.data = worker.phone
        form.email.data = worker.email
    return render_template("profile.html", form = form)

@users.route("/worker/list")
def list():
    workers_list = Worker.query.all()
    return render_template("list.html", list = workers_list)

@users.route("/worker/delete/<int:id>")
def delete(id):
    worker = Worker.query.get_or_404(id)
    db.session.delete(worker)
    db.session.commit()
    flash(f"Worker {worker.name} has been successfully deleted!", category = "green")
    return redirect(url_for("core.index"))

@users.route("/worker/<int:id>/payment/<int:month>/<int:year>", methods = ["GET", "POST"])
def manage_payment(id, month, year):
    # RECUPERA IL LAVORATORE DAL DATABASE
    monthly_pay = 0.0
    worker = db.session.execute(db.Select(Worker).where(Worker.id == id)).scalar()
    # STIMA LO STIPENDIO PER IL MESE CORRENTE, TENENDO PRESENTE CHE PUÒ ESSERCI STATO UN ACCONTO
    dates = db.session.execute(db.Select(Date.id).filter(db.and_(Date.month_number == month, Date.year == year))).scalars().all()
    plans = db.session.execute(db.Select(DailyPlan).filter(db.and_(DailyPlan.worker == worker, DailyPlan.has_been_paid == False))).scalars().all()
    plans_worked = [plan.schedule_id for plan in plans if plan.date_id in dates]
    for i in plans_worked:
        sum_pays = db.session.query(func.sum(SchedulePayment.pay)).filter(db.and_(SchedulePayment.worker_id == worker.id, SchedulePayment.schedule_id == i)).scalar()
        try:
            monthly_pay = monthly_pay + sum_pays
        except TypeError:
            pass
    form = PaymentFunc(monthly_pay)
    if request.method == "POST":
        if form.validate_on_submit():
            if monthly_pay == 0.0:
                # se non c'è niente da pagare, reindirizza con messaggio
                flash(f"No credit to pay for {worker.name}!", category = "yellow")
                return redirect(url_for("core.index"))
            # ridurre il credito del lavoratore e cambiare lo status dei turni in PAGATO (true)

            worker.credit = worker.credit - monthly_pay
            for plan in plans:
                plan.has_been_paid = True
            new_transaction = Payments(type = "Monthly pay", quantity = monthly_pay, date_id = date.today(), worker_id = worker.id)
            db.session.add(new_transaction)
            db.session.commit()
            flash(f"Transaction correctly executed for {worker.name}!", category = "green")
            return redirect(url_for("core.index"))
    return render_template("payment_manage.html", form = form)
      