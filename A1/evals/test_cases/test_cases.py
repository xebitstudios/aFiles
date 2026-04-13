"""
Test Cases — curated SAS snippets covering all major construct types.

Each test case is a dict with:
  - id:            Unique identifier
  - agent:         Which agent(s) this tests
  - category:      The SAS construct category
  - difficulty:    easy / medium / hard
  - sas_input:     The SAS source code
  - expected_types: (parser only) expected block types
  - description:   What this test case validates
"""

# ============================================================================
# DATA STEP TEST CASES
# ============================================================================

DATA_STEP_CASES = [
    {
        "id": "ds_001_simple_set",
        "agent": "data_step",
        "category": "data_step",
        "difficulty": "easy",
        "description": "Simple DATA step reading one dataset and creating a new variable",
        "sas_input": """\
data work.output;
    set work.input;
    total = price * quantity;
    if total > 100 then flag = 'HIGH';
    else flag = 'LOW';
run;
""",
    },
    {
        "id": "ds_002_merge",
        "agent": "data_step",
        "category": "data_step",
        "difficulty": "medium",
        "description": "DATA step with MERGE, BY, and IN= logic",
        "sas_input": """\
data work.combined;
    merge work.customers(in=a) work.orders(in=b);
    by customer_id;
    if a and b;
    order_status = 'MATCHED';
run;
""",
    },
    {
        "id": "ds_003_first_last",
        "agent": "data_step",
        "category": "data_step",
        "difficulty": "medium",
        "description": "First./Last. processing with BY group",
        "sas_input": """\
proc sort data=work.transactions;
    by account_id transaction_date;
run;

data work.account_summary;
    set work.transactions;
    by account_id;
    retain running_total 0;
    if first.account_id then running_total = 0;
    running_total = running_total + amount;
    if last.account_id then output;
run;
""",
    },
    {
        "id": "ds_004_array",
        "agent": "data_step",
        "category": "data_step",
        "difficulty": "hard",
        "description": "ARRAY processing with DO loop",
        "sas_input": """\
data work.normalized;
    set work.raw_scores;
    array scores{5} score1-score5;
    array normed{5} norm1-norm5;
    do i = 1 to 5;
        if scores{i} ne . then normed{i} = (scores{i} - 50) / 10;
        else normed{i} = .;
    end;
    drop i;
run;
""",
    },
    {
        "id": "ds_005_multiple_outputs",
        "agent": "data_step",
        "category": "data_step",
        "difficulty": "hard",
        "description": "Multiple output datasets with conditional routing",
        "sas_input": """\
data work.valid work.invalid work.review;
    set work.applications;
    if credit_score >= 700 and income >= 50000 then output work.valid;
    else if credit_score < 500 then output work.invalid;
    else output work.review;
run;
""",
    },
]

# ============================================================================
# PROC STEP TEST CASES
# ============================================================================

PROC_STEP_CASES = [
    {
        "id": "ps_001_sort",
        "agent": "proc_step",
        "category": "proc_step",
        "difficulty": "easy",
        "description": "PROC SORT with NODUPKEY",
        "sas_input": """\
proc sort data=work.employees out=work.unique_employees nodupkey;
    by department employee_id;
run;
""",
    },
    {
        "id": "ps_002_means",
        "agent": "proc_step",
        "category": "proc_step",
        "difficulty": "medium",
        "description": "PROC MEANS with CLASS, VAR, and OUTPUT",
        "sas_input": """\
proc means data=work.sales n mean std min max;
    class region product_category;
    var revenue quantity discount;
    output out=work.sales_summary
        mean=avg_revenue avg_quantity avg_discount
        sum=total_revenue total_quantity total_discount;
run;
""",
    },
    {
        "id": "ps_003_freq_crosstab",
        "agent": "proc_step",
        "category": "proc_step",
        "difficulty": "medium",
        "description": "PROC FREQ with TABLES cross-tabulation and chi-square",
        "sas_input": """\
proc freq data=work.survey;
    tables gender * satisfaction / chisq nocol norow;
    tables age_group * purchase_intent / chisq expected;
run;
""",
    },
    {
        "id": "ps_004_transpose",
        "agent": "proc_step",
        "category": "proc_step",
        "difficulty": "medium",
        "description": "PROC TRANSPOSE with ID and BY",
        "sas_input": """\
proc transpose data=work.long_data out=work.wide_data prefix=month_;
    by customer_id;
    id month;
    var sales_amount;
run;
""",
    },
    {
        "id": "ps_005_reg",
        "agent": "proc_step",
        "category": "proc_step",
        "difficulty": "hard",
        "description": "PROC REG with multiple models and output",
        "sas_input": """\
proc reg data=work.housing;
    model price = sqft bedrooms bathrooms lot_size / vif;
    model price = sqft bedrooms bathrooms lot_size neighborhood_score / vif stb;
    output out=work.reg_results p=predicted r=residual;
run;
quit;
""",
    },
]

