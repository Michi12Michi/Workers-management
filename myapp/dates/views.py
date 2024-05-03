from flask import Blueprint, redirect, render_template, flash, url_for, request
import datetime as dt
from myapp import db
from myapp.models import Worker, Schedule, Date, DailyPlan, SchedulePayment
from myapp.dates.forms import AddSchedule, DynamicSchedule

dates = Blueprint("dates", __name__)

@dates.route("/dates/add/<date>")
def create_dates(date):
    ''' Creates dates for the current year '''
    end_date = dt.date(int(date), 12, 31).toordinal()
    for i in range(dt.date(int(date), 1, 1).toordinal(), end_date + 1):
        new_date = dt.date.fromordinal(i)
        date_obj = Date(fulldate = new_date)
        db.session.add(date_obj)
        db.session.commit()
    flash("A full-year date plan has been created successfully for you!", category = "green")
    return redirect(url_for("core.index"))

@dates.route("/schedule/add", methods = ["GET", "POST"])
def create_schedule():
    '''Creates a new schedule (name and hours)'''
    form = AddSchedule()
    if form.validate_on_submit():
        new_schedule = Schedule(name = form.name.data, hours = form.hours.data)
        db.session.add(new_schedule)
        db.session.commit()
        flash("A new schedule has been created successfully!", category = "green")
        return redirect(url_for("core.index"))
    return render_template("schedule_create.html", form = form)

@dates.route("/schedule/<int:id>", methods = ["GET", "POST"])
def schedule_update(id):
    '''Updates a selected schedule'''
    schedule = Schedule.query.get_or_404(id)
    form = AddSchedule()
    if form.validate_on_submit():
        schedule.name = form.name.data
        schedule.hours = form.hours.data
        db.session.commit()
        flash(f"Schedule {schedule.name} has been successfully updated!", category = "green")
        return redirect(url_for("core.index"))
    elif request.method == "GET":
        form.name.data = schedule.name
        form.hours.data = schedule.hours
    return render_template("schedule_create.html", form = form)

@dates.route("/schedule/list")
def list():
    '''Selects all schedules for their rendering'''
    schedule_list = Schedule.query.all()
    return render_template("schedule_list.html", list = schedule_list)

@dates.route("/schedule/delete/<int:id>")
def delete_schedule(id):
    '''Deletes the selected schedule (and all rows in DailyPlan containing it)'''
    schedule = Schedule.query.get_or_404(id)
    workers = db.session.execute(db.Select(Worker).order_by(Worker.id)).scalars().all()
    for worker in workers:
        turni_da_riaggiornare = DailyPlan.query.filter(db.and_(DailyPlan.worker == worker, DailyPlan.schedule == schedule, DailyPlan.has_been_paid == False)).count()
        pay = db.session.execute(db.Select(SchedulePayment.pay).where(db.and_(SchedulePayment.worker == worker, SchedulePayment.schedule == schedule))).scalar()
        try:
            worker.credit = worker.credit - turni_da_riaggiornare*pay
        except TypeError:
            pass
    db.session.delete(schedule)
    db.session.commit()
    flash(f'Schedule "{schedule.name}" ({schedule.hours} hours) has been successfully deleted!', category = "green")
    return redirect(url_for("core.index"))

@dates.route("/plan")
def a_plan():
    year = dt.date.today().year
    return redirect(url_for("dates.plan", year = year))

@dates.route("/plan/<int:year>")
def plan(year):
    page = request.args.get("page", 1, type = int)
    dates = db.session.execute(db.Select(Date).where(db.and_(Date.year == year, Date.month_number == page))).scalars().all()
    #finquiok
    all_workers = db.session.execute(db.Select(Worker).order_by(Worker.id)).scalars().all()
    all_workers_name = [worker.name for worker in all_workers]
    if not dates:
        return render_template("404.html")
    else:
        month_num = str(page)
        datetime_object = dt.datetime.strptime(month_num, "%m")
        full_month_name = datetime_object.strftime("%B")
        scheds = {}
        for worker in all_workers:
            scheds[worker.name] = []
            for d in dates:
                sched_id =  db.session.execute(db.Select(DailyPlan.schedule_id).where(db.and_(DailyPlan.date_id == d.id, DailyPlan.worker_id == worker.id))).scalar()
                if sched_id:
                    sched_name = db.session.execute(db.Select(Schedule).where(Schedule.id == sched_id)).scalar()

                    scheds[worker.name].append(str(sched_name.name))
                else:
                    scheds[worker.name].append("")
        return render_template("plan.html", dates = dates, month = full_month_name, year = year, workers = all_workers, scheds = scheds)

@dates.route("/plan/day/<int:id>", methods = ["GET", "POST"])
def manage_day(id):
    # lista nomi e id lavoratori
    workers = db.session.execute(db.Select(Worker).order_by(Worker.id)).scalars().all()
    current_date = db.session.execute(db.Select(Date).where(Date.id == id)).scalar()
    workers_names = [w.name for w in workers]
    workers_ids = [w.id for w in workers]
    n_workers = len(workers_names)
    # lista di turni
    schedules_name = db.session.execute(db.Select(Schedule.name).order_by(Schedule.id)).scalars().all()
    # renderizzo il form e associo i nomi dei lavoratori agli StringField e i loro id ai SelectField
    form = DynamicSchedule(n_workers, schedules_name)
    for i in range(n_workers):
        form.work_sche[i].worker.data = workers_names[i]
        form.work_sche[i].schedule.id = workers_ids[i]
    if request.method == "GET":
            for item in form.work_sche:
                sch = db.session.execute(db.Select(DailyPlan.schedule_id).where(db.and_(DailyPlan.date_id == id, DailyPlan.worker_id == item.schedule.id))).scalar()
                shift_name = db.session.execute(db.Select(Schedule.name).where(Schedule.id == sch)).scalar()
                item.schedule.data = shift_name

    if request.method == "POST":
        for item in form.work_sche:
            value = item.form.schedule.data
            current_worker = db.session.execute(db.Select(Worker).where(Worker.id == item.form.schedule.id)).scalar()
            selected_schedule = (db.session.execute(db.Select(Schedule).where(Schedule.name == str(value))).scalar())
            # È NECESSARIO PRIMA VERIFICARE SE I DATI C'ERANO GIÀ
            already_present = db.session.execute(db.Select(DailyPlan).where(db.and_(DailyPlan.date == current_date, DailyPlan.worker == current_worker))).scalar()
            if (already_present):
                # # ---- aggiornare il credito del dipendente, a meno che non sia stato già pagato questo turno
                # if (not already_present.has_been_paid):
                #     old_payment = db.session.execute(db.Select(SchedulePayment.pay).where(db.and_(SchedulePayment.worker_id == current_worker, SchedulePayment.schedule_id == already_present.schedule_id))).scalar()
                # # CERCARE LA TARIFFA DI QUESTO TURNO (se c'è)
                # if payment := db.session.execute(db.Select(SchedulePayment.pay).where(db.and_(SchedulePayment.schedule_id == selected_schedule, SchedulePayment.worker_id == current_worker))).scalar():
                #     pass
                # # DECURTARE DAL CREDITO E SOMMARE IL NUOVO IMPORTO
                already_present.schedule_id = str(selected_schedule.id)
            else:
                # aggiornare il credito del dipendente
                #
                new_plan = DailyPlan(date_id = current_date.id, worker_id = current_worker.id, schedule_id = selected_schedule.id)
                db.session.add(new_plan)
            db.session.commit()
        return redirect(url_for("dates.a_plan"))

    return render_template("plan_daily.html", form = form, sche = schedules_name, string = workers_names)
