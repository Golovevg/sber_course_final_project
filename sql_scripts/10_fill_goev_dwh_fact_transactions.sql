delete from goev_dwh_fact_transactions;
insert into goev_dwh_fact_transactions
select *
from goev_stg_transactions
