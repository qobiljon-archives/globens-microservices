-- region 1.user <-> vacancy relationship : zero to many
alter table "gb_user"
    add column "vacancy_id" integer references "gb_vacancy" ("id") default null;
-- endregion


-- region 2. vacancy <-> business page relationship : many to one
alter table "gb_business_page"
    add column "vacancy_id" integer references "gb_vacancy" ("id");
-- endregion


-- region 3. vacancy_application <-> user relationship : many to one
alter table "gb_vacancy_application"
    add column "user_id" integer references "gb_user" ("id");
-- endregion


-- region 4. vacancy_application <-> vacancy relationship : many to one
alter table "gb_vacancy_application"
    add column "vacancy_id" integer references "gb_user" ("id");
-- endregion


-- region 5. business page <-> product relationship : zero to many
alter table "gb_product"
    add column "business_page_id" integer references "gb_business_page" ("id");
-- endregion


-- region 6. purchase <-> product relationship : zero to one
alter table "gb_purchase"
    add column "product_id" integer references "gb_product" ("id");
-- endregion


-- region 7. purchase <-> user relationship : zero to one
alter table "gb_purchase"
    add column "buyer_id" integer references "gb_user" ("id");
-- endregion
