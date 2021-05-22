from flask import Flask, render_template
import accounding

app = Flask(__name__)

titles_revenue = ['Распределение суммы продаж по когортам в абсолютном выражении (тыс.усл.ед.)',
                 'Распределение суммы продаж по когортам в относительном выражении (к первому месяцу)']


@app.route('/')
@app.route('/cohort_amount')
def cohort_revenue():
    return render_template('cohort_revenue.html',
                           tables=[accounding.tbl_revenue().to_html(classes='data', header=True),
                                   accounding.tbl_revenue_percent().to_html(classes='data', header=True)],
                           titles=titles_revenue)


titles_count_customer = ['Распределение количества клиентов по когортам в абсолютном выражении',
                           'Распределение количества клиентов в относительном выражении (к первому месяцу)']


@app.route('/cohort_count_customer')
def cohort_count_customer():
    return render_template('cohort_count_customer.html',
                           tables=[accounding.tbl_count_customer().to_html(classes='data', header=True),
                                   accounding.tbl_percent_count_customer().to_html(classes='data', header=True)],
                           titles=titles_count_customer)

titles_sales_metrics = ['Выручка, средний чек, количество покупок на одного пользователя',
                        'Уровень удержания и оттока клиентов']
@app.route('/sales_metrics')
def sales_metrics():
    return render_template('sales_metrics.html', tables=[accounding.tbl_sales_metrics().to_html(classes='data',header=True),
                                                         accounding.tbl_crr_churn_rate().to_html(classes='data',header=True)],
                           titles=titles_sales_metrics)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
