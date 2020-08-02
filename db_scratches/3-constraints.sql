-- region 1. unique vacancy application entry : one user + one vacancy = one application
alter table "vacancy_application"
    add unique ("vacancy_id", "user_id");
-- endregion


-- region 2. unique purchase log entry : one user + one product = one purchase
alter table "purchase"
    add unique ("buyer_id", "product_id");
-- endregion