# ============================================================================
# MACRO TEST CASES
# ============================================================================

MACRO_CASES = [
    {
        "id": "mc_001_simple_let",
        "agent": "macro",
        "category": "macro",
        "difficulty": "easy",
        "description": "Simple %LET variable assignment",
        "sas_input": """\
%let start_date = 01JAN2024;
%let end_date = 31DEC2024;
%let report_name = Annual Sales Report;
""",
    },
    {
        "id": "mc_002_simple_macro",
        "agent": "macro",
        "category": "macro",
        "difficulty": "medium",
        "description": "Macro definition with parameters and %IF/%THEN",
        "sas_input": """\
%macro filter_data(input_ds=, output_ds=, filter_var=, filter_val=);
    %if &filter_val ne %then %do;
        data &output_ds;
            set &input_ds;
            where &filter_var = "&filter_val";
        run;
    %end;
    %else %do;
        data &output_ds;
            set &input_ds;
        run;
    %end;
%mend filter_data;
""",
    },
    {
        "id": "mc_003_iterative_macro",
        "agent": "macro",
        "category": "macro",
        "difficulty": "hard",
        "description": "Macro with iterative %DO loop generating dynamic code",
        "sas_input": """\
%macro create_monthly_tables(year=2024, start_month=1, end_month=12);
    %do month = &start_month %to &end_month;
        %let month_str = %sysfunc(putn(&month, z2.));
        data work.sales_&year._&month_str;
            set work.all_sales;
            where year(sale_date) = &year and month(sale_date) = &month;
        run;
        %put NOTE: Created table for &year-&month_str;
    %end;
%mend create_monthly_tables;
""",
    },
    {
        "id": "mc_004_nested_macros",
        "agent": "macro",
        "category": "macro",
        "difficulty": "hard",
        "description": "Nested macro calls with %SYSFUNC and %EVAL",
        "sas_input": """\
%macro compute_age(dob, ref_date);
    %let age = %sysfunc(intck(year, "&dob"d, "&ref_date"d));
    %if %eval(&age < 0) %then %let age = 0;
    &age
%mend compute_age;

%macro categorize_customer(cust_ds=);
    data work.categorized;
        set &cust_ds;
        age = %compute_age(date_of_birth, today());
        if age < 25 then age_group = 'Young';
        else if age < 55 then age_group = 'Adult';
        else age_group = 'Senior';
    run;
%mend categorize_customer;
""",
    },
]

# ============================================================================
# SQL TEST CASES
# ============================================================================

SQL_CASES = [
    {
        "id": "sq_001_simple_select",
        "agent": "sql",
        "category": "sql",
        "difficulty": "easy",
        "description": "Simple SELECT with WHERE and ORDER BY",
        "sas_input": """\
proc sql;
    create table work.active_customers as
    select customer_id, name, email, signup_date
    from work.customers
    where status = 'ACTIVE'
    order by signup_date desc;
quit;
""",
    },
    {
        "id": "sq_002_join",
        "agent": "sql",
        "category": "sql",
        "difficulty": "medium",
        "description": "Multi-table JOIN with aggregation",
        "sas_input": """\
proc sql;
    create table work.customer_totals as
    select c.customer_id,
           c.name,
           count(o.order_id) as num_orders,
           sum(o.total_amount) as lifetime_value,
           calculated lifetime_value / calculated num_orders as avg_order_value
    from work.customers c
    left join work.orders o on c.customer_id = o.customer_id
    group by c.customer_id, c.name
    having calculated num_orders > 0
    order by lifetime_value desc;
quit;
""",
    },
    {
        "id": "sq_003_subquery_case",
        "agent": "sql",
        "category": "sql",
        "difficulty": "hard",
        "description": "Subquery, CASE WHEN, and UNION",
        "sas_input": """\
proc sql;
    create table work.segmented as
    select customer_id, name,
           case
               when lifetime_value >= (select avg(lifetime_value) * 2 from work.customer_totals)
                   then 'Platinum'
               when lifetime_value >= (select avg(lifetime_value) from work.customer_totals)
                   then 'Gold'
               else 'Standard'
           end as segment
    from work.customer_totals

    union all

    select customer_id, name, 'New' as segment
    from work.customers
    where customer_id not in (select customer_id from work.customer_totals);
quit;
""",
    },
    {
        "id": "sq_004_into_macrovar",
        "agent": "sql",
        "category": "sql",
        "difficulty": "medium",
        "description": "SELECT INTO macro variable",
        "sas_input": """\
proc sql noprint;
    select count(*) into :total_records
    from work.transactions;

    select distinct region into :region_list separated by ', '
    from work.transactions
    order by region;
quit;

%put Total records: &total_records;
%put Regions: &region_list;
""",
    },
]

