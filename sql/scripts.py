sales_group = """  
with sales_result as (select s.invoiceno,
                             strftime("%Y-%m-%d", julianday(s.invoicedate, 'start of month')) as month_sale,
                             s.customerid,
                             s.amount,
                             c.month_cohort
                    from sales s left join (select f.customerid,
                                                   strftime("%Y-%m-%d", julianday(min(f.invoicedate), 'start of month')) as month_cohort
                                            from sales f
                                            group by f.customerid) c
                                 on s.customerid = c.customerid),

sales_group as (select r.month_cohort,
                       r.month_sale,
                       sum(amount) as revenue,
                       count(distinct r.customerid) as count_customer,
                       count(distinct r.invoiceno) as count_invoice
                from sales_result r
                group by r.month_cohort, r.month_sale
                order by r.month_cohort, r.month_sale),

sales_group_result as (select gr.*,
                              n.revenue as first_revenue,
                              n.count_customer as first_count_customer
                        from sales_group gr left join (select g.month_cohort,
                                                              g.month_sale,
                                                              g.revenue,
                                                              g.count_customer,
                                                              row_number() over(partition by g.month_cohort order by g.month_cohort, g.month_sale) as row_n
                                                        from sales_group g) n
                                            on gr.month_cohort = n.month_cohort and n.row_n = 1)

select substr(r.month_cohort,1,7) as month_cohort,
       substr(r.month_sale,1,7) as month_sale,
       round(cast(r.revenue as real)/1000, 1) as revenue,
       r.count_customer,
       r.count_invoice,
       round(cast(r.revenue as real) / cast(r.first_revenue as real), 1) as percent_revenue,
       round(cast(r.count_customer as real) / cast(r.first_count_customer as real), 1) as percent_count_customer
from sales_group_result r """

sales_metrics = """
with sales_group as (select
                           strftime('%Y-%m-%d',julianday(s.invoicedate,'start of month')) as month_sale,
                           count(distinct s.invoiceno) as count_invoice,
                           count(distinct s.customerid) as count_customer,
                           sum (s.amount) as revenue
                    from sales s
                     group by strftime('%Y-%m-%d',julianday(s.invoicedate,'start of month')))

select gr.*,
       round(cast(gr.revenue as real)/cast(gr.count_invoice as real),2) as avg_receipt,
       round(cast(gr.count_invoice as real)/cast(gr.count_customer as real),0) as purchase_frequency,
       round(cast(gr.revenue as real)/cast(gr.count_customer as real),0) as arpu
from sales_group gr """

crr_churn_rate = """ 
with sales_result as (select s.invoiceno,
                             strftime("%Y-%m-%d", julianday(s.invoicedate, 'start of month')) as month_sale,
                             s.customerid,
                             s.amount,
                             c.month_cohort
                       from sales s left join (select f.customerid,
                                                      strftime("%Y-%m-%d", julianday(min(f.invoicedate), 'start of month')) as month_cohort
                                                from sales f
                                                group by f.customerid) c
                                    on s.customerid = c.customerid),

count_customer_group as (select r.month_cohort,
                                r.month_sale,
                                count(distinct r.customerid) as count_customer
                        from sales_result r
                        group by r.month_cohort, r.month_sale
                        order by  r.month_sale,r.month_cohort),
 
count_customer_group_result as (select distinct gr.month_sale,
                                      last_value(gr.count_customer) over (partition by gr.month_sale order by gr.month_sale) as count_customer_new, 
                                      sum(gr.count_customer) over (partition by gr.month_sale) as count_customer_end_month
                                 
                          from count_customer_group gr),

count_customer_result as (select r.month_sale,
								lag(r.count_customer_end_month,1,0) over (order by r.month_sale) as count_customer_start_month,
								r.count_customer_new,
								r.count_customer_end_month
						from count_customer_group_result r)
select r.*,
      coalesce(round(
                     cast((r.count_customer_end_month - r.count_customer_new) as real)
                     /
                   cast(r.count_customer_start_month as real),
                   2),
            "-") as crr,
            
      coalesce(round(
                  cast(r.count_customer_start_month -  (r.count_customer_end_month-r.count_customer_new) as real)
                  /
                   cast(r.count_customer_start_month as real),
                 2),
          "-") as churn_rate       
from count_customer_result r"""