# ============================================================================
# IO TEST CASES
# ============================================================================

IO_CASES = [
    {
        "id": "io_001_libname_file",
        "agent": "io",
        "category": "io",
        "difficulty": "easy",
        "description": "File-based LIBNAME",
        "sas_input": """\
libname mydata '/data/project/datasets';
""",
    },
    {
        "id": "io_002_libname_db",
        "agent": "io",
        "category": "io",
        "difficulty": "medium",
        "description": "Database LIBNAME with Oracle connection",
        "sas_input": """\
libname oradb oracle user=analyst password="{SAS002}XXXX"
    path="PRODDB" schema="SALES"
    access=readonly;
""",
    },
    {
        "id": "io_003_ods_multi",
        "agent": "io",
        "category": "io",
        "difficulty": "medium",
        "description": "Multiple ODS destinations",
        "sas_input": """\
ods html file='/reports/output.html' style=htmlblue;
ods pdf file='/reports/output.pdf';
ods excel file='/reports/output.xlsx' options(sheet_name='Summary');

proc print data=work.summary; run;

ods excel close;
ods pdf close;
ods html close;
""",
    },
    {
        "id": "io_004_email",
        "agent": "io",
        "category": "io",
        "difficulty": "hard",
        "description": "Email with attachment via FILENAME EMAIL",
        "sas_input": """\
filename mymail email
    to="manager@company.com"
    cc="team@company.com"
    from="sas_reports@company.com"
    subject="Monthly Report - &sysdate"
    attach="/reports/monthly_report.pdf"
    content_type="text/html";

data _null_;
    file mymail;
    put '<html><body>';
    put '<h2>Monthly Report</h2>';
    put '<p>Please find the attached monthly report.</p>';
    put '</body></html>';
run;
""",
    },
    {
        "id": "io_005_include",
        "agent": "io",
        "category": "io",
        "difficulty": "easy",
        "description": "%INCLUDE statement",
        "sas_input": """\
%include '/sas/programs/common/macros.sas';
%include '/sas/programs/common/formats.sas';
""",
    },
]

# ============================================================================
# CONFIG TEST CASES
# ============================================================================

CONFIG_CASES = [
    {
        "id": "cf_001_options",
        "agent": "config",
        "category": "config",
        "difficulty": "easy",
        "description": "Common SAS OPTIONS",
        "sas_input": """\
options mprint mlogic symbolgen obs=1000 nocenter
        linesize=150 pagesize=60 nofmterr;
""",
    },
    {
        "id": "cf_002_proc_format",
        "agent": "config",
        "category": "config",
        "difficulty": "medium",
        "description": "PROC FORMAT with VALUE and range-based labels",
        "sas_input": """\
proc format;
    value agefmt
        low -< 18 = 'Minor'
        18 -< 25  = 'Young Adult'
        25 -< 45  = 'Adult'
        45 -< 65  = 'Middle Age'
        65 - high  = 'Senior';
    value $statusfmt
        'A' = 'Active'
        'I' = 'Inactive'
        'P' = 'Pending'
        other = 'Unknown';
run;
""",
    },
    {
        "id": "cf_003_titles",
        "agent": "config",
        "category": "config",
        "difficulty": "easy",
        "description": "TITLE and FOOTNOTE statements",
        "sas_input": """\
title 'Quarterly Sales Analysis';
title2 'Period: Q1 2024';
footnote 'Source: Internal Sales Database';
footnote2 'Confidential - Do Not Distribute';
""",
    },
]

# ============================================================================
# PARSER TEST CASES
# ============================================================================

PARSER_CASES = [
    {
        "id": "pa_001_mixed_simple",
        "agent": "parser",
        "category": "parser",
        "difficulty": "easy",
        "description": "Simple mixed program with known block types",
        "sas_input": """\
libname mylib '/data/myproject';

%let report_year = 2024;

data work.filtered;
    set mylib.raw_data;
    where year = &report_year;
run;

proc sort data=work.filtered;
    by region;
run;

proc means data=work.filtered n mean sum;
    class region;
    var revenue;
run;
""",
        "expected_types": ["libname", "assignment", "data_step", "proc_step", "proc_step"],
        "expected_count": 5,
    },
    {
        "id": "pa_002_complex_mixed",
        "agent": "parser",
        "category": "parser",
        "difficulty": "hard",
        "description": "Complex program with macros, SQL, ODS, and DATA steps",
        "sas_input": """\
options mprint mlogic;

%global report_date;
%let report_date = %sysfunc(today(), date9.);

%macro gen_report(region=);
    proc sql;
        create table work.region_data as
        select * from work.all_data
        where region = "&region";
    quit;

    proc means data=work.region_data noprint;
        var sales;
        output out=work.summary mean=avg_sales sum=total_sales;
    run;
%mend gen_report;

ods pdf file="/reports/report_&report_date..pdf";

%gen_report(region=EAST);
%gen_report(region=WEST);

ods pdf close;
""",
        "expected_types": [
            "options", "global", "assignment", "macro_definition",
            "ods", "macro_call", "macro_call", "ods",
        ],
        "expected_count": 8,
    },
]

# ============================================================================
# END-TO-END TEST CASES — full SAS programs
# ============================================================================

E2E_CASES = [
    {
        "id": "e2e_001_basic_etl",
        "category": "end_to_end",
        "difficulty": "medium",
        "description": "Basic ETL: read, transform, aggregate, export",
        "sas_input": """\
libname raw '/data/raw';
libname out '/data/processed';

options mprint nocenter;

%let start_date = 01JAN2024;
%let end_date = 31MAR2024;

/* Read and filter raw transactions */
data work.transactions;
    set raw.all_transactions;
    where transaction_date between "&start_date"d and "&end_date"d;
    amount_usd = amount * exchange_rate;
    if amount_usd > 0;
run;

/* Remove duplicates */
proc sort data=work.transactions out=work.transactions_clean nodupkey;
    by transaction_id;
run;

/* Summarise by category */
proc means data=work.transactions_clean noprint;
    class category;
    var amount_usd;
    output out=work.category_summary
        n=num_transactions
        mean=avg_amount
        sum=total_amount;
run;

/* Export */
proc export data=work.category_summary
    outfile='/data/processed/category_summary.csv'
    dbms=csv replace;
run;

title 'Transaction Summary Q1 2024';
proc print data=work.category_summary noobs; run;
""",
    },
    {
        "id": "e2e_002_macro_driven_report",
        "category": "end_to_end",
        "difficulty": "hard",
        "description": "Macro-driven reporting with ODS, SQL, and formatting",
        "sas_input": """\
options mprint mlogic symbolgen;

%global report_month report_year;
%let report_month = 3;
%let report_year = 2024;

proc format;
    value revfmt
        low -< 1000 = 'Low'
        1000 -< 10000 = 'Medium'
        10000 - high = 'High';
    value $regionfmt
        'N' = 'North'
        'S' = 'South'
        'E' = 'East'
        'W' = 'West';
run;

%macro monthly_report(region=);
    proc sql;
        create table work.region_&region as
        select customer_id,
               customer_name,
               sum(revenue) as total_revenue,
               count(*) as num_orders,
               case
                   when calculated total_revenue > 10000 then 'VIP'
                   when calculated total_revenue > 1000 then 'Regular'
                   else 'Occasional'
               end as customer_tier
        from work.all_orders
        where region = "&region"
          and month(order_date) = &report_month
          and year(order_date) = &report_year
        group by customer_id, customer_name
        order by total_revenue desc;
    quit;

    title "Monthly Report: Region &region - &report_month/&report_year";
    proc print data=work.region_&region(obs=20) noobs;
        format total_revenue revfmt.;
    run;
%mend monthly_report;

ods pdf file="/reports/monthly_&report_year._&report_month..pdf";

%monthly_report(region=N);
%monthly_report(region=S);
%monthly_report(region=E);
%monthly_report(region=W);

ods pdf close;
""",
    },
]

# ============================================================================
# ALL CASES combined for easy iteration
# ============================================================================

ALL_CASES = (
    DATA_STEP_CASES
    + PROC_STEP_CASES
    + MACRO_CASES
    + SQL_CASES
    + IO_CASES
    + CONFIG_CASES
)

ALL_PARSER_CASES = PARSER_CASES
ALL_E2E_CASES = E2E_CASES
